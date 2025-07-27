import requests

MCP_BASE_URL = "http://localhost:3000"

def list_calendars(user_id, consent_token):
    payload = {"user_id": user_id, "consent_token": consent_token}
    resp = requests.post(f"{MCP_BASE_URL}/list-calendars", json=payload)
    resp.raise_for_status()
    return resp.json()

def list_events(user_id, consent_token, calendar_id=None, time_min=None, time_max=None):
    payload = {
        "user_id": user_id,
        "consent_token": consent_token,
    }
    if calendar_id: payload["calendar_id"] = calendar_id
    if time_min: payload["time_min"] = time_min
    if time_max: payload["time_max"] = time_max
    resp = requests.post(f"{MCP_BASE_URL}/list-events", json=payload)
    resp.raise_for_status()
    return resp.json()

def search_events(user_id, consent_token, query, calendar_id=None):
    payload = {
        "user_id": user_id,
        "consent_token": consent_token,
        "query": query,
    }
    if calendar_id: payload["calendar_id"] = calendar_id
    resp = requests.post(f"{MCP_BASE_URL}/search-events", json=payload)
    resp.raise_for_status()
    return resp.json()

def create_event(user_id, consent_token, event_data, calendar_id=None):
    payload = {
        "user_id": user_id,
        "consent_token": consent_token,
        "event_data": event_data,
    }
    if calendar_id: payload["calendar_id"] = calendar_id
    resp = requests.post(f"{MCP_BASE_URL}/create-event", json=payload)
    resp.raise_for_status()
    return resp.json()

def update_event(user_id, consent_token, event_id, update_data, calendar_id=None):
    payload = {
        "user_id": user_id,
        "consent_token": consent_token,
        "event_id": event_id,
        "update_data": update_data,
    }
    if calendar_id: payload["calendar_id"] = calendar_id
    resp = requests.post(f"{MCP_BASE_URL}/update-event", json=payload)
    resp.raise_for_status()
    return resp.json()

def delete_event(user_id, consent_token, event_id, calendar_id=None):
    payload = {
        "user_id": user_id,
        "consent_token": consent_token,
        "event_id": event_id,
    }
    if calendar_id: payload["calendar_id"] = calendar_id
    resp = requests.post(f"{MCP_BASE_URL}/delete-event", json=payload)
    resp.raise_for_status()
    return resp.json()

def get_freebusy(user_id, consent_token, time_min, time_max, calendar_ids=None):
    payload = {
        "user_id": user_id,
        "consent_token": consent_token,
        "time_min": time_min,
        "time_max": time_max,
    }
    if calendar_ids: payload["calendar_ids"] = calendar_ids
    resp = requests.post(f"{MCP_BASE_URL}/get-freebusy", json=payload)
    resp.raise_for_status()
    return resp.json()

def list_colors(user_id, consent_token):
    payload = {"user_id": user_id, "consent_token": consent_token}
    resp = requests.post(f"{MCP_BASE_URL}/list-colors", json=payload)
    resp.raise_for_status()
    return resp.json()