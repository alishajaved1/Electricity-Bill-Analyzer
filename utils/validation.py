import re
from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
MAGIC = {"pdf": [b"%PDF"], "png": [b"\x89PNG"], "jpg": [b"\xff\xd8\xff"], "jpeg": [b"\xff\xd8\xff"]}


def valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match((email or "").strip()))


def validate_signup(name, email, pw, confirm) -> list[str]:
    errs = []
    if not (name or "").strip():
        errs.append("Full name is required.")
    if not (email or "").strip():
        errs.append("Email address is required.")
    elif not valid_email(email):
        errs.append("Please enter a valid email address (e.g. name@example.com).")
    if not pw:
        errs.append("Password is required.")
    elif len(pw) < 8:
        errs.append("Password must be at least 8 characters.")
    if pw and pw != confirm:
        errs.append("Passwords do not match.")
    return errs


def validate_upload(filename: str, data: bytes) -> str | None:
    """Return an error message, or None if the upload is acceptable."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return f"Unsupported file type '.{ext}'. Please upload a PDF, JPG, JPEG or PNG file."
    if len(data) == 0:
        return "The uploaded file is empty."
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        return f"File is too large ({len(data)/1024/1024:.1f} MB). Maximum size is {MAX_UPLOAD_MB} MB."
    if not any(data.startswith(m) for m in MAGIC[ext]):
        return "The file content does not match its extension. It may be corrupted or renamed."
    return None
