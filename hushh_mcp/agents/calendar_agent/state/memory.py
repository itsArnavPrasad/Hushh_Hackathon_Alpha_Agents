# hushh_mcp/agents/calendar_agent/state/memory.py

from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.config import VAULT_ENCRYPTION_KEY

class CalendarAgentMemory:
    """
    Bacteria-style: Each method is a single responsibility.
    Context memory is always encrypted at rest.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self._store = {}  # In-memory for demo; replace with persistent store in prod

    def save_context(self, key: str, value: dict):
        """
        Encrypt and store context for a given key.
        """
        plaintext = str(value)
        encrypted = encrypt_data(plaintext, VAULT_ENCRYPTION_KEY)
        self._store[key] = encrypted

    def load_context(self, key: str):
        """
        Decrypt and retrieve context for a given key.
        """
        encrypted = self._store.get(key)
        if not encrypted:
            return None
        plaintext = decrypt_data(encrypted, VAULT_ENCRYPTION_KEY)
        # For demo, assume value was a dict string
        try:
            return eval(plaintext)
        except Exception:
            return plaintext

    def clear_context(self, key: str):
        """
        Remove context for a given key.
        """
        if key in self._store:
            del self._store[key]