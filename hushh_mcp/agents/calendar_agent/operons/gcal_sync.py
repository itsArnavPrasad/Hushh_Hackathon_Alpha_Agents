# hushh_mcp/agents/calendar_agent/operons/gcal_sync.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.external_mcp.google_calendar.mcp_adapter import fetch_calendar_events, create_event
from hushh_mcp.agents.calendar_agent.state.memory import CalendarAgentMemory

def sync_with_gcal(user_id, consent_token, time_range):
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    events = fetch_calendar_events(user_id, *time_range)
    # Save events to memory for context
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_synced_events", events)
    return {"events": events}

def add_event_to_gcal(user_id, consent_token, event_data):
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_WRITE)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    result = create_event(user_id, event_data)
    # Optionally update memory
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_created_event", result)
    return {"status": "created", "event": result}