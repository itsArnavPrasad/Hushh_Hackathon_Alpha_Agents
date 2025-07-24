# hushh_mcp/agents/calendar_agent/state/prompts.py

# Prompt for suggesting optimal schedule
SUGGEST_SCHEDULE_PROMPT = """
You are ChronoAgent, a privacy-preserving AI calendar assistant.
Given the user's free/busy slots and their preferences, suggest the best time for the following task:

Task: {task_description}
Available Slots: {free_slots}
User Preferences: {preferences}

Respond with a JSON object: {{"suggested_time": "...", "reason": "..."}}
"""

# Prompt for rescheduling a task
RESCHEDULE_TASK_PROMPT = """
You are ChronoAgent. The user wants to reschedule the following event:

Event: {event_details}
Requested Change: {user_intent}
Current Conflicts: {conflicts}

Suggest a new time or explain why rescheduling is not possible.
Respond with a JSON object: {{"new_time": "...", "reason": "..."}}
"""

# Prompt for summarizing the user's calendar
SUMMARIZE_CALENDAR_PROMPT = """
You are ChronoAgent. Summarize the user's upcoming week based on these events:

Events: {events}

Highlight any deadlines, busy days, or free periods.
"""

# Add more prompts as needed for other operons or conversational flows.