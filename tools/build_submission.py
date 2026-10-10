"""Package source/ + output/ (+ optional demo/) into your-submission.zip and validate it.

  python tools/build_submission.py --output output [--demo demo/demo.mp4] [--zip your-submission.zip]
"""
import argparse
import csv
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "output", "demo", "test", ".pytest_cache", "training_bills"}  # private bills stay out
SKIP_FILES = {".env"}
KEY_RE = re.compile(r"AIza[0-9A-Za-z_\-]{30,}")
MAX_MB = 15


def check_csv(path: Path, cols, rows, fill_col):
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        data = list(r)
        if r.fieldnames != cols:
            raise SystemExit(f"{path.name}: columns must be {cols}")
    if len(data) != rows:
        raise SystemExit(f"{path.name}: expected {rows} rows, found {len(data)}")
    for i, row in enumerate(data, 2):
        if not (row[fill_col] or "").strip():
            raise SystemExit(f"{path.name}: empty '{fill_col}' on line {i}")
        if fill_col == "json":
            json.loads(row["json"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="output")
    ap.add_argument("--demo", default=None)
    ap.add_argument("--zip", default="your-submission.zip")
    ap.add_argument("--l1-rows", type=int, default=10)
    ap.add_argument("--l2-rows", type=int, default=120)
    a = ap.parse_args()
    out = Path(a.output)
    check_csv(out / "level1.csv", ["bill_id", "json"], a.l1_rows, "json")
    check_csv(out / "level2.csv", ["bill_id", "question_id", "question", "answer"], a.l2_rows, "answer")
    files = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if p.is_dir() or set(rel.parts) & SKIP_DIRS or p.name in SKIP_FILES or p.suffix in (".pyc", ".zip"):
            continue
        if p.suffix in (".py", ".md", ".txt", ".toml", ".example", ".gitignore") and KEY_RE.search(p.read_text(errors="ignore")):
            raise SystemExit(f"Possible real API key found in {rel} - remove it first.")
        files.append((p, Path("source") / rel))
    zp = Path(a.zip)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out / "level1.csv", "output/level1.csv")
        z.write(out / "level2.csv", "output/level2.csv")
        for src, arc in files:
            z.write(src, str(arc))
        if a.demo:
            d = Path(a.demo)
            if d.suffix.lower() not in (".mp4", ".mov", ".webm"):
                raise SystemExit("Demo must be .mp4, .mov or .webm")
            z.write(d, f"demo/demo{d.suffix.lower()}")
    mb = zp.stat().st_size / 1024 / 1024
    if mb > MAX_MB:
        raise SystemExit(f"{zp} is {mb:.1f} MB; the limit is {MAX_MB} MB (shrink the demo video).")
    with zipfile.ZipFile(zp) as z:
        names = z.namelist()
    assert "source/README.md" in names and "source/.env.example" in names, "README.md / .env.example missing from source/"
    print(f"OK: {zp} ({mb:.1f} MB, {len(names)} files). Top-level: {sorted({n.split('/')[0] for n in names})}")


if __name__ == "__main__":
    sys.exit(main())
