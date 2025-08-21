# aiXplain Certification Project Scaffold

Prerequisites
- Python 3.10+
- aiXplain API key

Setup
- Create venv and activate (Windows PowerShell):
  - python -m venv .venv
  - .venv\\Scripts\\Activate.ps1
- Install deps: pip install -r requirements.txt
- Set env var `AIXPLAIN_API_KEY` (see ENV.md)

Optional configuration
- `AIXPLAIN_LLM_ID` — override LLM powering the agent
- `AIXPLAIN_TOOL_ID` — attach a model tool by ID
- or function-based tool:
  - `AIXPLAIN_TOOL_FUNCTION` (e.g., TEXT_GENERATION, OCR)
  - `AIXPLAIN_TOOL_SUPPLIER` (e.g., GOOGLE, MICROSOFT)
- External APIs:
  - `COURTLISTENER_TOKEN` — optional token for higher rate limits
- Notifications:
  - `SLACK_WEBHOOK_URL` — send basic notifications on ingestion/chat sessions
- Logging:
  - `LOG_LEVEL` — DEBUG/INFO/WARNING/ERROR (default: INFO)

CLI usage
- Help: `python main.py --help`
- Create an index: `python main.py create-index demo-index --description "Demo"`
- Ingest your PDF: `python main.py ingest-pdf demo-index Certification-Course-Project.pdf`
- Chat (interactive): `python main.py chat --initial "Hello" --lang en`
  - Then type messages; `/exit` to quit

Programmatic run (demo)
- python -m app.main

Notes on certification requirements
- The scaffold supports: agent creation, tool configuration, index creation/ingestion/search (programmatic), interactive LLM chat via CLI, and RAG with structured citations in `app/main.py`.
- External API contexts (Federal Register, CourtListener) are included in RAG answers when relevant.
- Replace placeholder Index SDK calls in `app/indexing.py` with exact aiXplain Index APIs in your account for full compliance.