# hushh_mcp/agents/calendar_agent/operons/detect_slots.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.vault.encrypt import decrypt_data
from hushh_mcp.external_mcp.google_calendar.mcp_adapter import get_free_busy
from hushh_mcp.agents.calendar_agent.state.memory import CalendarAgentMemory
from hushh_mcp.agents.calendar_agent.state.gemini_llm import gemini_chat
from hushh_mcp.agents.calendar_agent.state.prompts import SUMMARIZE_CALENDAR_PROMPT

def detect_available_slots(user_id, consent_token, time_min, time_max, explain=False):
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.CALENDAR_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    free_busy = get_free_busy(user_id, time_min, time_max)
    # Save to memory (optional, for context)
    memory = CalendarAgentMemory(user_id)
    memory.save_context("last_free_busy", free_busy)

    result = {"free_busy": free_busy}
    if explain:
        prompt = SUMMARIZE_CALENDAR_PROMPT.format(events=free_busy)
        explanation = gemini_chat(prompt)
        result["explanation"] = explanation
    return result