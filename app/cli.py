import argparse
from typing import Optional

from .indexing import IndexService
from .main import build_agent, get_api_key
from .i18n import t
from .logging_conf import configure_logging
from .tools import slack_notify
from dotenv import load_dotenv


def cmd_create_index(args: argparse.Namespace) -> None:
	service = IndexService()
	created = service.create_index(name=args.name, description=args.description)
	print(created)


def cmd_ingest_pdf(args: argparse.Namespace) -> None:
	service = IndexService()
	count = service.ingest_pdf(args.index, args.path)
	print({"index": args.index, "ingested": count, "path": args.path})
	slack_notify(f"Ingested {count} chunks from {args.path} into index {args.index}")


def cmd_chat(args: argparse.Namespace) -> None:
	lang = args.lang
	api_key = get_api_key()
	if not api_key:
		print(t("error.no_api_key", lang))
		return
	agent = build_agent()
	if agent is None:
		return

	session_id: Optional[str] = None
	slack_notify("Chat session started")

	def run_once(text: str):
		resp = agent.run(text, session_id=session_id)
		try:
			out = resp["data"]["output"]  # type: ignore[index]
			new_session = resp["data"].get("session_id")  # type: ignore[index]
			return out, new_session
		except Exception:
			return str(resp), session_id

	# Initial message if provided
	if args.initial:
		out, session_id = run_once(args.initial)
		print(out)

	# Interactive loop
	print(t("chat.exit_hint", lang))
	while True:
		try:
			user = input(t("chat.prompt", lang))
		except (EOFError, KeyboardInterrupt):
			break
		if not user:
			continue
		if user.strip().lower() in {"/exit", "exit", ":q", "quit"}:
			break
		out, session_id = run_once(user)
		print(out)

	slack_notify("Chat session ended")


def main() -> None:
	configure_logging()
	load_dotenv()
	parser = argparse.ArgumentParser(prog="aixp", description="aiXplain Certification CLI")
	sub = parser.add_subparsers(dest="cmd", required=True)

	p_idx = sub.add_parser("create-index", help="Create a new index")
	p_idx.add_argument("name", help="Index name")
	p_idx.add_argument("--description", default="", help="Index description")
	p_idx.set_defaults(func=cmd_create_index)

	p_ing = sub.add_parser("ingest-pdf", help="Ingest a local PDF into an index")
	p_ing.add_argument("index", help="Index ID or name")
	p_ing.add_argument("path", help="Path to PDF file")
	p_ing.set_defaults(func=cmd_ingest_pdf)

	p_chat = sub.add_parser("chat", help="Interactive back-and-forth chat with the LLM")
	p_chat.add_argument("--initial", help="Optional initial message", default="")
	p_chat.add_argument("--lang", help="Language for CLI prompts (en/ar)", default="en")
	p_chat.set_defaults(func=cmd_chat)

	args = parser.parse_args()
	args.func(args)


if __name__ == "__main__":
	main()