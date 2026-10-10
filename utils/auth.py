"""DEMO authentication using Streamlit session state only.

Accounts live in memory for the current browser session and vanish on refresh/restart.
Passwords are never stored in plaintext (salted PBKDF2). Replace this module with a real
identity provider + database for production use; keep the same function names.
"""
import hashlib
import hmac
import os

import streamlit as st

from utils.validation import valid_email, validate_signup


def _hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return salt.hex() + ":" + digest.hex()


def _verify(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split(":")
    candidate = _hash(password, bytes.fromhex(salt_hex)).split(":")[1]
    return hmac.compare_digest(candidate, digest_hex)


def _users() -> dict:
    return st.session_state.setdefault("users", {})


def register(name, email, password, confirm) -> tuple[bool, list[str]]:
    errs = validate_signup(name, email, password, confirm)
    if errs:
        return False, errs
    key = email.strip().lower()
    if key in _users():
        return False, ["An account with this email already exists in this demo session."]
    _users()[key] = {"name": name.strip(), "hash": _hash(password)}
    return True, []


def login(email, password) -> tuple[bool, str]:
    if not (email or "").strip() or not password:
        return False, "Email and password are required."
    if not valid_email(email):
        return False, "Please enter a valid email address."
    user = _users().get(email.strip().lower())
    if not user or not _verify(password, user["hash"]):
        return False, ("Incorrect email or password. Demo accounts only exist for the current "
                       "session, so please sign up first if you refreshed the page.")
    st.session_state.auth = {"email": email.strip().lower(), "name": user["name"]}
    return True, ""


def logout():
    for k in ("auth", "analysis_draft", "chat_history", "view_bill_id", "confirm_clear"):
        st.session_state.pop(k, None)


def is_authenticated() -> bool:
    return bool(st.session_state.get("auth"))


def current_name() -> str:
    return (st.session_state.get("auth") or {}).get("name", "User")
