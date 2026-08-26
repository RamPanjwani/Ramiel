#!/bin/bash
# Ramiel Sandbox Entrypoint
# Executes user code with timeout and captures output.
# This script runs inside a container with --network none.

set -euo pipefail

CODE_FILE="${1:-/home/sandbox/code.py}"
LANGUAGE="${2:-python}"
TIMEOUT="${3:-60}"

if [ ! -f "$CODE_FILE" ]; then
    echo "ERROR: Code file not found: $CODE_FILE" >&2
    exit 1
fi

case "$LANGUAGE" in
    python)
        timeout "$TIMEOUT" python3 "$CODE_FILE"
        ;;
    bash)
        timeout "$TIMEOUT" bash "$CODE_FILE"
        ;;
    *)
        echo "ERROR: Unsupported language: $LANGUAGE" >&2
        exit 1
        ;;
esac
