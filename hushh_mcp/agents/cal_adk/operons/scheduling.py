from typing import Dict, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.vault import store_consent
from google.adk.tools import Tool
from chrono_agent.tools.fetch_calendar_state import fetch_calendar_state
from chrono_agent.tools.schedule_event import schedule_event
from chrono_agent.tools.notify_user import notify_user

class SchedulingOperon:
    """Operon for handling calendar event creation, updates, and rescheduling."""
    
    required_scopes = [ConsentScope.VAULT_READ_CALENDAR, ConsentScope.VAULT_WRITE_CALENDAR]
    
    def __init__(self):
        self.tools = [
            Tool(name="fetch_calendar_state", function=fetch_calendar_state),
            Tool(name="schedule_event", function=schedule_event),
            Tool(name="notify_user", function=notify_user)
        ]
    
    def validate_consent(self, token: str, user_id: str) -> bool:
        """Validate consent token for required scopes."""
        for scope in self.required_scopes:
            valid, reason, parsed = validate_token(token, expected_scope=scope)
            if not valid:
                store_consent(f"/vault/consent_failure_{scope}_{user_id}", {"reason": reason})
                raise PermissionError(f"Invalid token for {scope}: {reason}")
            if parsed.user_id != user_id:
                store_consent(f"/vault/consent_user_mismatch_{scope}_{user_id}", {"reason": "Token user mismatch"})
                raise PermissionError("Token user mismatch")
        return True
    
    def process(self, user_id: str, token: str, request: Dict) -> Dict:
        """Process a scheduling request."""
        # Validate consent
        self.validate_consent(token, user_id)
        
        # Fetch calendar state
        calendar_state = fetch_calendar_state()
        if not calendar_state.get("available_slots"):
            store_consent(f"/vault/scheduling_failure_{user_id}", {"reason": "No available slots"})
            return {"status": "error", "message": "No available slots found"}
        
        # Schedule event
        event_details = {
            "event": request.get("event_name", "Unnamed Event"),
            "time": request.get("time"),
            "duration": request.get("duration", "1h")
        }
        result = schedule_event(event_details)
        
        # Log scheduling action
        store_consent(f"/vault/scheduling_action_{user_id}", {
            "action": "schedule_event",
            "event": event_details,
            "timestamp": request.get("timestamp")
        })
        
        # Notify user
        notification = notify_user(f"Scheduled {event_details['event']} at {event_details['time']}")
        
        return {
            "status": "success",
            "message": result,
            "notification": notification
        }