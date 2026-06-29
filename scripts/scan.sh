#!/bin/bash
# Wrapper: creates/activates venv, installs deps, runs scan.py
# Usage: ./scripts/scan.sh --kategorie mlecne-vyrobky foto1.jpg foto2.jpg

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv..."
    python3 -m venv "$VENV_DIR"
fi

# Activate
source "$VENV_DIR/bin/activate"

# Install deps if needed
if ! python -c "import ollama" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install --quiet ollama pyyaml
fi

# Run from project root
cd "$PROJECT_DIR"
python scripts/scan.py "$@"
