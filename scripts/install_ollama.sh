#!/bin/bash
# Install Ollama and pull the default vision model
# Supports macOS (Darwin) and Ubuntu (Linux)

set -e

MODEL="${1:-qwen2.5vl:7b}"

echo "=== Ollama installer ==="

# Check if already installed
if command -v ollama &>/dev/null; then
    echo "Ollama already installed: $(ollama --version)"
else
    OS="$(uname -s)"
    case "$OS" in
        Darwin)
            if command -v brew &>/dev/null; then
                echo "Installing Ollama via Homebrew..."
                brew install ollama
            else
                echo "Installing Ollama via curl..."
                curl -fsSL https://ollama.com/install.sh | sh
            fi
            ;;
        Linux)
            echo "Installing Ollama via curl..."
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        *)
            echo "Unsupported OS: $OS"
            exit 1
            ;;
    esac
fi

# Start ollama serve if not running
if ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
    echo "Starting Ollama server..."
    ollama serve &>/dev/null &
    sleep 3
fi

# Pull model
echo "Pulling model: $MODEL ..."
ollama pull "$MODEL"

echo ""
echo "Done! Ollama ready with model: $MODEL"
echo "Test: ollama run $MODEL"
