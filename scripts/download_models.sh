#!/bin/bash
# Ramiel — Model Download Script
# ONE-TIME network access allowed per Rules.md §2.3.
# This is the ONLY script permitted to access the internet.
# Runtime application code must NEVER invoke this script.

set -euo pipefail

echo "================================================================"
echo "          Ramiel Model Downloader (One-Time Setup)              "
echo "================================================================"
echo "NOTICE: Network egress is allowed ONLY for this one-time step."
echo "All model weights will be saved to ./models/ (gitignored)."
echo ""

MODEL_DIR="${MODEL_DIR:-./models}"
mkdir -p "$MODEL_DIR"

ENGINE="${1:-ollama}"

case "$ENGINE" in
    ollama)
        echo "[1/2] Pulling reasoning model via Ollama (llama3.2:3b or llama3.1:8b)..."
        ollama pull llama3.2 || ollama pull llama3.1:8b || echo "Ollama pull command exited."
        echo "[2/2] Pulling coding model via Ollama (qwen2.5-coder:7b)..."
        ollama pull qwen2.5-coder:7b || echo "Ollama pull command exited."
        echo "Models ready in local Ollama daemon library."
        ;;
    huggingface|hf)
        echo "Downloading open-weight checkpoints to $MODEL_DIR..."
        if ! command -v huggingface-cli &> /dev/null; then
            echo "huggingface-cli not found. Installing into virtualenv..."
            pip install "huggingface_hub[cli]"
        fi
        echo "Downloading Llama-3.1-8B-Instruct..."
        huggingface-cli download meta-llama/Llama-3.1-8B-Instruct --local-dir "$MODEL_DIR/llama3-8b-instruct" --local-dir-use-symlinks False
        echo "Downloading Qwen2.5-Coder-7B-Instruct..."
        huggingface-cli download Qwen/Qwen2.5-Coder-7B-Instruct --local-dir "$MODEL_DIR/qwen2.5-coder-7b" --local-dir-use-symlinks False
        ;;
    *)
        echo "Usage: ./scripts/download_models.sh [ollama | huggingface]"
        exit 1
        ;;
esac

echo ""
echo "================================================================"
echo " Model download complete. Disconnect network before continuing. "
echo "================================================================"
