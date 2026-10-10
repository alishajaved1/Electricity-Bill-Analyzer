"""Central configuration. Secrets are read from Streamlit Secrets or environment variables only."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # loads a local .env file (never committed)

APP_NAME = "Electricity Bill Analyzer"
APP_VERSION = "1.0.0"
BASE_DIR = Path(__file__).parent
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MAX_UPLOAD_MB = 5
ALLOWED_EXTENSIONS = ("pdf", "jpg", "jpeg", "png")
CURRENCY = "Rs."
PAGES = ["Dashboard", "Analyze Bill", "Training Bills", "Usage Trends", "Bill History", "AI Assistant", "Reports", "Settings"]
PAGE_ICONS = {"Dashboard": "▦", "Analyze Bill": "⌕", "Training Bills": "◈", "Usage Trends": "↗", "Bill History": "☰",
              "AI Assistant": "✦", "Reports": "▤", "Settings": "⚙"}


def get_secret(name: str, default=None):
    """Streamlit Secrets first (Cloud), then environment variables / .env (local)."""
    try:
        import streamlit as st
        value = st.secrets[name]
        if value:
            return str(value)
    except Exception:  # no secrets.toml locally, or key missing
        pass
    return os.getenv(name, default)


def get_api_key():
    key = get_secret("GEMINI_API_KEY") or get_secret("API_KEY")
    if not key or key.strip() in ("", "your_gemini_api_key_here", "your-api-key-here"):
        return None
    return key.strip()


def get_model_name() -> str:
    return get_secret("GEMINI_MODEL") or get_secret("MODEL_NAME") or DEFAULT_MODEL


def money(v, decimals=2) -> str:
    if v is None:
        return "Not available"
    try:
        return f"{CURRENCY} {float(v):,.{decimals}f}"
    except (TypeError, ValueError):
        return "Not available"


def kwh(v) -> str:
    if v is None:
        return "Not available"
    try:
        return f"{float(v):,.0f} kWh"
    except (TypeError, ValueError):
        return "Not available"

TRAINING_DIR = BASE_DIR / "assets" / "training_bills"
LOGO_DIR = BASE_DIR / "assets" / "logos"


def get_provider() -> str:
    """MODEL_PROVIDER (competition-style config). Only Google Gemini is implemented."""
    return (get_secret("MODEL_PROVIDER") or "google").strip().lower()
