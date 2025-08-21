import os
from typing import Optional, List

from dotenv import load_dotenv

try:
	# Import lazily so that the file loads even if SDK isn't installed yet
	from aixplain.factories import AgentFactory  # type: ignore
except ImportError:
	AgentFactory = None  # type: ignore

# Optional SDK symbols; ignore failures without blocking AgentFactory
try:  # noqa: E722
	from aixplain.modules.agent import ModelTool, PipelineTool  # type: ignore
except Exception:  # noqa: E722
	ModelTool = None  # type: ignore
	PipelineTool = None  # type: ignore

try:  # noqa: E722
	from aixplain.enums import Function, Supplier  # type: ignore
except Exception:  # noqa: E722
	Function = None  # type: ignore
	Supplier = None  # type: ignore

from .indexing import IndexService
from .rag import answer_with_rag
from .logging_conf import configure_logging


def get_api_key() -> Optional[str]:
	load_dotenv()
	return os.getenv("AIXPLAIN_API_KEY")


def _build_tools() -> List[object]:
	tools: List[object] = []
	if AgentFactory is None:
		return tools

	tool_id = os.getenv("AIXPLAIN_TOOL_ID")
	if tool_id:
		try:  # noqa: E722
			tools.append(AgentFactory.create_model_tool(model=tool_id))  # type: ignore
		except Exception:
			pass
	else:
		func_name = os.getenv("AIXPLAIN_TOOL_FUNCTION")
		supplier_name = os.getenv("AIXPLAIN_TOOL_SUPPLIER")
		if func_name and Function is not None:
			try:  # noqa: E722
				func = getattr(Function, func_name, None)
				supp = getattr(Supplier, supplier_name, None) if (Supplier is not None and supplier_name) else None
				if func is not None:
					if supp is not None:
						tools.append(AgentFactory.create_model_tool(function=func, supplier=supp))  # type: ignore
					else:
						tools.append(AgentFactory.create_model_tool(function=func))  # type: ignore
			except Exception:
				pass
	return tools


def build_agent():
	if AgentFactory is None:
		print("aiXplain SDK not installed. Run: pip install -r requirements.txt")
		return None
	llm_id = os.getenv("AIXPLAIN_LLM_ID")
	tools = _build_tools()
	kwargs = {}
	if llm_id:
		kwargs["llm_id"] = llm_id
	if tools:
		kwargs["tools"] = tools
	return AgentFactory.create(
		name="Starter Agent",
		description="A minimal agent for aiXplain certification scaffold.",
		**kwargs,
	)


def demo_agent(agent) -> None:
	print("Running agent...")
	response = agent.run("Say hello and confirm you're alive.")
	try:
		print(response["data"]["output"])  # type: ignore[index]
	except Exception:
		print(response)


def demo_indexing(service: IndexService) -> str:
	created = service.create_index(name="demo-index", description="Temporary demo index")
	index_id = created.get("id", created.get("name", "demo-index"))
	print(f"Created index: {created}")
	count = service.ingest(index_id, [
		{"id": "1", "text": "aiXplain lets you build agents quickly."},
		{"id": "2", "text": "Agentic RAG combines retrieval with tool use."},
	])
	print(f"Ingested {count} documents")
	pdf_path = os.path.join(os.getcwd(), "Certification-Course-Project.pdf")
	if os.path.exists(pdf_path):
		try:
			added = service.ingest_pdf(index_id, pdf_path)
			print(f"Ingested {added} pages from {os.path.basename(pdf_path)}")
		except Exception as e:
			print(f"PDF ingest skipped: {e}")
	results = service.search(index_id, query="What is agentic RAG?", top_k=3)
	print(f"Search results: {results}")
	return str(index_id)


def demo_rag(agent, service: IndexService, index_id: str) -> None:
	result = answer_with_rag(
		agent=agent,
		index_service=service,
		index_id=index_id,
		question="What is agentic RAG?",
		top_k=3,
	)
	print("RAG answer:\n", result.get("answer"))
	print("Citations:")
	for c in result.get("citations", []):
		print(f"- {c['source']}: {c['snippet']}")


def main() -> None:
	configure_logging()
	api_key = get_api_key()
	if not api_key:
		print("Error: AIXPLAIN_API_KEY is not set. See ENV.md to configure.")
		return

	agent = build_agent()
	if agent is None:
		return
	demo_agent(agent)

	service = IndexService()
	index_id = demo_indexing(service)
	demo_rag(agent, service, index_id)


if __name__ == "__main__":
	main()