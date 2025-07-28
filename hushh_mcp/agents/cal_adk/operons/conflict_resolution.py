from typing import Dict, List, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.vault import store_consent
from google.adk.tools import Tool
from chrono_agent.tools.fetch_calendar_state import fetch_calendar_state
from chrono_agent.tools.resolve_conflict import resolve_conflict
from chrono_agent.tools.notify_user import notify_user

class ConflictResolutionOperon:
    """Operon for detecting and resolving calendar event conflicts."""
    
    required_scopes = [ConsentScope.VAULT_READ_CALENDAR, ConsentScope.VAULT_WRITE_CALENDAR]
    
    def __init__(self):
        self.tools = [
            Tool(name="fetch_calendar_state", function=fetch_calendar_state),
            Tool(name="resolve_conflict", function=resolve_conflict),
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
        """Process a conflict resolution request."""
        # Validate consent
        self.validate_consent(token, user_id)
        
        # Fetch calendar state
        calendar_state = fetch_calendar_state()
        if not calendar_state.get("events"):
            store_consent(f"/vault/conflict_resolution_no_events_{user_id}", {"reason": "No events to analyze"})
            return {"status": "success", "message": "No conflicts found"}
        
        # Check for conflicts
        event_details = {
            "event": request.get("event_name", "Unnamed Event"),
            "time": request.get("time"),
            "duration": request.get("duration", "1h"),
            "priority": request.get("priority", "normal")
        }
        conflicts = self.detect_conflicts(event_details, calendar_state.get("events"))
        
        if not conflicts:
            store_consent(f"/vault/conflict_resolution_no_conflicts_{user_id}", {"event": event_details})
            return {"status": "success", "message": "No conflicts detected"}
        
        # Resolve conflicts
        resolution = resolve_conflict(event_details, conflicts)
        
        # Log resolution action
        store_consent(f"/vault/conflict_resolution_action_{user_id}", {
            "action": "resolve_conflict",
            "event": event_details,
            "resolution": resolution,
            "timestamp": request.get("timestamp")
        })
        
        # Notify user
        notification = notify_user(f"Conflict detected for {event_details['event']}. Suggested: {resolution.get('suggested_time')}")
        
        return {
            "status": "success",
            "message": resolution.get("message"),
            "suggested_time": resolution.get("suggested_time"),
            "notification": notification
        }
    
    def detect_conflicts(self, event_details: Dict, events: List[Dict]) -> List[Dict]:
        """Detect conflicts for the proposed event."""
        proposed_time = event_details.get("time")
        proposed_duration = event_details.get("duration")
        conflicts = [
            event for event in events
            if self.is_time_overlap(proposed_time, proposed_duration, event.get("time"), event.get("duration"))
        ]
        return conflicts
    
    def is_time_overlap(self, time1: str, duration1: str, time2: str, duration2: str) -> bool:
        """Check if two events overlap (simplified logic)."""
        # Placeholder: Implement actual time overlap logic based on datetime parsing
        # For simplicity, assume string comparison or external datetime library
        return False  # Replace with actual overlap check