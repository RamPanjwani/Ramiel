#!/bin/bash
# Ramiel — Environment Setup Script
# Run once to initialize the development environment.

set -euo pipefail

echo "=== Ramiel Environment Setup ==="

# 1. Python venv
echo "[1/4] Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 2. Backend deps
echo "[2/4] Installing backend dependencies..."
pip install -r backend/requirements.txt

# 3. Frontend deps
echo "[3/4] Installing frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "pnpm-lock.yaml" ]; then
        pnpm install
    else
        npm install
    fi
    cd ..
fi

# 4. Create data directories
echo "[4/4] Creating data directories..."
mkdir -p data/kb_raw data/kb_index data/uploads
mkdir -p logs/audit logs/egress
mkdir -p models

echo ""
echo "=== Setup complete ==="
echo "Activate the venv: source .venv/bin/activate"
echo "Run backend: uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
echo "Run frontend: cd frontend && npm run dev"
