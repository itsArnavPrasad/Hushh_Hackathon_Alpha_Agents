# hushh_mcp/external_mcp/google_calendar/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional

class CalendarEvent(BaseModel):
    id: str
    summary: str
    start: str  # ISO 8601 datetime string
    end: str    # ISO 8601 datetime string
    description: Optional[str] = None
    attendees: Optional[List[str]] = None
    location: Optional[str] = None
    status: Optional[str] = None

class FreeBusySlot(BaseModel):
    start: str  # ISO 8601 datetime string
    end: str    # ISO 8601 datetime string

class OAuthTokenPayload(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int  # epoch ms
    scope: str
    token_type: Optional[str] = "Bearer"
    id_token: Optional[str] = None