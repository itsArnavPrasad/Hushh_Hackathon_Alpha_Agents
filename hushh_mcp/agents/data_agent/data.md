 This agent is a core part of a multi-agent AI system that fetches user data from Gmail, detects actionable sales opportunities, and routes insights after proper consent validation.

⸻

📩 User Data Agent – README

A modular AI Data Agent that connects to Gmail via MCP, extracts useful sales insights, ensures privacy with Hush Consent, and passes contextual data to Calendar and Sales Agents.

⸻

🚀 Overview

The User Data Agent automates the process of:
	1.	Fetching email data using Gmail MCP Tool.
	2.	Parsing email content for actionable sales insights (dates, contacts, intent).
	3.	Detecting meeting opportunities or follow-ups.
	4.	Triggering the Hush Consent Protocol for secure data processing.
	5.	Forwarding structured data to Calendar Agent or Sales Agent.

⸻

🧱 Agent File Structure

user-data-agent/
│
├── index.py                # Agent entrypoint & routing logic
├── manifest.py             # Metadata, capabilities, dependencies
├── operons/
│   ├── fetch_gmail_threads.py
│   ├── parse_sales_data.py
│   ├── detect_meeting_opportunities.py
│   ├── request_consent.py
│   └── store_and_share_insights.py
│
├── consent_layer/
│   └── hush_protocol_adapter.py   # Hush Consent Protocol integration
│
└── config/
    └── gmail_mcp_config.json      # MCP HTTP config & headers


⸻

🛠  Tools & Technologies

Tool	Purpose
Google Agent SDK	Build agent structure and lifecycle
Gmail MCP Tool	Fetch Gmail data over HTTP using MCP
Hush Consent Protocol	Secure access and permission gating
Python 3.10+	Development language
Operons	Modular functional logic (micro-task units)


⸻

⚙️ Step-by-Step Functionality

1. 📡 Connect to Gmail MCP
	•	File: fetch_gmail_threads.py
	•	Task: Use requests or internal MCP protocol client to access Gmail threads with filters (unread, label).
	•	Protocol: MCP HTTP

Example:

def fetch_gmail_threads():
    url = config["gmail_mcp_url"] + "/threads"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"labelIds": ["UNREAD", "IMPORTANT"], "maxResults": 10}
    response = requests.get(url, headers=headers, params=params)
    return response.json()


⸻

2. 🧠 Parse Emails
	•	File: parse_sales_data.py
	•	Task: Extract entities using LLM or regex/NLP: names, dates, contact info, intent keywords.

Logic:
	•	Use SpaCy or GPT function calling.
	•	Detect “Let’s meet”, “Follow up”, “Schedule”, etc.

⸻

3. 🎯 Detect Sales Opportunities
	•	File: detect_meeting_opportunities.py
	•	Task: Classify whether an email indicates scheduling, follow-up, or other intents.

Classifier Options:
	•	Rule-based: Keyword/regex matching.
	•	ML-based: Train binary/multilabel classifier (intent detection).

⸻

4. 🔐 Request Consent
	•	File: request_consent.py
	•	Task: Pause agent, invoke Hush Consent flow.

Flow:
	1.	Construct consent request JSON.
	2.	Send to Hush Consent Layer.
	3.	Await token/approval.
	4.	If denied, halt processing.

def request_consent(context_data):
    return hush_protocol.ask_for_consent(data=context_data, purpose="Sales Follow-up Detection")


⸻

5. 🔄 Forward to Other Agents
	•	File: store_and_share_insights.py
	•	Task: Post-parsing, forward metadata & structured data to:
	•	Calendar Agent for meeting slotting.
	•	Sales Agent for lead follow-up.

Method: Send via HTTP call to other agents or via GADK agent-to-agent messaging.

⸻

📁 manifest.py Example

manifest = {
    "name": "user-data-agent",
    "version": "1.0.0",
    "description": "Fetches and parses Gmail data to extract sales signals with consent gating.",
    "capabilities": ["fetch_data", "parse_emails", "classify_intent", "forward_insights"],
    "dependencies": ["requests", "hush-protocol-sdk", "spacy"],
    "entrypoint": "index.py"
}


⸻

🧠 index.py Example

from operons.fetch_gmail_threads import fetch_gmail_threads
from operons.parse_sales_data import parse_sales_data
from operons.detect_meeting_opportunities import detect_opportunities
from operons.request_consent import request_consent
from operons.store_and_share_insights import forward_data

def main():
    threads = fetch_gmail_threads()
    parsed = parse_sales_data(threads)
    opportunities = detect_opportunities(parsed)

    if request_consent(opportunities):
        forward_data(opportunities)
    else:
        print("Consent not granted. Aborting.")

if __name__ == "__main__":
    main()


⸻

🔗 Integration Flow

          ┌──────────────┐
          │  Gmail MCP   │  ←── HTTP Fetch (MCP Tool)
          └────┬─────────┘
               │
         fetch_gmail_threads
               │
         parse_sales_data
               │
    detect_meeting_opportunities
               │
       request_consent (Hush)
               ▼
 ┌─────────────────────┐
 │ Consent Approved?   │─────No──▶ Log, Halt
 └─────────┬───────────┘
           │Yes
 store_and_share_insights
     │                │
     ▼                ▼
Calendar Agent    Sales Agent


⸻

🧬 Code-Like Bacteria Design Principles Applied

Principle	Implementation
Micro-modular operons	Each function is an operon with clear boundary.
Swappable interfaces	MCP and Consent can be configured/swapped via manifest/config.
Reusable by other agents	Operons can be imported into Calendar/Sales agent.
Autonomous but composable	Can run standalone, or be invoked by User Agent.
Consent-first execution	All downstream flows gated behind Hush consent check.


⸻

📌 Notes
	•	The Gmail MCP Tool must be set up and served over HTTP with token-based auth.
	•	Hush Consent Layer must be available to handle permission flows.
	•	All agents should be stateless where possible, storing metadata externally (e.g., Redis/Postgres).
	•	Logs and activity metadata must be collected for transparency.

⸻

Let me know if you’d like the operon code templates, a Postman collection to test Gmail MCP, or a Consent Protocol mock server for local testing.