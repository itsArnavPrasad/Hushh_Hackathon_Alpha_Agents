# hushh_mcp/operons/reschedule_task.py

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.calendar_agent.state.prompts import RESCHEDULE_TASK_PROMPT
from hushh_mcp.agents.calendar_agent.state.gemini_llm import gemini_chat
from hushh_mcp.operons.mcp_adapter import update_event

def reschedule_task(user_id, consent_token, calendar_id, event_id, new_time, reason=None, event_details=None, user_intent=None, conflicts=None):
    """
    Uses Gemini LLM for reasoning, then calls MCP update-event tool to reschedule.
    """
    valid, reason_msg, parsed = validate_token(consent_token, expected_scope=ConsentScope.CALENDAR_WRITE)
    if not valid or parsed.user_id != user_id:
        raise PermissionError(f"Consent validation failed: {reason_msg}")

    prompt = RESCHEDULE_TASK_PROMPT.format(
        event_details=event_details or "N/A",
        user_intent=user_intent or "N/A",
        conflicts=conflicts or "None"
    )
    import json
    suggestion_text = gemini_chat(prompt)
    try:
        suggestion = json.loads(suggestion_text)
    except Exception:
        suggestion = {"new_time": None, "reason": suggestion_text}

    update_result = None
    if suggestion.get("new_time"):
        update_result = update_event(
            user_id=user_id,
            calendar_id=calendar_id,
            event_id=event_id,
            new_time=suggestion["new_time"],
            reason=reason
        )
    return {"status": "rescheduled", "suggestion": suggestion, "result": update_result}