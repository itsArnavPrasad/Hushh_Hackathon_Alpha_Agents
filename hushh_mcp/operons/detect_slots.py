# hushh_mcp/operons/detect_slots.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.operons.mcp_adapter import get_freebusy
from hushh_mcp.agents.calendar_agent.state.memory import CalendarAgentMemory
from hushh_mcp.agents.calendar_agent.state.gemini_llm import gemini_chat
from hushh_mcp.agents.calendar_agent.state.prompts import SUMMARIZE_CALENDAR_PROMPT

def detect_available_slots(user_id, consent_token, calendar_ids=None, time_min=None, time_max=None, explain=False):
    """
    Calls the MCP server's get-freebusy tool to find free/busy slots.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.AGENT_GCAL_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    free_busy = get_freebusy(
        user_id=user_id,
        calendar_ids=calendar_ids or [],
        time_min=time_min,
        time_max=time_max
    )
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_free_busy", free_busy)

    result = {"free_busy": free_busy}
    if explain:
        prompt = SUMMARIZE_CALENDAR_PROMPT.format(events=free_busy)
        explanation = gemini_chat(prompt)
        result["explanation"] = explanation
    return result