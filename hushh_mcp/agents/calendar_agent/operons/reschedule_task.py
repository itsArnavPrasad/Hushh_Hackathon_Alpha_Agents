# hushh_mcp/agents/calendar_agent/operons/reschedule_task.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.calendar_agent.state.prompts import RESCHEDULE_TASK_PROMPT
from hushh_mcp.agents.calendar_agent.state.gemini_llm import gemini_chat
from hushh_mcp.external_mcp.google_calendar.mcp_adapter import update_event

def reschedule_task(user_id, consent_token, event_id, new_time, reason=None, event_details=None, user_intent=None, conflicts=None):
    valid, reason_msg, parsed = validate_token(consent_token, expected_scope=ConsentScope.CALENDAR_WRITE)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason_msg}")

    # Use Gemini to suggest a new time or explain conflicts
    prompt = RESCHEDULE_TASK_PROMPT.format(
        event_details=event_details or "N/A",
        user_intent=user_intent or "N/A",
        conflicts=conflicts or "None"
    )
    suggestion_text = gemini_chat(prompt)
    import json
    try:
        suggestion = json.loads(suggestion_text)
    except Exception:
        suggestion = {"new_time": None, "reason": suggestion_text}

    # If a new time is suggested, update the event
    update_result = None
    if suggestion.get("new_time"):
        update_result = update_event(user_id, event_id, {"start": suggestion["new_time"], "reason": reason})
    return {"status": "rescheduled", "suggestion": suggestion, "result": update_result}