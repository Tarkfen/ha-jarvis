# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Jarvis — Home Automation AI Assistant

A Python FastAPI backend that bridges **Claude API** (with tool use) and **Home Assistant REST API**, with a browser-based chat UI featuring voice input/output.

## Architecture

```
Browser (frontend/) ←→ FastAPI (backend/) ←→ Claude API (tool use) ←→ Home Assistant REST API
```

- **backend/config.py** — Load and validate `.env` settings
- **backend/ha_client.py** — Async wrapper around HA REST API (httpx)
- **backend/tools.py** — Claude tool definitions (JSON schemas)
- **backend/tool_executor.py** — Routes Claude tool calls to HA API methods
- **backend/claude_client.py** — Agentic loop: message → tool calls → response
- **backend/main.py** — FastAPI app, routes `/api/chat` and `/api/health`, serves frontend
- **frontend/** — Single-page chat UI with voice (Web Speech API)

## Setup

```bash
bash setup.sh
# Edit .env with HA_URL, HA_TOKEN, ANTHROPIC_API_KEY
source .venv/bin/activate && python -m uvicorn backend.main:app --reload
# Open http://localhost:8000
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python -m uvicorn backend.main:app --reload --port 8000

# Check HA connection
curl http://localhost:8000/api/health
```

## Adding New Tools

1. Add the tool schema to `backend/tools.py` in `ALL_TOOLS`
2. Add the handler case in `backend/tool_executor.py` in `execute_tool()`
3. Add the HA API method to `backend/ha_client.py` if needed
