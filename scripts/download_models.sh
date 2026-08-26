#!/bin/bash
# Ramiel — Model Download Script
# ONE-TIME network access allowed per Rules.md §2.3.
# This is the ONLY script permitted to access the internet.
# Runtime application code must NEVER invoke this script.

set -euo pipefail

echo "=== Ramiel Model Downloader ==="
echo "WARNING: This script requires network access (one-time only)."
echo ""

MODEL_DIR="${MODEL_DIR:-./models}"
mkdir -p "$MODEL_DIR"

echo "TODO: Add model download commands here."
echo "  Example targets (per model_registry.yaml):"
echo "    - llama3-70b-instruct  (reasoning primary)"
echo "    - llama3-8b-instruct   (reasoning fallback)"
echo "    - qwen2.5-coder-32b    (coder primary)"
echo "    - qwen2.5-coder-7b     (coder fallback)"
echo "    - qwen2-vl-7b          (vision primary)"
echo "    - bge-m3                (embeddings)"
echo ""
echo "Download tools: huggingface-cli, ollama pull, or manual."
echo "After download, no further network access is needed."
