from typing import Dict, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.vault import store_consent
from google.adk.tools import Tool
from chrono_agent.tools.apply_preferences import apply_preferences
from chrono_agent.tools.notify_user import notify_user

class PreferencesOperon:
    """Operon for enforcing user-defined calendar preferences."""
    
    required_scopes = [ConsentScope.VAULT_READ_CALENDAR]
    
    def __init__(self):
        self.tools = [
            Tool(name="apply_preferences", function=apply_preferences),
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
        """Process a preference application request."""
        # Validate consent
        self.validate_consent(token, user_id)
        
        # Extract event details
        event_details = {
            "event": request.get("event_name", "Unnamed Event"),
            "time": request.get("time"),
            "duration": request.get("duration", "1h"),
            "priority": request.get("priority", "normal")
        }
        
        # Apply preferences
        preference_result = apply_preferences(event_details)
        
        # Log preference application
        store_consent(f"/vault/preference_application_{user_id}", {
            "action": "apply_preferences",
            "event": event_details,
            "result": preference_result,
            "timestamp": request.get("timestamp")
        })
        
        # Check if preferences block scheduling
        if not preference_result.get("is_valid"):
            notification = notify_user(
                f"Cannot schedule {event_details['event']} at {event_details['time']} "
                f"due to {preference_result.get('reason', 'user preferences')}"
            )
            return {
                "status": "error",
                "message": preference_result.get("reason", "Blocked by user preferences"),
                "notification": notification
            }
        
        # Return valid scheduling details
        notification = notify_user(
            f"Preferences applied for {event_details['event']} at {event_details['time']}"
        )
        
        return {
            "status": "success",
            "message": "Preferences applied successfully",
            "event_details": event_details,
            "notification": notification
        }