
CALENDAR AGENT  

## 1️⃣ **High-Level Architecture**

- **Calendar Agent** is a privacy-preserving, fully autonomous AI assistant that manages your calendar (Google Calendar) using the HushhMCP protocol.
- **Key Principles:** Consent-first, modular (bacteria architecture), end-to-end encryption, composable, auditable, and trust-delegation ready.
- **Core Technologies:** Python, LangGraph (state machine orchestration), Gemini LLM (for reasoning), Google Calendar MCP (for real calendar integration), Hushh Consent/Trust/Vault.

Explicit Scopes Used:(as in manifest.py)
calendar.read — Read access to calendar data (free/busy, events)
calendar.write — Write access to calendar data (create/update events)
gcal.read — Read access to Google Calendar via MCP
gcal.write — Write access to Google Calendar via MCP

## 2️⃣ **Directory Structure & Key Files**

```
hushh_mcp/
├── agents/
│   └── calendar_agent/
│       ├── index.py         # Main orchestrator (LangGraph state machine)
│       ├── manifest.py      # Agent metadata, scopes
│       ├── operons/         # Modular, single-responsibility functions
│       │   ├── detect_slots.py
│       │   ├── suggest_schedule.py
│       │   ├── reschedule_task.py
│       │   ├── gcal_sync.py
│       │   └── utils.py
│       └── state/           # Memory, prompts, LLM utils
│           ├── memory.py
│           ├── prompts.py
│           └── gemini_llm.py
├── consent/
│   └── token.py             # Consent token creation/validation
├── trust/
│   └── link.py              # TrustLink creation/validation
├── vault/
│   └── encrypt.py           # Encryption/decryption APIs
├── external_mcp/
│   └── google_calendar/
│       ├── mcp_adapter.py   # Google Calendar MCP adapter
│       └── schemas.py       # Data models for events, tokens, etc.
└── tests/
    └── test_calender_agent.py # Full pytest suite
```

---

## 3️⃣ **How Each Operon Works**

### **A. detect_slots.py**
- **Purpose:** Find free/busy slots for a user.
- **Logic:**  
  1. Validates consent token for `calendar.read`.
  2. Calls `get_free_busy` from the Google Calendar MCP adapter.
  3. Optionally uses Gemini LLM to explain the slots in natural language.
  4. Stores results in agent memory for context.
- **Bacteria Principle:** Only handles slot detection, nothing else.

### **B. suggest_schedule.py**
- **Purpose:** Suggest the best time for a task using LLM reasoning.
- **Logic:**  
  1. Validates consent token for `calendar.read`.
  2. Formats a prompt using user preferences and free slots.
  3. Calls Gemini LLM via `gemini_chat`.
  4. Parses and returns the LLM’s suggestion.
- **Bacteria Principle:** Only handles schedule suggestion, nothing else.

### **C. reschedule_task.py**
- **Purpose:** Handle rescheduling, cancellation, or adjustment of events.
- **Logic:**  
  1. Validates consent token for `calendar.write`.
  2. Uses Gemini LLM to suggest a new time or explain conflicts.
  3. If a new time is suggested, calls `update_event` in the MCP adapter.
  4. Returns the result and LLM’s reasoning.
- **Bacteria Principle:** Only handles rescheduling, nothing else.

### **D. gcal_sync.py**
- **Purpose:** Sync events with Google Calendar (read/write).
- **Logic:**  
  1. Validates consent token for `gcal.read` or `gcal.write`.
  2. For reading, calls `fetch_calendar_events` in the MCP adapter.
  3. For writing, calls `create_event` in the MCP adapter.
  4. Stores results in agent memory.
- **Bacteria Principle:** Only handles sync, nothing else.

### **E. utils.py**
- **Purpose:** Utility functions (e.g., natural language time parsing).
- **Logic:**  
  1. Uses Gemini LLM for advanced parsing if needed.
  2. Returns parsed time ranges.

---

## 4️⃣ **How index.py Orchestrates Everything (LangGraph State Machine)**

- **State:** A plain Python dict with keys like `user_id`, `consent_token`, `intent`, and any operon-specific args.
- **Nodes:** Each operon is a node in the graph (`DetectSlots`, `SuggestSchedule`, etc.).
- **Routing:**  
  - The entry node is always `DetectSlots`.
  - After slot detection, a router function (`intent_router`) decides which node to go to next based on the user’s intent (e.g., `suggest_schedule`, `reschedule_task`, etc.).
  - Direct edges connect nodes for follow-up logic (e.g., after suggesting a schedule, go to event creation).
- **Consent Validation:**  
  - At the start of `run_agent`, the consent token is validated once.
  - All required scopes are checked to be present in the token.
- **Execution:**  
  - The graph is compiled and invoked with the initial state.
  - Each node only touches its own logic and state keys (bacteria principle).

---


### **5. How the Agent Uses MCP**
- The agent’s MCP adapter (`mcp_adapter.py`) makes HTTP requests to the MCP server for all calendar operations.
- All OAuth and Google API logic is handled by the MCP server, not the agent.
- The agent never sees or stores plaintext OAuth tokens.

---

## 6️⃣ **Consent, Token, and Hushh Protocol Integration**

### **A. Consent Tokens**
- Created using `issue_token` in `token.py`.
- Can include multiple scopes (e.g., `calendar.read`, `calendar.write`, `gcal.read`, `gcal.write`).
- Are cryptographically signed and time-limited.
- Validated at the start of every agent run and before every operon action.

### **B. TrustLinks**
- Used for agent-to-agent delegation (e.g., if Calendar Agent calls Notification Agent).
- Created and validated using `link.py`.
- Include scope, agent IDs, and are cryptographically signed.

### **C. Vault Encryption**
- All sensitive data (tokens, events) is encrypted using AES-256-GCM via `vault/encrypt.py`.
- No plaintext calendar or task data is ever stored or transmitted.

### **D. Hushh Protocol Compliance**
- Every operon checks consent and scope before accessing user data.
- All actions are auditable and logged.
- No hardcoded trust or access.

---

## 7️⃣ **How to Run and Test the Calendar Agent**

### **A. Prerequisites**
- Python 3.10+
- All dependencies installed (`pip install -r requirements.txt`)
- `.env` file with all required keys (`SECRET_KEY`, `VAULT_ENCRYPTION_KEY`, `GEMINI_API_KEY`, `GOOGLE_CALENDAR_MCP_URL`)
- Google Calendar MCP server running and authenticated

### **B. Run the Agent Manually**
```sh
python hushh_mcp/agents/calendar_agent/index.py <user_id> <consent_token> <intent> <json_args>
```
Example:
```sh
python hushh_mcp/agents/calendar_agent/index.py user_123 <token> suggest_schedule '{"detect_slots_args": {"time_min": "...", "time_max": "..."}}'
```

### **C. Run the Test Suite**
```sh
PYTHONPATH=. pytest tests/test_calender_agent.py
```
- This will run all operon and integration tests, mocking external services for speed and reliability.






