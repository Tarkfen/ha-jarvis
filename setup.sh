#!/bin/bash
set -e

echo "=== Jarvis Setup ==="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 is required. Download it at https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python $PYTHON_VERSION found."

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate
echo "Installing dependencies..."
pip install --quiet -r requirements.txt

# Copy env template
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "✓ Created .env file — edit it with your settings before starting Jarvis."
else
    echo "✓ .env already exists."
fi

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your HA URL, HA token, and Anthropic API key"
echo "  2. Run:  source .venv/bin/activate && python -m uvicorn backend.main:app --reload"
echo "  3. Open: http://localhost:8000"
echo ""
