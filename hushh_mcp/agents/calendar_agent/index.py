from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.trust.link import verify_trust_link
from hushh_mcp.operons.detect_slots import detect_available_slots
from hushh_mcp.operons.suggest_schedule import suggest_optimal_schedule
from hushh_mcp.operons.reschedule_task import reschedule_task
from hushh_mcp.operons.gcal_sync import (
    sync_with_gcal,
    add_event_to_gcal,
    get_freebusy,
    list_calendars,
    list_colors,
)
from langgraph.graph import StateGraph, END

# --- Agent State Definition ---
class CalendarAgentState(dict):
    """
    State is a dict with:
        - user_id
        - consent_token
        - intent
        - context (optional)
        - result (optional)
        - other operon-specific keys
    """
    pass

# --- LangGraph Node Functions ---

def node_detect_slots(state: CalendarAgentState):
    slots = detect_available_slots(
        state["user_id"], state["consent_token"], **state.get("detect_slots_args", {})
    )
    state["slots"] = slots
    return state

def node_suggest_schedule(state: CalendarAgentState):
    suggestion = suggest_optimal_schedule(
        state["user_id"], state["consent_token"],
        state.get("slots"), state.get("user_preferences", {})
    )
    state["suggestion"] = suggestion
    return state

def node_reschedule_task(state: CalendarAgentState):
    result = reschedule_task(
        state["user_id"], state["consent_token"],
        **state.get("reschedule_args", {})
    )
    state["reschedule_result"] = result
    return state

def node_sync_gcal(state: CalendarAgentState):
    events = sync_with_gcal(
        state["user_id"], state["consent_token"],
        state.get("sync_time_range", ()),
        state.get("calendar_id"),
    )
    state["gcal_events"] = events
    return state

def node_add_event_to_gcal(state: CalendarAgentState):
    result = add_event_to_gcal(
        state["user_id"], state["consent_token"],
        state.get("event_data", {}),
        state.get("calendar_id"),
    )
    state["add_event_result"] = result
    return state

def node_get_freebusy(state: CalendarAgentState):
    result = get_freebusy(
        state["user_id"], state["consent_token"],
        state.get("freebusy_time_range"),
        state.get("calendar_ids"),
    )
    state["freebusy_result"] = result
    return state

def node_list_calendars(state: CalendarAgentState):
    result = list_calendars(
        state["user_id"], state["consent_token"]
    )
    state["calendars"] = result
    return state

def node_list_colors(state: CalendarAgentState):
    result = list_colors(
        state["user_id"], state["consent_token"]
    )
    state["colors"] = result
    return state

# --- LangGraph State Machine Construction ---
def build_calendar_agent_graph():
    graph = StateGraph(CalendarAgentState)

    # Add all nodes
    graph.add_node("DetectSlots", node_detect_slots)
    graph.add_node("SuggestSchedule", node_suggest_schedule)
    graph.add_node("RescheduleTask", node_reschedule_task)
    graph.add_node("SyncGCal", node_sync_gcal)
    graph.add_node("AddEventToGCal", node_add_event_to_gcal)
    graph.add_node("GetFreeBusy", node_get_freebusy)
    graph.add_node("ListCalendars", node_list_calendars)
    graph.add_node("ListColors", node_list_colors)

    # Use conditional routing
    def intent_router(state: CalendarAgentState):
        intent = state.get("intent")
        if intent == "suggest_schedule":
            return "SuggestSchedule"
        elif intent == "reschedule_task":
            return "RescheduleTask"
        elif intent == "sync_gcal":
            return "SyncGCal"
        elif intent == "add_event_to_gcal":
            return "AddEventToGCal"
        elif intent == "get_freebusy":
            return "GetFreeBusy"
        elif intent == "list_calendars":
            return "ListCalendars"
        elif intent == "list_colors":
            return "ListColors"
        else:
            raise ValueError(f"Unknown intent: {intent}")

    # Define transition from DetectSlots based on intent
    graph.add_conditional_edges("DetectSlots", intent_router)

    # Add direct edges for follow-up logic
    graph.add_edge("SuggestSchedule", "AddEventToGCal")
    graph.add_edge("AddEventToGCal", END)
    graph.add_edge("RescheduleTask", END)
    graph.add_edge("SyncGCal", END)
    graph.add_edge("GetFreeBusy", END)
    graph.add_edge("ListCalendars", END)
    graph.add_edge("ListColors", END)

    # Entry point
    graph.set_entry_point("DetectSlots")

    return graph.compile()

# --- Main Entrypoint ---
def run_agent(user_id, consent_token, intent, **kwargs):
    # Consent validation
    valid, reason, parsed = validate_token(consent_token)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"❌ Consent validation failed: {reason}")

    # Build initial state
    state = {
        "user_id": user_id,
        "consent_token": consent_token,
        "intent": intent,
        **kwargs
    }

    # Run LangGraph
    graph = build_calendar_agent_graph()
    result = graph.invoke(state)
    return result

# --- CLI/Test usage ---
if __name__ == "__main__":
    import sys, json
    user_id = sys.argv[1]
    token = sys.argv[2]
    intent = sys.argv[3]
    kwargs = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    output = run_agent(user_id, token, intent, **kwargs)
    print(json.dumps(output, indent=2))