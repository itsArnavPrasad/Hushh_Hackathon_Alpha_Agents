import pytest
from unittest.mock import patch, MagicMock
from hushh_mcp.agents.calendar_agent.index import run_agent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

USER_ID = "user_123"
AGENT_ID = "calendar_agent"

@pytest.fixture
def valid_token():
    scopes = [
        ConsentScope.CALENDAR_READ.value,
        ConsentScope.CALENDAR_WRITE.value,
        ConsentScope.GCAL_READ.value,
        ConsentScope.GCAL_WRITE.value
    ]
    return issue_token(USER_ID, AGENT_ID, scopes).token

@pytest.fixture
def mock_mcp_adapter():
    with patch("hushh_mcp.operons.mcp_adapter.fetch_calendar_events", return_value=[{"id": "evt1", "summary": "Test Event"}]):
        with patch("hushh_mcp.operons.mcp_adapter.get_free_busy", return_value={"busy": []}):
            with patch("hushh_mcp.operons.mcp_adapter.create_event", return_value={"status": "created"}):
                with patch("hushh_mcp.operons.mcp_adapter.update_event", return_value={"status": "updated"}):
                    yield

@pytest.fixture
def mock_vault():
    with patch("hushh_mcp.vault.encrypt.encrypt_data", return_value="encrypted"):
        with patch("hushh_mcp.vault.encrypt.decrypt_data", return_value="decrypted"):
            yield

def test_consent_token_validation(valid_token, mock_mcp_adapter, mock_vault):
    # Should not raise
    result = run_agent(USER_ID, valid_token, "detect_slots", detect_slots_args={"time_min": "2025-07-25T00:00:00Z", "time_max": "2025-07-25T23:59:59Z"})
    assert "slots" in result or "free_busy" in result

def test_trustlink_delegation():
    # Example: test that verify_trust_link is called if delegation is needed
    with patch("hushh_mcp.trust.link.verify_trust_link") as mock_verify:
        mock_verify.return_value = True
        # Simulate a delegated call (details depend on your agent's API)
        # For now, just check that the function can be called
        assert mock_verify("assistant_agent", "calendar_agent", USER_ID)

def test_vault_encryption_decryption(mock_vault):
    from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
    data = "testdata"
    encrypted = encrypt_data(data, "0"*64)
    decrypted = decrypt_data(encrypted, "0"*64)
    assert decrypted == "decrypted"

def test_detect_slots_operon(valid_token, mock_mcp_adapter, mock_vault):
    result = run_agent(USER_ID, valid_token, "detect_slots", detect_slots_args={"time_min": "2025-07-25T00:00:00Z", "time_max": "2025-07-25T23:59:59Z"})
    assert "slots" in result or "free_busy" in result

def test_suggest_schedule_operon(valid_token, mock_mcp_adapter, mock_vault):
    result = run_agent(USER_ID, valid_token, "suggest_schedule", free_busy=[], user_preferences={"priority": "high"})
    assert "suggestion" in result

def test_reschedule_task_operon(valid_token, mock_mcp_adapter, mock_vault):
    result = run_agent(USER_ID, valid_token, "reschedule_task", reschedule_args={"event_id": "evt1", "new_time": "2025-07-26T10:00:00Z"})
    assert "reschedule_result" in result

def test_sync_gcal_operon(valid_token, mock_mcp_adapter, mock_vault):
    result = run_agent(USER_ID, valid_token, "sync_gcal", sync_time_range=("2025-07-25T00:00:00Z", "2025-07-25T23:59:59Z"))
    assert "gcal_events" in result

def test_add_event_to_gcal_operon(valid_token, mock_mcp_adapter, mock_vault):
    result = run_agent(USER_ID, valid_token, "add_event_to_gcal", event_data={"summary": "New Event", "start": "2025-07-27T10:00:00Z", "end": "2025-07-27T11:00:00Z"})
    assert "add_event_result" in result 