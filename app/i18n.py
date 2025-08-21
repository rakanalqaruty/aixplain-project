from __future__ import annotations

from typing import Dict

_STRINGS: Dict[str, Dict[str, str]] = {
	"en": {
		"chat.exit_hint": "Type /exit to quit.",
		"error.no_api_key": "Error: AIXPLAIN_API_KEY is not set. See ENV.md to configure.",
		"chat.prompt": "> ",
	},
	"ar": {
		"chat.exit_hint": "اكتب /exit للخروج.",
		"error.no_api_key": "خطأ: لم يتم ضبط AIXPLAIN_API_KEY. راجع ENV.md.",
		"chat.prompt": "> ",
	},
}


def t(key: str, lang: str) -> str:
	lang_map = _STRINGS.get(lang, _STRINGS["en"])  # fallback to en
	return lang_map.get(key, _STRINGS["en"].get(key, key))