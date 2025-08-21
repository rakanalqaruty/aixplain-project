from __future__ import annotations

import os
import json
import logging
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def fetch_federal_register(query: str, per_page: int = 5) -> List[Dict[str, Any]]:
	url = "https://www.federalregister.gov/api/v1/documents.json"
	params = {"per_page": per_page, "search": query}
	resp = requests.get(url, params=params, timeout=30)
	resp.raise_for_status()
	data = resp.json()
	results: List[Dict[str, Any]] = []
	for item in data.get("results", []):
		title = item.get("title")
		snippet = item.get("excerpt") or item.get("summary") or ""
		source_url = item.get("html_url") or item.get("pdf_url")
		if title and source_url:
			results.append({"source": source_url, "title": title, "snippet": snippet})
	return results


def fetch_courtlistener(query: str, per_page: int = 5) -> List[Dict[str, Any]]:
	api_url = "https://www.courtlistener.com/api/rest/v3/search/"
	headers = {}
	token = os.getenv("COURTLISTENER_TOKEN")
	if token:
		headers["Authorization"] = f"Token {token}"
	params = {"q": query, "page_size": per_page}
	resp = requests.get(api_url, params=params, headers=headers, timeout=30)
	resp.raise_for_status()
	data = resp.json()
	results: List[Dict[str, Any]] = []
	for item in data.get("results", []):
		title = item.get("caseName") or item.get("absolute_url")
		snippet = item.get("snippet") or ""
		url_path = item.get("absolute_url")
		if url_path:
			source_url = f"https://www.courtlistener.com{url_path}" if url_path.startswith("/") else url_path
			results.append({"source": source_url, "title": title, "snippet": snippet})
	return results


def slack_notify(message: str) -> None:
	# Ensure .env is loaded in case caller didn't
	load_dotenv()
	webhook = os.getenv("SLACK_WEBHOOK_URL")
	if not webhook:
		return
	try:
		requests.post(webhook, data=json.dumps({"text": message}), headers={"Content-Type": "application/json"}, timeout=10)
	except Exception as exc:
		logger.warning("Slack notification failed: %s", exc)


def build_extra_contexts(question: str, max_items: int = 5) -> List[Dict[str, Any]]:
	contexts: List[Dict[str, Any]] = []
	q_lower = question.lower()
	try:
		if "federal register" in q_lower or "regulation" in q_lower:
			for r in fetch_federal_register(question, per_page=max_items):
				contexts.append({"source": r["source"], "text": f"{r['title']}: {r['snippet']}"})
		if "court" in q_lower or "case" in q_lower or "opinion" in q_lower:
			for r in fetch_courtlistener(question, per_page=max_items):
				contexts.append({"source": r["source"], "text": f"{r['title']}: {r['snippet']}"})
	except Exception as exc:
		logger.warning("External tool fetch failed: %s", exc)
	return contexts