# Halls Booking App

A simple Flask application for booking halls with an accessible chatbot modal integrated via OpenRouter.

## Project Setup
- Requirements:
  - `Python` 3.11+
  - `pip` (bundled with Python)
  - Windows PowerShell
- Install Python dependencies:
  - `python -m venv .venv`
  - `.venv\Scripts\Activate.ps1`
  - `pip install -r requirements.txt`
- Configuration:
  - Set environment: `APP_ENV` (e.g., `development`, `production`)
  - Set OpenRouter key: `OPENROUTER_API_KEY`
  - Optional local overrides file: `config\config.local.json`

## Running the Project
- Development server:
  - `.venv\Scripts\Activate.ps1`
  - `$env:APP_ENV = 'development'`
  - `python app.py`
  - Open `http://127.0.0.1:5000/`
- Production configuration:
  - Set `APP_ENV` to `production` and configure `config\config.json`:
    - `server.host`: `0.0.0.0`
    - `server.debug`: `false`
  - Use a production WSGI server (e.g., `gunicorn`) if deploying beyond local development.

## Testing
- Environment checks:
  - Verify key is loaded: `Get-ChildItem Env:OPENROUTER_API_KEY`
  - Verify environment: `Get-ChildItem Env:APP_ENV`
- API smoke test:
  - `.venv\Scripts\Activate.ps1`
  - `$body = '{"messages":[{"role":"system","content":"اختبار"},{"role":"user","content":"مرحباً"}]}'`
  - `Invoke-RestMethod -Uri http://127.0.0.1:5000/api/chat -Method POST -ContentType 'application/json' -Body $body`
- Linting (optional):
  - No linter configured. You may add `ruff` or `flake8`.

## Environment Variables
- `OPENROUTER_API_KEY`: required to call the OpenRouter API.
- `APP_ENV`: selects config environment (`development` default).

## Configuration Files
- `config\config.json`: base + environment sections.
- `config\config.local.json`: optional local overrides (not committed).
- `config\config.example.json`: copy to `config.local.json` to start.

## Security Notes
- Do not commit secrets. Prefer environment variables.
- The app reads `OPENROUTER_API_KEY` from environment first, then local config if provided.