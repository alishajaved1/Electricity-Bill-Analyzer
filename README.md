# ⚡ Electricity Bill Analyzer

**Runtime:** Python 3.12 (3.11+ works). Dependencies are pinned in `requirements.txt`.

A Streamlit website that reads Pakistani electricity bills (KE, LESCO, IESCO) with Google Gemini, calculates insights in Python, tracks usage and lets you chat with **EnergyBot**.

> **Demo notes:** Login/Sign Up is a *demo* flow (accounts live only in session memory on the app server (Streamlit session state, not your browser); passwords are hashed in memory; no emails are sent). There is **no database** - bills and chat history are temporary and vanish on refresh/restart.

## Features
Landing page (hero, supported companies, animated **How It Works**, features, short privacy/accuracy note, floating **EnergyBot** guide) · demo auth · dashboard · bill upload (PDF/JPG/PNG) with Gemini extraction · review/edit before saving · Python-calculated insights · usage trends (Plotly) · bill history (view/remove/clear, CSV/JSON) · EnergyBot chat · reports (CSV, JSON, printable HTML) · settings.

## Project layout
```
app.py            entry point + routing      config.py   settings & secret loading
services/         gemini_service, extraction, calculations, energybot (+ energybot_kb knowledge base)
views/            one file per page          landing_sections.py, energybot_widget.py (landing page)
components/       styles, charts, SVG, UI    how_it_works.py + hiw/ (HTML/CSS/JS step navigator), icons, landing_styles
utils/            auth, validation, files, exports, session state
tests/            offline tests (no API key or network needed)
```

## New in this version: landing-page experience
**Animated "How It Works"** - a four-step navigator (Upload, Verify, Review, Ask) with a progress ring, step illustrations and a call-to-action on step 4.
- **Enter** advances exactly one step (1 -> 2 -> 3 -> 4). It is ignored while you type in any input, textarea or the EnergyBot dialog, when the section is not on screen, when a button/link has focus (the button handles Enter itself), and at step 4 (it never restarts).
- **Next / Previous** buttons and clickable step numbers do the same without a keyboard. **Restart** returns to step 1.
- Defined behaviour: the section starts at Step 1 when first scrolled into view; scrolling away and back keeps your current step; only **Restart** resets it. Streamlit reruns do not reset it (state lives in the browser component and is mirrored on the page).
- Respects `prefers-reduced-motion`; layout is responsive down to phone width.
- If the component cannot load, a static four-card version is shown instead.

**Landing copy** - kept short and written only from what the code does (see `services/energybot_kb.py`, the knowledge base used by EnergyBot). If you add or remove a feature, update that file.

**EnergyBot - Your Electricity Bill Analyzer Guide** - a floating "Ask EnergyBot" button (bottom-right) and opens a chat dialog.
- Answers common website questions from the built-in knowledge base **without any API call**; only unmatched questions go to Gemini (reusing the existing `GEMINI_API_KEY` setup), capped at 30 AI replies per session and 500 characters per message.
- Works with **no API key** (built-in help only) and degrades to a friendly message on API errors.
- Never receives bill data, refuses requests for keys/secrets/prompts locally, and scrubs the key from any reply.
- Bill-specific questions are answered with how to analyse a bill; the dashboard **AI Assistant** page remains the place that uses your extracted bill data.

## Tests (offline)
```powershell
python -m unittest discover -s tests          # EnergyBot knowledge base + service
python tests\smoke_landing_stub.py            # landing page renders (stubbed Streamlit)
python tests\smoke_widget_stub.py             # EnergyBot dialog logic (stubbed Streamlit)
node tests\test_hiw_logic.js                  # step/keyboard logic (optional, needs Node.js)
```
These do not replace opening the app in a browser and clicking through it (see the manual checklist below).

### Manual checklist
Landing page: nav links scroll; Explore How It Works scrolls to the section; step through 1-4 with Enter, Next, Previous and clicking numbers; type in the EnergyBot box and confirm Enter does not move the steps; Start Analyzing Your Bill / Start Analyzing open Sign Up; Meet EnergyBot opens the chat; resize to phone width; try with and without an API key.

## Setup on Windows (PowerShell + VS Code)
1. Install **Python 3.11 or newer** from python.org (tick "Add python.exe to PATH"). Check: `python --version`
2. Unzip, then open the folder in VS Code: `cd electricity-bill-analyzer; code .`
3. Create a virtual environment: `python -m venv .venv`
4. Activate it: `.\.venv\Scripts\Activate.ps1`
   (If blocked: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and retry.)
5. Install dependencies: `pip install -r requirements.txt`
6. Create your env file: `Copy-Item .env.example .env`
7. Get a free key at https://aistudio.google.com → *Get API key*, then edit `.env` and set `API_KEY=your_real_key` (`GEMINI_API_KEY` also works). Never share or commit this file.
8. Run: `streamlit run app.py` (opens http://localhost:8501)
9. **Test uploading:** Sign Up (demo) → *Analyze Bill* → upload a bill → *Analyze Bill* → review → *Save*.
10. **Test the assistant:** *AI Assistant* → ask "What is the due date?".

`MODEL_NAME` (or `GEMINI_MODEL`) in `.env` sets the model (default `gemini-3.5-flash-lite`). Use another model ID available to your key if you get a "model not available" error.

## Company logos and training bills
`assets/logos/` holds `iesco.png`, `ke.png`, `lesco.png` (shown on the landing page, dashboard company cards, beside the upload box and on results; a text badge is shown if a file is missing). `assets/training_bills/` holds five sample bills used by the **Training Bills** page. The AI is *not* trained on them; they are just practice inputs. `assets/hero_bill.jpg` is the landing-page photo - replace it with an image you are licensed to use before publishing.

## Competition mode (WTQ Build Track: Utility Bill Decoder)
Put the 10 test bills in `test/bills/` (file name = `bill_id`, e.g. `KESC_0002.png`); the two empty CSV templates are in `templates/`.
```powershell
python run_competition.py --bills test\bills --templates templates --out output
python tools\build_submission.py --output output [--demo demo\demo.mp4]
```
- Level 1: Gemini reads each bill image; `services/extraction.py` normalises it to the guide's exact schema (numbers as numbers, nulls when unreadable, credits negative, no personal identifiers); `competition/pipeline.py` writes one-line JSON.
- Level 2: `competition/facts.py` computes every number in Python (highest month, averages, summer vs winter, trend, forecast estimate, late surcharge, same-units estimate). Gemini only phrases the answer from the bill image, the Level 1 JSON and those facts. Failures are reported and exit non-zero, never silently faked.
- `--delay` (default 3 s) keeps you under the free-tier limit (15 requests/min); expect ~10 minutes for 10 bills + 120 answers.
- `build_submission.py` validates 10/120 rows, no empty cells, no keys, <= 15 MB, and builds `output/` + `source/` (+ `demo/`). `assets/training_bills/` and `.env` are never packaged.
- Tests: `python -m unittest discover -s tests` (includes `tests/test_facts.py`).

## AI usage
- **Models / APIs:** Google Gemini via the `google-genai` SDK, model `gemini-3.5-flash-lite` (configurable). Used for bill extraction (vision), EnergyBot chat, recommendations and phrasing Level 2 answers.
- **Services:** Google AI Studio (API key).
- **AI tools used to write the code:** Claude (Anthropic) assisted with writing and testing this project.
- All arithmetic (sums, percentages, per-unit cost, comparisons) is computed in Python, not by the model.
- Local OCR: none. Invoice/receipt extraction services (Azure prebuilt-invoice, Textract AnalyzeExpense, Mindee): none. Other LLMs: none.

## Push to GitHub (without secrets)
```powershell
git init
git add .
git status        # confirm .env is NOT listed
git commit -m "Electricity Bill Analyzer"
git branch -M main
git remote add origin https://github.com/<you>/electricity-bill-analyzer.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io → *New app* → pick your repo, branch `main`, main file `app.py`.
2. *Advanced settings → Secrets*, paste (see `.streamlit/secrets.toml.example`):
   ```toml
   GEMINI_API_KEY = "your_real_key"
   ```
3. Deploy. The key is read via `st.secrets`, falling back to environment variables locally.

## Troubleshooting
| Problem | Fix |
|---|---|
| `python` not recognised | Reinstall Python with *Add to PATH*, reopen PowerShell |
| Activation script blocked | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `pip install` fails | `python -m pip install --upgrade pip`, use Python 3.11-3.13 |
| "API key not configured" | `.env` must be in the project root, key without quotes/spaces; restart Streamlit |
| "key was rejected" | Re-create the key in AI Studio |
| "model not available" | Set `GEMINI_MODEL` to a model your key can use |
| Quota / rate-limit message | Wait a minute (free tier is limited) |
| Poor extraction | Use a flat, well-lit, full-page image; check/edit values in the review step |
| OCR | No local OCR is used: extraction relies on Gemini vision (PDF/image). Missing fields stay "Not available" |
| Deploy: ModuleNotFoundError | Make sure `requirements.txt` is committed |

## Notes on accuracy
All sums, percentages and per-unit costs are computed in Python from extracted values and shown with the formula used. Missing or unreadable fields remain empty - nothing is invented. Always verify extracted values against the original bill.

## Privacy model (accurate summary)
- No database; nothing is saved permanently by the app. Saved bills, drafts and chat live in **Streamlit session state**, i.e. in the app server's memory for your session (not in the browser), and disappear on refresh or restart.
- Pressing **Analyze Bill** sends your file to Google Gemini; dashboard EnergyBot sends extracted values (no names/addresses). The app cannot make claims about Google's own retention; check Google's terms.
- The landing-page EnergyBot never receives bill data; if it needs Gemini, only your typed question is sent.
- Keep `.env` private; it is excluded by `.gitignore` and from the release ZIP. `assets/training_bills/` is only read server-side by the Training Bills page and is not served as a public static directory (do not enable Streamlit static serving for `assets/`).
