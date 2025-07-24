# hushh_mcp/agents/calendar_agent/index.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.trust.link import verify_trust_link
from .operons.detect_slots import detect_available_slots
from .operons.suggest_schedule import suggest_optimal_schedule
from .operons.reschedule_task import reschedule_task
from .operons.gcal_sync import sync_with_gcal, add_event_to_gcal

# LangGraph imports
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

# --- LangGraph Node Functions (Bacteria: one function = one responsibility) ---

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
        state.get("sync_time_range", ())
    )
    state["gcal_events"] = events
    return state

def node_add_event_to_gcal(state: CalendarAgentState):
    result = add_event_to_gcal(
        state["user_id"], state["consent_token"],
        state.get("event_data", {})
    )
    state["add_event_result"] = result
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

    # Use conditional routing instead of old-style condition=
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
        else:
            raise ValueError(f"Unknown intent: {intent}")

    # Define transition from DetectSlots based on intent
    graph.add_conditional_edges("DetectSlots", intent_router)

    # Add direct edges for follow-up logic
    graph.add_edge("SuggestSchedule", "AddEventToGCal")
    graph.add_edge("AddEventToGCal", END)
    graph.add_edge("RescheduleTask", END)
    graph.add_edge("SyncGCal", END)

    # Entry point
    graph.set_entry_point("DetectSlots")

    return graph.compile()

# --- Main Entrypoint ---
def run_agent(user_id, consent_token, intent, **kwargs):
    # Consent validation (bacteria: always explicit)
    valid, reason, parsed = validate_token(consent_token)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"❌ Consent validation failed: {reason}")

    required_scopes = [
        ConsentScope.CALENDAR_READ.value,
        ConsentScope.CALENDAR_WRITE.value,
        ConsentScope.GCAL_READ.value,
        ConsentScope.GCAL_WRITE.value
    ]

    # Additional scope check (optional)
    # Can add scope check logic here if needed using parsed.scopes

    # Build initial state
    state = {
        "user_id":user_id,
        "consent_token":consent_token,
        "intent":intent,
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