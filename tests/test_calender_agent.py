import pytest
from unittest.mock import patch
from hushh_mcp.agents.calendar_agent.index import run_agent
from hushh_mcp.consent.token import issue_token, revoke_token
from hushh_mcp.constants import ConsentScope

USER_ID = "user_123"
AGENT_ID = "calendar_agent"

@pytest.fixture
def token_gcal_read():
    return issue_token(USER_ID, AGENT_ID, ConsentScope.AGENT_GCAL_READ).token

@pytest.fixture
def token_gcal_write():
    return issue_token(USER_ID, AGENT_ID, ConsentScope.AGENT_GCAL_WRITE).token

@pytest.fixture
def mock_mcp_adapter():
    with patch("hushh_mcp.operons.mcp_adapter.list_events", return_value=[{"id": "evt1", "summary": "Test Event"}]):
        with patch("hushh_mcp.operons.mcp_adapter.create_event", return_value={"status": "created"}):
            with patch("hushh_mcp.operons.mcp_adapter.get_freebusy", return_value={"busy": []}):
                with patch("hushh_mcp.operons.mcp_adapter.list_calendars", return_value=[{"id": "primary", "summary": "Primary"}]):
                    with patch("hushh_mcp.operons.mcp_adapter.list_colors", return_value={"event": {"1": "#a4bdfc"}}):
                        with patch("hushh_mcp.operons.mcp_adapter.update_event", return_value={"status": "updated"}):
                            yield

@pytest.fixture
def mock_vault():
    with patch("hushh_mcp.vault.encrypt.encrypt_data", return_value="encrypted"):
        with patch("hushh_mcp.vault.encrypt.decrypt_data", return_value="decrypted"):
            yield

def test_sync_gcal_operon(token_gcal_read, mock_mcp_adapter, mock_vault):
    result = run_agent(
        USER_ID,
        token_gcal_read,
        "sync_gcal",
        sync_time_range=("2025-07-25T00:00:00Z", "2025-07-25T23:59:59Z")
    )
    assert "gcal_events" in result

def test_add_event_to_gcal_operon(token_gcal_write, mock_mcp_adapter, mock_vault):
    result = run_agent(
        USER_ID,
        token_gcal_write,
        "add_event_to_gcal",
        event_data={
            "summary": "New Event",
            "start": "2025-07-27T10:00:00Z",
            "end": "2025-07-27T11:00:00Z"
        }
    )
    assert "add_event_result" in result

def test_list_calendars(token_gcal_read, mock_mcp_adapter, mock_vault):
    result = run_agent(
        USER_ID,
        token_gcal_read,
        "list_calendars"
    )
    assert "calendars" in result

def test_list_colors(token_gcal_read, mock_mcp_adapter, mock_vault):
    result = run_agent(
        USER_ID,
        token_gcal_read,
        "list_colors"
    )
    assert "colors" in result

def test_get_freebusy(token_gcal_read, mock_mcp_adapter, mock_vault):
    result = run_agent(
        USER_ID,
        token_gcal_read,
        "get_freebusy",
        freebusy_time_range=("2025-07-25T00:00:00Z", "2025-07-25T23:59:59Z")
    )
    assert "freebusy_result" in result

def test_reschedule_task_operon(token_gcal_write, mock_mcp_adapter, mock_vault):
    result = run_agent(
        USER_ID,
        token_gcal_write,
        "reschedule_task",
        reschedule_args={
            "event_id": "evt1",
            "new_time": "2025-07-26T10:00:00Z"
        }
    )
    assert "reschedule_result" in result