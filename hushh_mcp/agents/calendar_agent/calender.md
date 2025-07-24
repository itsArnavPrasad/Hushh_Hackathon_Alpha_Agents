Calendar Agent 

Calender agent is a fully autonomous, privacy-preserving AI calendar assistant designed using the HushhMCP framework. It intelligently schedules, reschedules, and manages tasks by integrating with your calendar (e.g., Google Calendar), while **strictly enforcing trust, consent, and encrypted data workflows**.

> 🔐 Built using the **Hushh Consent Protocol**, **LangGraph**, and **LangChain**.

---

## 📂 Directory Structure

hushh_mcp/
├── agents/
│   └── calendar_agent/
│       ├── index.py         # LangGraph state machine, main entry
│       ├── manifest.py      # Agent metadata, scopes
│       ├── operons/
│       │   ├── detect_slots.py
│       │   ├── suggest_schedule.py
│       │   ├── reschedule_task.py
│       │   ├── gcal_sync.py
│       │   └── utils.py
│       └── state/
│           ├── memory.py
│           └── prompts.py
├── consent/
│   └── token.py
├── trust/
│   └── link.py
├── vault/
│   └── encrypt.py
├── external_mcp/
│   └── google_calendar/
│       ├── mcp_adapter.py
│       └── schemas.py
└── tests/
    └── test_calendar_agent.py
	
## 🧠 Agent Capabilities

ChronoAgent supports the following key operations (**Operons**) built as modular LangGraph steps:

| Operon Function              | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `detectAvailableSlots()`     | Finds available free slots using encrypted calendar data                   |
| `suggestOptimalSchedule()`   | Uses LLM reasoning + user priorities to generate the best schedule plan    |
| `rescheduleTask(userIntent)` | Handles natural language commands to reschedule, cancel, or adjust events |
| `syncWithGCal()`             | Bi-directional sync with Google Calendar via OAuth token                   |

Each operon operates with strict **consent-based access**, full **end-to-end encryption**, and **contextual memory**.

---

## 🔐 Hushh Protocol Compliance

### ✅ Consent Token Enforcement

Every operon checks:

- `validate_token()` from `consent/token.py` before accessing any user data
- Consent Scope must match (e.g., `calendar.read`, `calendar.write`)
- Tokens are scoped, timestamped, and include metadata like userID, agentID

### ✅ TrustLink Delegation

- If ChronoAgent calls another agent (e.g., NotificationAgent), it must use `create_trust_link()` from `trust/link.py`
- All delegated actions include metadata and consent propagation

### ✅ Vault Encryption

All calendar data is accessed using:

- `encrypt_data()` and `decrypt_data()` from `vault/encrypt.py`
- Stored with structured metadata: userID, agentID, timestamp, data scope
- No plaintext calendar or task data is stored or transmitted

---

## 🧠 LangGraph-Based Agent Logic

The ChronoAgent runs as a **LangGraph state machine**, managing calendar logic as transitions:

```python
States = {
  "DetectSlots",
  "SuggestSchedule",
  "Reschedule",
  "SyncGCal",
  "Done"
}

The graph transitions based on:
	•	User intent (parsed via LangChain prompt templates)
	•	Schedule constraints and priorities
	•	Consent tokens validity
	•	System conflicts (e.g., time overlaps)

⸻

⚙️ Setup Instructions

🔧 Prerequisites
	•	Python 3.10+
	•	Google Calendar API credentials
	•	LangChain + LangGraph
	•	Hushh SDK (provided in base fork)

📦 Install Requirements

pip install -r requirements.txt

🔐 Environment Variables

Create a .env file:

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
HUSHH_ENCRYPTION_KEY=32-byte-secret


⸻

🚀 Running ChronoAgent

python hushh_mcp/agents/chronoagent/index.py

This launches the interactive loop or webhook endpoint depending on config.

⸻

🧪 Testing the Agent

Run all agent tests using:

pytest tests/test_chronoagent.py

Tests include:
	•	Consent token validation
	•	TrustLink delegation logic
	•	Operon behaviors (slot detection, suggestion accuracy)
	•	Vault encryption round-trips
	•	Chat-based intent parsing

⸻

🧬 Code Principles Followed

Principle	Applied In
🦠 Bacteria Architecture	Small, autonomous operons for each function
🧩 Composability	Each operon can run independently or in graphs
🔁 Observability + Debugging	Each LangGraph step logs state & outcome
🧠 Agent State Isolation	Operons don’t share memory directly
🔐 Minimal Trust Surface	Vault + Consent enforced strictly in every operon


⸻

📘 Example Consent Flow
	1.	User Request:
“Schedule a meeting with Dr. Nair this Friday between 3–5pm.”
	2.	ChronoAgent Flow:
	•	Receives command via voice/chat interface
	•	Checks calendar.write consent token via validate_token()
	•	Queries encrypted data vault for availability
	•	Suggests best slot with suggestOptimalSchedule()
	•	Creates event in GCal via syncWithGCal()
	•	Logs all steps with proper metadata
	3.	Sample Consent Token:

{
  "user_id": "user_456",
  "agent_id": "chronoagent",
  "scope": ["calendar.read", "calendar.write"],
  "issued_at": "2025-07-24T10:10:00Z",
  "valid_until": "2025-07-25T10:10:00Z",
  "signature": "0x9ab3c..."
}

	4.	Sample TrustLink (if NotificationAgent is used):

{
  "delegator": "chronoagent",
  "delegatee": "notificationagent",
  "scope": ["notify.event"],
  "issued_at": "...",
  "token": "<delegated_token_here>"
}


⸻

💡 Future Add-ons (Optional)
	•	Agent-to-agent coordination with MeetingCoordinationAgent
	•	Smart notifications using NotificationAgent
	•	Work/personal schedule segregation
	•	Slack / Discord integrations

⸻

🙌 Team & Credits

Built by Team ⏱ ChronoSyncers
Submitted to: Hushh Hackathon 2025
Powered by: LangGraph, LangChain, HushhMCP, Google Calendar, OpenAI API


To connect your ChronoAgent (Calendar Manager) with essential MCP (Model-Context-Protocol) services such as Google Calendar MCP, while aligning with the Hushh architecture and trust/consent protocols, we need a bulletproof integration strategy that’s secure, compliant, and scalable.

Here is a very detailed step-by-step breakdown of how to connect your ChronoAgent to Google Calendar MCP and other calendar MCPs (if needed), using LangChain + LangGraph, inside the Hushh multi-agent trust-based architecture.

⸻

✅ OBJECTIVE

Enable ChronoAgent to:
	•	Access and manipulate user’s Google Calendar via a trusted MCP agent
	•	Comply with Hushh ConsentToken, TrustLink, and Vault encryption flows
	•	Act only when authorized by the user (via signed tokens)
	•	Leverage LangChain to plan + act, LangGraph for agent loop
	•	Use syncWithGCal() operon to read/write events securely

⸻

📦 MODULE STRUCTURE OVERVIEW

hushh_mcp/
│
├── agents/
│   └── chrono_agent/
│       ├── index.py
│       ├── manifest.py
│       ├── planner/
│       ├── executor/
│       └── prompts/
│
├── consent/
│   └── token.py        🔐 issue_token(), validate_token()
│
├── trust/
│   └── link.py         🔗 create_trust_link()
│
├── vault/
│   └── encrypt.py      🔒 encrypt_data(), decrypt_data()
│
├── external_mcp/
│   └── google_calendar/
│       ├── mcp_adapter.py  ← You build this (OAuth, API client wrapper)
│       └── schemas.py
│
└── tests/
    └── test_chrono_agent.py


⸻

🔗 STEP 1: UNDERSTAND THE GOOGLE CALENDAR MCP SCOPE

Google Calendar’s API can be treated as a remote MCP agent. The interface should:
	•	Authenticate via OAuth2
	•	Expose methods to:
	•	Get free/busy time
	•	Create events
	•	Update or delete events
	•	Be wrapped as a LangChain Tool or LangGraph node

⸻

🧩 STEP 2: BUILD THE GOOGLE CALENDAR MCP ADAPTER

Path: hushh_mcp/external_mcp/google_calendar/mcp_adapter.py

Functions to include:

def authenticate_user(oauth_token: str) -> Dict:
    """Validate and store Google OAuth token in Vault."""
    # Use encrypt_data() here
    ...

def fetch_calendar_events(user_id: str, time_min, time_max) -> List[Dict]:
    """Retrieve calendar events within a time window using stored token."""
    ...

def get_free_busy(user_id: str, time_min, time_max) -> Dict:
    """Return free/busy schedule for user."""
    ...

def create_event(user_id: str, event_data: Dict) -> Dict:
    """Create a new calendar event in Google Calendar."""
    ...

def update_event(user_id: str, event_id: str, updates: Dict) -> Dict:
    """Update an existing event."""
    ...

Use the official Google Calendar Python client.

⸻

🔐 STEP 3: HANDLE AUTH + CONSENT SECURELY
	•	When a user connects their calendar:
	•	Call issue_token() → Save signed ConsentScope with gcal.read, gcal.write
	•	Store encrypted OAuth token in Vault
	•	Create TrustLink if another agent (e.g., MeetingBot) is allowed to act on their behalf

Example consent scope:

{
  "subject": "user_123",
  "resource": "google_calendar",
  "actions": ["read", "write"],
  "agent": "chrono_agent",
  "expires": "2025-08-01T00:00:00Z"
}


⸻

🧠 STEP 4: IMPLEMENT syncWithGCal() OPERON

In chrono_agent/executor/sync.py:

from hushh_mcp.external_mcp.google_calendar import fetch_calendar_events, create_event
from hushh_mcp.vault.encrypt import decrypt_data
from hushh_mcp.consent.token import validate_token

def syncWithGCal(user_id: str, consent_token: str, time_range: Tuple):
    validate_token(consent_token, scope="gcal.read")
    
    events = fetch_calendar_events(user_id, *time_range)
    
    # Optionally parse, sort, clean, or tag events
    return events

To write back:

def addEventToGCal(user_id: str, event_data: Dict, consent_token: str):
    validate_token(consent_token, scope="gcal.write")
    return create_event(user_id, event_data)


⸻

🧰 STEP 5: EXPOSE THIS AS LANGCHAIN TOOLS / LangGraph NODES

from langchain.tools import tool

@tool
def get_free_slots(...):
    """Returns user's free slots from Google Calendar"""
    ...

@tool
def schedule_event(...):
    """Creates a new event in Google Calendar"""
    ...

In LangGraph:
	•	Planner Node: Suggests best slots (calls get_free_slots tool)
	•	Executor Node: Creates events or reschedules (calls schedule_event)

⸻

🛡️ STEP 6: RESPECT TRUST + PRIVACY

When another agent (e.g., a productivity assistant) invokes ChronoAgent:
	•	It must first have a valid TrustLink
	•	You must check:

from hushh_mcp.trust.link import verify_trust_link

verify_trust_link(caller_agent="assistant_agent", target_agent="chrono_agent", user_id="123")


⸻

🧪 STEP 7: TEST END-TO-END

In tests/test_chrono_agent.py:
	•	Mock consent token and TrustLink
	•	Run:
	•	syncWithGCal() – ensure correct data format
	•	suggestOptimalSchedule() – validate time optimization logic
	•	rescheduleTask() – validate conflict resolution
	•	Test vault: encrypted storage + retrieval
	•	Simulate 3-agent flow (user → Chrono → GCal)

⸻

📄 README.MD UPDATES

In your README.md, explain:
	•	How ChronoAgent interfaces with external MCP (Google Calendar)
	•	Consent + Trust flow
	•	Security: OAuth, Vault encryption
	•	How users can revoke access
	•	Sample ConsentToken and TrustLink JSON
	•	Example prompt:
“Schedule Deep Work between 3-5pm tomorrow if I’m free”

⸻

🔄 FUTURE MCP INTEGRATIONS (Optional, Similar Pattern)
	•	Outlook Calendar MCP
	•	Apple Calendar via CalDAV
	•	Notion Calendar integration
	•	Internal Hushh Agents (e.g., for personal productivity analysis)

⸻

✅ CHECKLIST

Task	Status
gcal_adapter.py to wrap API	✅
OAuth token Vault storage	✅
ConsentToken generation & validation	✅
LangChain tools or LangGraph nodes	✅
End-to-end tests with mock tokens	✅
README with flows + JSON examples	✅


⸻

Let me know if you’d like a starter GitHub repo, full OAuth implementation code, or LangGraph config to wire up these nodes.