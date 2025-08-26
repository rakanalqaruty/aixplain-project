# Policy Navigator Agent (aiXplain Certification)

A multi-agent RAG-style scaffold that lets users ingest policy/regulatory documents and chat with an LLM. It supports PDF/website/dataset ingestion (programmatic), structured RAG answers with citations, external government API context (Federal Register, CourtListener), Slack notifications, logging, and basic i18n.

**Demo Video**: See `assets/demo-video.mp4` for a walkthrough of the application features.

## What it does
- Interactive chat with an aiXplain-powered agent (CLI)
- Create a vector index and ingest knowledge (PDF via CLI; website/dataset programmatically)
- Answer questions using RAG with citations (programmatic demo)
- Enrich answers with context from government APIs (Federal Register, CourtListener)
- Send Slack notifications on ingestion/chat sessions (optional)
- Logging and simple multilingual prompts for CLI (en/ar)

## Architecture (high-level)
- `app/cli.py`: CLI for chat and ingestion
- `app/main.py`: Programmatic demo (agent + RAG with citations)
- `app/indexing.py`: Index management; ingestion for PDF, website, dataset; simple text chunking
- `app/rag.py`: RAG composition (retrieval + prompt + citations)
- `app/tools.py`: External APIs (Federal Register, CourtListener) and Slack notifications
- `app/logging_conf.py`: Logging setup
- `app/i18n.py`: Minimal i18n strings

## Setup
1) Create and activate a virtual environment (Windows PowerShell):
   - `python -m venv .venv`
   - `.venv\Scripts\Activate.ps1`
2) Install dependencies:
   - `pip install -r requirements.txt`
3) Configure environment variables (`.env` or your shell):
```dotenv
# Required
AIXPLAIN_API_KEY=your_api_key_here

# Optional (choose ONE of these approaches to attach a tool)
AIXPLAIN_TOOL_ID=               # e.g., marketplace model/tool ID

SLACK_WEBHOOK_URL=              # Slack incoming webhook for notifications

# Optional logging
LOG_LEVEL=INFO                  # DEBUG/INFO/WARNING/ERROR
```

## CLI usage
- Help: `python main.py --help`
- Create an index: `python main.py create-index demo-index --description "Demo"`
- Ingest a PDF: `python main.py ingest-pdf demo-index Certification-Course-Project.pdf`
- Chat (interactive): `python main.py chat --initial "Hello" --lang en`
  - Then type messages; `/exit` to quit

## Programmatic usage (examples)
Run the built-in demo (agent + RAG with citations):
- `python -m app.main`

Ingest a website and a dataset programmatically:
```python
from app.indexing import IndexService

service = IndexService()
index = service.create_index("demo-index")
index_id = index.get("id", "demo-index")

# Website ingestion
service.ingest_website(index_id, "https://www.federalregister.gov/", chunk=True)

# Dataset ingestion (CSV or JSON)
# By default concatenates object-typed columns; specify columns via text_columns=[...]
service.ingest_dataset(index_id, "data/policies.csv", chunk=True)
```

Ask with RAG and citations programmatically:
```python
from app.main import build_agent
from app.rag import answer_with_rag

agent = build_agent()
res = answer_with_rag(agent, service, index_id, "When does this policy take effect?", top_k=5)
print(res["answer"])      # Model answer
print(res["citations"])   # List of {source, snippet}
```

## Data sources (update with your selections)
- Course PDF: `Certification-Course-Project.pdf` (provided)
- Dataset(s): add links here (e.g., Kaggle, Data.gov, UCI)
  - Example: https://www.kaggle.com/ (search relevant regulatory datasets)
- Website(s): add links here (e.g., EPA, WHO, Federal Register pages)
  - Example: `https://www.federalregister.gov/`

## Tool integration steps
- Marketplace tool: set `AIXPLAIN_TOOL_ID` to a valid aiXplain tool/model ID
- Function/supplier tool: set `AIXPLAIN_TOOL_FUNCTION` and `AIXPLAIN_TOOL_SUPPLIER`
- External APIs:
  - Federal Register and CourtListener are used for supplemental context in RAG
  - Optional: set `COURTLISTENER_TOKEN` for improved rate limits
- Slack notifications: set `SLACK_WEBHOOK_URL` to receive messages on ingestion/chat

## Example I/O
- Chat (CLI):
  - Input: `python main.py chat --initial "Summarize the project requirements."`
  - Output: A concise summary response from the agent
- RAG (programmatic):
  - Input question: "What are the compliance requirements for small businesses?"
  - Output: `{ "answer": "...", "citations": [{"source": "...", "snippet": "..."}, ...] }`

## Troubleshooting
- SDK import issues: ensure your venv is active and run `pip install -r requirements.txt`
- No Slack notifications:
  - Verify `SLACK_WEBHOOK_URL` is set in your environment (and `.env` is loaded)
  - Test directly: send a POST with a small JSON payload to the webhook
- CourtListener rate limits: add `COURTLISTENER_TOKEN`
- Missing or poor retrieval: ensure your content is ingested and consider smaller chunk sizes

## Future improvements
- Demonstrate three aiXplain tool types end-to-end
- Multi-agent orchestration (e.g., retrieval agent + answer agent)
- Improved HTML extraction and better chunking strategies
- Richer UI (web-based) and deployment instructions
- Memory/caching, guardrails, and evaluation metrics