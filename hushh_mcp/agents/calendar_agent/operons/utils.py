# hushh_mcp/agents/calendar_agent/operons/utils.py

from hushh_mcp.agents.calendar_agent.state.gemini_llm import gemini_chat

def parse_time_range(natural_language_str):
    # Use Gemini to parse natural language time ranges if needed
    prompt = f"Parse this time range into ISO 8601 start and end datetimes: '{natural_language_str}'. Respond as JSON: {{'start': '...', 'end': '...'}}"
    response = gemini_chat(prompt)
    try:
        import json
        parsed = json.loads(response)
        return (parsed["start"], parsed["end"])
    except Exception:
        # Fallback to a static example
        return ("2025-07-25T15:00:00Z", "2025-07-25T17:00:00Z")