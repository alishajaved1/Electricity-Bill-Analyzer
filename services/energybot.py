"""EnergyBot website guide: local knowledge base first, Gemini only when needed.

- Reuses the project's existing secure Gemini service (`services.gemini_service`) and config.
- Never receives bill data and never reveals keys/config (see `energybot_kb.SYSTEM_PROMPT`).
- Works without an API key: answers come from the built-in knowledge base.
"""
from __future__ import annotations

from dataclasses import dataclass

from config import get_api_key
from services import energybot_kb as kb
from services.gemini_service import GeminiError, guide_chat

MAX_QUESTION_CHARS = 500
MAX_AI_CALLS_PER_SESSION = 30


@dataclass
class BotReply:
    text: str
    source: str          # "local" | "ai" | "fallback"
    used_ai: bool = False


def _scrub(text: str) -> str:
    """Last line of defence: never echo the configured key, whatever the model produced."""
    key = get_api_key()
    if key and key in text:
        text = text.replace(key, "[hidden]")
    return text


def reply(history: list[dict], question: str, ai_calls_used: int = 0) -> BotReply:
    q = (question or "").strip()[:MAX_QUESTION_CHARS]
    if not q:
        return BotReply("Please type a question about the website and I'll help.", "local")

    local, _reason = kb.local_answer(q)
    if local:
        return BotReply(local, "local")

    if not get_api_key():
        return BotReply(kb.GENERAL_FALLBACK + "\n\n_AI chat is not configured on this site, so I'm answering from my built-in help only._", "fallback")
    if ai_calls_used >= MAX_AI_CALLS_PER_SESSION:
        return BotReply(kb.GENERAL_FALLBACK + "\n\n_This session has reached its AI chat limit; built-in help is still available._", "fallback")
    try:
        text = guide_chat(history, q, kb.SYSTEM_PROMPT)
    except GeminiError as e:
        msg = "The AI service isn't available right now." if str(e) == "MISSING_KEY" else str(e)
        return BotReply(f"{kb.GENERAL_FALLBACK}\n\n_{msg} I'm using built-in help instead._", "fallback")
    except Exception:  # noqa: BLE001  - never break the page because of the chatbot
        return BotReply(kb.GENERAL_FALLBACK, "fallback")
    if not text:
        return BotReply(kb.GENERAL_FALLBACK, "fallback")
    return BotReply(_scrub(text), "ai", used_ai=True)
