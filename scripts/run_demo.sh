#!/bin/bash
# Ramiel — Flagship Scenario & System Demo Runner
# Executes all 5 PRD acceptance criteria scenarios in sequence completely offline.

set -euo pipefail

echo "========================================================"
echo "    RAMIEL — Sovereign Air-Gapped AI Engineering Workbench"
echo "========================================================"
echo ""

echo "[1/5] Scenario 1: Model Auto-Selection & Task Routing"
echo "      Testing automatic classification and fallback chains..."
pytest tests/test_router.py -q

echo ""
echo "[2/5] Scenario 2: Standalone Tool Layer & Sandbox Isolation"
echo "      Executing ScopedFileIO, CodeSandbox (--network none), and SpreadsheetTool..."
pytest tests/test_tools.py -q

echo ""
echo "[3/5] Scenario 3: Agent Orchestration & Checkpoint Gates"
echo "      Testing Planner, Executor ReAct loop, and Human Confirmation Gates..."
pytest tests/test_orchestrator.py -q

echo ""
echo "[4/5] Scenario 4: Multimodal (OCR + Drawing Parser) & Knowledge Base"
echo "      Extracting P&ID equipment tags and running Hybrid RAG queries..."
pytest tests/test_vision.py tests/test_knowledge_base.py -q

echo ""
echo "[5/5] Scenario 5: End-to-End Flagship Overhaul Scenario & Zero-Egress Proof"
echo "      Generating Tri-Format Deliverables (.docx, .pptx, .xlsx) with 0 network leaks..."
pytest tests/test_e2e_scenario.py tests/test_egress_monitor.py -q

echo ""
echo "========================================================"
echo "    ALL 5 SCENARIOS VERIFIED GREEN — ZERO NETWORK EGRESS"
echo "========================================================"
