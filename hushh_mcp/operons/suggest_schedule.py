# hushh_mcp/operons/suggest_schedule.py
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.calendar_agent.state.prompts import SUGGEST_SCHEDULE_PROMPT
from hushh_mcp.agents.calendar_agent.state.gemini_llm import gemini_chat
import json

def suggest_optimal_schedule(user_id, consent_token, free_busy, user_preferences):
    """
    Uses LLM to suggest a schedule based on free/busy slots (from get-freebusy) and user preferences.
    """
    valid, reason, parsed = validate_token(consent_token, expected_scope=ConsentScope.CALENDAR_READ)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason}")

    prompt = SUGGEST_SCHEDULE_PROMPT.format(
        task_description=user_preferences.get("task", "No task provided"),
        free_slots=free_busy,
        preferences=user_preferences
    )
    suggestion_text = gemini_chat(prompt)
    try:
        suggestion = json.loads(suggestion_text)
    except Exception:
        suggestion = {"suggested_time": None, "reason": suggestion_text}
    return suggestion