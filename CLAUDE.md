# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Jarvis — Home Automation AI Assistant

A Python FastAPI backend that bridges **Claude API** (with tool use) and **Home Assistant REST API**, with a browser-based chat UI featuring voice input/output.

## Architecture

```
Browser (jarvis/frontend/) ←→ FastAPI (jarvis/backend/) ←→ Claude API (tool use) ←→ Home Assistant REST API
```

- **jarvis/backend/config.py** — Load and validate `.env` settings
- **jarvis/backend/ha_client.py** — Async wrapper around HA REST API (httpx)
- **jarvis/backend/tools.py** — Claude tool definitions (JSON schemas)
- **jarvis/backend/tool_executor.py** — Routes Claude tool calls to HA API methods
- **jarvis/backend/claude_client.py** — Agentic loop: message → tool calls → response
- **jarvis/backend/main.py** — FastAPI app, routes `/api/chat` and `/api/health`, serves frontend
- **jarvis/frontend/** — Single-page chat UI with voice (Web Speech API)
- **jarvis/config.yaml** — HA add-on manifest
- **jarvis/Dockerfile** — Container definition (ARM64 + amd64)
- **jarvis/run.sh** — Add-on startup script (reads Supervisor token, starts uvicorn)
- **repository.yaml** — Identifies this repo as an HA add-on store

## Setup

```bash
cd jarvis
bash ../setup.sh
# Edit .env with HA_URL, HA_TOKEN, ANTHROPIC_API_KEY
source ../.venv/bin/activate && python -m uvicorn backend.main:app --reload
# Open http://localhost:8000
```

## Development

```bash
cd jarvis
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python -m uvicorn backend.main:app --reload --port 8000

# Check HA connection
curl http://localhost:8000/api/health
```

## Adding New Tools

1. Add the tool schema to `jarvis/backend/tools.py` in `ALL_TOOLS`
2. Add the handler case in `jarvis/backend/tool_executor.py` in `execute_tool()`
3. Add the HA API method to `jarvis/backend/ha_client.py` if needed
