# hushh_mcp/agents/calendar_agent/operons/detect_slots.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.vault.encrypt import decrypt_data
from hushh_mcp.external_mcp.google_calender.mcp_adapter import get_free_busy 

def detect_available_slots(user_id, consent_token, time_min, time_max):
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.CALENDAR_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    # Fetch free/busy info from Google Calendar MCP (encrypted)
    free_busy = get_free_busy(user_id, time_min, time_max)
    # Optionally decrypt or process as needed
    return {"free_busy": free_busy}