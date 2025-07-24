# hushh_mcp/external_mcp/google_calender/mcp_adapter.py

import httpx
import os

MCP_URL = os.getenv("GOOGLE_CALENDAR_MCP_URL", "http://localhost:3000")

def fetch_calendar_events(user_id: str, time_min: str, time_max: str):
    # You may need to pass a user/session token for multi-user support
    resp = httpx.get(
        f"{MCP_URL}/list-events",
        params={"user_id": user_id, "time_min": time_min, "time_max": time_max}
    )
    resp.raise_for_status()
    return resp.json()

def get_free_busy(user_id: str, time_min: str, time_max: str):
    resp = httpx.get(
        f"{MCP_URL}/get-freebusy",
        params={"user_id": user_id, "time_min": time_min, "time_max": time_max}
    )
    resp.raise_for_status()
    return resp.json()

def create_event(user_id: str, event_data: dict):
    resp = httpx.post(
        f"{MCP_URL}/create-event",
        json={"user_id": user_id, "event": event_data}
    )
    resp.raise_for_status()
    return resp.json()

def update_event(user_id: str, event_id: str, updates: dict):
    resp = httpx.post(
        f"{MCP_URL}/update-event",
        json={"user_id": user_id, "event_id": event_id, "updates": updates}
    )
    resp.raise_for_status()
    return resp.json()