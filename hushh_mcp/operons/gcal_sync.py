# hushh_mcp/operons/gcal_sync.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.external_mcp.google_calendar.mcp_adapter import list_events, create_event
from hushh_mcp.agents.calendar_agent.state.memory import CalendarAgentMemory

def sync_with_gcal(user_id, consent_token, calendar_id, time_min=None, time_max=None):
    """
    Calls the MCP server's list-events tool to fetch events.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    events = list_events(
        user_id=user_id,
        calendar_id=calendar_id,
        time_min=time_min,
        time_max=time_max
    )
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_synced_events", events)
    return {"events": events}

def add_event_to_gcal(user_id, consent_token, calendar_id, event_data):
    """
    Calls the MCP server's create-event tool to add an event.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_WRITE)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    result = create_event(
        user_id=user_id,
        calendar_id=calendar_id,
        event_data=event_data
    )
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_created_event", result)
    return {"status": "created", "event": result}