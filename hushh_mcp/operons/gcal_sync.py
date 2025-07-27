from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from .mcp_adapter import (
    list_events,
    create_event,
    get_freebusy,
    list_calendars,
    list_colors,
)
from hushh_mcp.agents.calendar_agent.state.memory import CalendarAgentMemory

def sync_with_gcal(user_id, consent_token, time_range=None, calendar_id=None):
    """
    Fetch events from Google Calendar via MCP.
    Requires gcal.read scope.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    time_min, time_max = (time_range if time_range else (None, None))
    events = list_events(
        user_id=user_id,
        consent_token=consent_token,
        calendar_id=calendar_id,
        time_min=time_min,
        time_max=time_max,
    )
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_synced_events", events)
    return {"events": events}

def add_event_to_gcal(user_id, consent_token, event_data, calendar_id=None):
    """
    Add an event to Google Calendar via MCP.
    Requires gcal.write scope.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_WRITE)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    result = create_event(
        user_id=user_id,
        consent_token=consent_token,
        event_data=event_data,
        calendar_id=calendar_id,
    )
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_created_event", result)
    return {"status": "created", "event": result}

def get_freebusy(user_id, consent_token, time_range, calendar_ids=None):
    """
    Get free/busy information from Google Calendar via MCP.
    Requires gcal.read scope.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    time_min, time_max = time_range
    result = get_freebusy(
        user_id=user_id,
        consent_token=consent_token,
        time_min=time_min,
        time_max=time_max,
        calendar_ids=calendar_ids,
    )
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_freebusy_result", result)
    return {"freebusy": result}

def list_calendars(user_id, consent_token):
    """
    List all available calendars for the user via MCP.
    Requires gcal.read scope.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    result = list_calendars(user_id, consent_token)
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_listed_calendars", result)
    return {"calendars": result}

def list_colors(user_id, consent_token):
    """
    List available event colors via MCP.
    Requires gcal.read scope.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.GCAL_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    result = list_colors(user_id, consent_token)
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_listed_colors", result)
    return {"colors": result}