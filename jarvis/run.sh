#!/usr/bin/with-contenv bashio

# Read user-configured options
ANTHROPIC_API_KEY=$(bashio::config 'anthropic_api_key')

if bashio::var.is_empty "${ANTHROPIC_API_KEY}"; then
    bashio::log.fatal "anthropic_api_key is not set — configure it in the add-on options."
    exit 1
fi

# Inside an HA add-on, SUPERVISOR_TOKEN is a valid long-lived HA token
# and http://supervisor/core is the internal HA REST API endpoint.
export HA_URL="http://supervisor/core"
export HA_TOKEN="${SUPERVISOR_TOKEN}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
export JARVIS_HOST="0.0.0.0"
export JARVIS_PORT="8000"

bashio::log.info "Starting Jarvis on port 8000..."
cd /app
exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
