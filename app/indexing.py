from __future__ import annotations

from typing import Iterable, Dict, Any, Optional, List

try:
	# aiXplain SDK imports (names based on common SDK structure)
	from aixplain.factories import IndexFactory  # type: ignore
	from aixplain.v2.index import Index  # type: ignore
except Exception:
	IndexFactory = None  # type: ignore
	Index = None  # type: ignore


def _chunk_text(text: str, max_len: int = 1000, overlap: int = 150) -> List[str]:
	chunks: List[str] = []
	start = 0
	while start < len(text):
		end = min(start + max_len, len(text))
		chunks.append(text[start:end])
		if end == len(text):
			break
		start = end - overlap
		if start < 0:
			start = 0
	return chunks


class IndexService:
	"""
	aiXplain Index (aiRIndex) interactions with graceful fallback.
	"""

	def __init__(self) -> None:
		self._sdk_available = IndexFactory is not None

	def create_index(self, name: str, description: str | None = None) -> Dict[str, Any]:
		if self._sdk_available:
			idx: Any = IndexFactory.create(name=name, description=description or "")  # type: ignore
			return getattr(idx, "__dict__", {"id": getattr(idx, "id", name), "name": name, "description": description or ""})
		return {"id": name, "name": name, "description": description or ""}

	def ingest(self, index_id: str, documents: Iterable[Dict[str, Any]]) -> int:
		if self._sdk_available:
			idx: Any = IndexFactory.get(index_id)  # type: ignore
			res = idx.ingest(list(documents))  # type: ignore
			if isinstance(res, dict) and "count" in res:
				return int(res["count"])  # type: ignore
			return len(list(documents))
		return len(list(documents))

	def search(self, index_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
		if self._sdk_available:
			idx: Any = IndexFactory.get(index_id)  # type: ignore
			res = idx.search(query=query, top_k=top_k)  # type: ignore
			return {"index_id": index_id, "query": query, "results": getattr(res, "results", res), "top_k": top_k}
		return {"index_id": index_id, "query": query, "results": [], "top_k": top_k}

	def ingest_pdf(self, index_id: str, pdf_path: str, chunk: bool = True) -> int:
		"""Basic PDF text extraction and ingestion (chunked)."""
		try:
			from pypdf import PdfReader  # type: ignore
		except Exception:
			raise RuntimeError("pypdf is not installed. Run: pip install -r requirements.txt")
		reader = PdfReader(pdf_path)
		total = 0
		for i, page in enumerate(reader.pages):
			try:
				text = (page.extract_text() or "").strip()
				if not text:
					continue
				if chunk:
					parts = _chunk_text(text)
					docs = [{"id": f"{pdf_path}#p{i+1}-{j}", "text": part, "meta": {"source": pdf_path, "page": i+1}} for j, part in enumerate(parts)]
					total += self.ingest(index_id, docs)
				else:
					total += self.ingest(index_id, [{"id": f"{pdf_path}#p{i+1}", "text": text, "meta": {"source": pdf_path, "page": i+1}}])
			except Exception:
				continue
		return total

	def ingest_website(self, index_id: str, url: str, chunk: bool = True) -> int:
		"""Fetch HTML, extract main text, and ingest (chunked)."""
		import requests
		from bs4 import BeautifulSoup
		resp = requests.get(url, timeout=30)
		resp.raise_for_status()
		soup = BeautifulSoup(resp.text, "lxml")
		# Simple extraction: all paragraphs
		paras = [p.get_text(strip=True) for p in soup.find_all("p")]
		text = "\n\n".join([p for p in paras if p])
		if not text:
			return 0
		if chunk:
			parts = _chunk_text(text)
			docs = [{"id": f"{url}#{i}", "text": part, "meta": {"source": url}} for i, part in enumerate(parts)]
			return self.ingest(index_id, docs)
		return self.ingest(index_id, [{"id": url, "text": text, "meta": {"source": url}}])

	def ingest_dataset(self, index_id: str, path: str, text_columns: Optional[List[str]] = None, chunk: bool = True) -> int:
		"""Ingest CSV/JSON datasets. text_columns defines which columns to concatenate as text."""
		import os
		import pandas as pd
		ext = os.path.splitext(path)[1].lower()
		if ext in {".csv"}:
			df = pd.read_csv(path)
		elif ext in {".json"}:
			df = pd.read_json(path)
		else:
			raise ValueError("Unsupported dataset type. Use CSV or JSON.")
		if df.empty:
			return 0
		cols = text_columns or [c for c in df.columns if df[c].dtype == object]
		count = 0
		for idx, row in df.iterrows():
			parts = [str(row[c]) for c in cols if pd.notna(row[c])]
			doc_text = "\n".join(parts).strip()
			if not doc_text:
				continue
			if chunk:
				pieces = _chunk_text(doc_text)
				docs = [{"id": f"{path}#{idx}-{i}", "text": p, "meta": {"source": path, "row": int(idx)}} for i, p in enumerate(pieces)]
				count += self.ingest(index_id, docs)
			else:
				count += self.ingest(index_id, [{"id": f"{path}#{idx}", "text": doc_text, "meta": {"source": path, "row": int(idx)}}])
		return count