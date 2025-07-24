# hushh_mcp/agents/calendar_agent/index.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.vault.encrypt import decrypt_data
from hushh_mcp.trust.link import verify_trust_link
from .operons.detect_slots import detect_available_slots
from .operons.suggest_schedule import suggest_optimal_schedule
from .operons.reschedule_task import reschedule_task
from .operons.gcal_sync import sync_with_gcal, add_event_to_gcal

# LangChain & LangGraph imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
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
        state["user_id"], state["consent_token"], state.get("slots"), state.get("user_preferences", {})
    )
    state["suggestion"] = suggestion
    return state

def node_reschedule_task(state: CalendarAgentState):
    result = reschedule_task(
        state["user_id"], state["consent_token"], **state.get("reschedule_args", {})
    )
    state["reschedule_result"] = result
    return state

def node_sync_gcal(state: CalendarAgentState):
    events = sync_with_gcal(
        state["user_id"], state["consent_token"], state.get("sync_time_range", ())
    )
    state["gcal_events"] = events
    return state

def node_add_event_to_gcal(state: CalendarAgentState):
    result = add_event_to_gcal(
        state["user_id"], state["consent_token"], state.get("event_data", {})
    )
    state["add_event_result"] = result
    return state

# --- LangGraph State Machine Construction ---

def build_calendar_agent_graph():
    graph = StateGraph(CalendarAgentState)
    # Add nodes
    graph.add_node("DetectSlots", node_detect_slots)
    graph.add_node("SuggestSchedule", node_suggest_schedule)
    graph.add_node("RescheduleTask", node_reschedule_task)
    graph.add_node("SyncGCal", node_sync_gcal)
    graph.add_node("AddEventToGCal", node_add_event_to_gcal)
    # Define transitions (example: intent-based)
    graph.add_edge("DetectSlots", "SuggestSchedule", condition=lambda s: s["intent"] == "suggest_schedule")
    graph.add_edge("SuggestSchedule", "AddEventToGCal", condition=lambda s: s.get("suggestion") is not None)
    graph.add_edge("RescheduleTask", END)
    graph.add_edge("SyncGCal", END)
    graph.add_edge("AddEventToGCal", END)
    # Entry points
    graph.set_entry_point("DetectSlots")
    return graph.compile()

# --- Main Entrypoint ---

def run_agent(user_id, consent_token, intent, **kwargs):
    # Consent validation (bacteria: always explicit)
    for scope in [
        ConsentScope.CALENDAR_READ,
        ConsentScope.CALENDAR_WRITE,
        ConsentScope.GCAL_READ,
        ConsentScope.GCAL_WRITE
    ]:
        valid, reason, parsed = validate_token(consent_token, expected_scope=scope)
        if not valid or parsed.user_id != user_id:
            raise PermissionError(f"❌ Consent validation failed: {reason}")

    # Build initial state
    state = CalendarAgentState(
        user_id=user_id,
        consent_token=consent_token,
        intent=intent,
        **kwargs
    )
    # Run LangGraph
    graph = build_calendar_agent_graph()
    result = graph.invoke(state)
    return result

# CLI/test usage
if __name__ == "__main__":
    import sys, json
    user_id = sys.argv[1]
    token = sys.argv[2]
    intent = sys.argv[3]
    # Example: python index.py user_123 <token> suggest_schedule '{"detect_slots_args": {"time_min": "...", "time_max": "..."}}'
    kwargs = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    output = run_agent(user_id, token, intent, **kwargs)
    print(json.dumps(output, indent=2))