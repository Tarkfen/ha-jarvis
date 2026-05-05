#!/bin/sh

# Read add-on options from /data/options.json (standard HA add-on location)
ANTHROPIC_API_KEY=$(python3 -c "import json; print(json.load(open('/data/options.json'))['anthropic_api_key'])")

if [ -z "${ANTHROPIC_API_KEY}" ]; then
    echo "ERROR: anthropic_api_key is not set — configure it in the add-on options."
    exit 1
fi

# SUPERVISOR_TOKEN is injected by HA and works as a Bearer token for the REST API
export HA_URL="http://supervisor/core"
export HA_TOKEN="${SUPERVISOR_TOKEN}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
export JARVIS_HOST="0.0.0.0"
export JARVIS_PORT="8000"

echo "Starting Jarvis on port 8000..."
cd /app
exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
