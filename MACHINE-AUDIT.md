# Machine Self-Sufficiency Audit (2026-06-16)

## Self-sufficient on this box? -> With caveats

## Issues found
- **Git:** OK. Repo with `origin` (github.com/violentlydelightful/command-center). On `main`, clean, in sync with `origin/main`. Backed up.
- **Mac dependency:** None found. No `/Users/` paths, no launchd/osascript/pbcopy/~Library references. Plain Flask app, cross-platform.
- **Secrets/auth:** No real secret files in repo. `.env.example` is a placeholder template (OpenAI, OpenWeather, NewsAPI, Alpha Vantage, SECRET_KEY) with no real values. App loads via `python-dotenv` `load_dotenv()` reading a local `.env`. This project does NOT use 1Password — Brad must create a real `.env` on this box. No Mac-only secret file dependency (the `.env` would be created fresh here).
- **Runnability:** `requirements.txt` present but no `venv`/`.venv` (MISSING). Needs a venv + `pip install -r requirements.txt`.

## Fixed this pass
- None needed.

## Outstanding (needs Brad)
- Create a venv and `pip install -r requirements.txt`.
- `cp .env.example .env` and fill in real API keys (OpenAI, OpenWeather, NewsAPI, Alpha Vantage, SECRET_KEY). These are not in git anywhere, so retrieve the values from wherever they're stored (1Password / provider dashboards) — they are not recoverable from this repo.
