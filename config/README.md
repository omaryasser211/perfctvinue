# Configuration Guide

This application uses JSON configuration with environment-specific overrides.

## Files
- `config/config.json`: Main configuration.
- `config/config.local.json`: Optional local overrides (not committed).
- `config/config.example.json`: Example configuration you can copy to `config.local.json`.

## Environments
Set `APP_ENV` to one of: `development`, `test`, `production`.

## Sensitive Data
Do not store secrets in versioned files. Provide secrets via environment variables or `config.local.json` only.
- `OPENROUTER_API_KEY`: required for chatbot API.

## Options
- `server.host` (string) – bind address
- `server.port` (int) – port
- `server.debug` (bool) – Flask debug mode
- `openrouter.enabled` (bool) – enable outbound API calls
- `openrouter.model` (string) – model route
- `openrouter.http_referer` (string) – referer header
- `openrouter.title` (string) – title header
- `openrouter.api_key` (string|null) – API key (use env var instead)

## Example local overrides
```json
{
  "default": {
    "openrouter": {
      "api_key": "YOUR_REAL_KEY"
    }
  },
  "production": {
    "server": {
      "host": "0.0.0.0",
      "debug": false
    }
  }
}
```

## Validation
Configuration is validated on startup; incorrect types raise clear errors.