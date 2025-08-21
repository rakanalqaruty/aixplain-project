from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .tools import build_extra_contexts


def _extract_contexts(results: Any) -> List[Dict[str, str]]:
	contexts: List[Dict[str, str]] = []
	if isinstance(results, dict) and "results" in results:
		items = results.get("results", [])
		for item in items:
			if isinstance(item, dict):
				text = None
				source = None
				if "text" in item and isinstance(item["text"], str):
					text = item["text"]
					source = item.get("meta", {}).get("source") if isinstance(item.get("meta"), dict) else None
				elif "content" in item and isinstance(item["content"], str):
					text = item["content"]
					source = item.get("source")
				elif "document" in item and isinstance(item["document"], dict):
					doc = item["document"]
					for key in ("text", "content", "body"):
						if isinstance(doc.get(key), str):
							text = doc[key]
							break
						source = doc.get("source")
				if text:
					contexts.append({"text": text, "source": source or "index"})
	return contexts


def answer_with_rag(agent: Any, index_service: Any, index_id: str, question: str, top_k: int = 5) -> Dict[str, Any]:
	search_res = index_service.search(index_id=index_id, query=question, top_k=top_k)
	contexts = _extract_contexts(search_res)
	# Add external API contexts if relevant
	extra = build_extra_contexts(question, max_items=max(0, top_k - len(contexts)))
	for e in extra:
		contexts.append({"text": e.get("text", ""), "source": e.get("source", "external")})
	context_block = "\n\n".join(f"[Doc {i+1}] ({c['source']}) {c['text']}" for i, c in enumerate(contexts))
	prompt = (
		"You are a helpful assistant. Use ONLY the provided context to answer the question.\n"
		"If the answer isn't in the context, say you don't know.\n\n"
		f"Context:\n{context_block}\n\n"
		f"Question: {question}\n"
		"Answer concisely and cite sources by [Doc #]."
	)
	resp = agent.run(prompt)
	answer_text = None
	try:
		answer_text = resp["data"]["output"]  # type: ignore[index]
	except Exception:
		answer_text = str(resp)
	citations = [{"source": c["source"], "snippet": c["text"][:280]} for c in contexts]
	return {"answer": answer_text, "citations": citations}