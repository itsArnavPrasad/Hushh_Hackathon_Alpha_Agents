# hushh_mcp/agents/calendar_agent/operons/reschedule_task.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
# from hushh_mcp.state.prompts import RESCHEDULE_PROMPT

def reschedule_task(user_id, consent_token, event_id, new_time, reason=None):
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.CALENDAR_WRITE)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    # Call GCal MCP to update event (pseudo-code)
    from hushh_mcp.external_mcp.google_calender.mcp_adapter import update_event     
    result = update_event(user_id, event_id, {"start": new_time, "reason": reason})
    return {"status": "rescheduled", "result": result}