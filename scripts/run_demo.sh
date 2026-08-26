#!/bin/bash
# Ramiel — Demo Scenario Runner
# Runs all 5 PRD acceptance criteria scenarios in sequence.
#
# Phase 0: stub — full scenarios wired in Phase 8+.

set -euo pipefail

echo "=== Ramiel Demo Runner ==="
echo ""
echo "Scenario 1: Model Auto-Selection ............. [Phase 2 — not yet]"
echo "Scenario 2: End-to-End Agentic Task .......... [Phase 8 — not yet]"
echo "Scenario 3: Coding Task + Sandbox ............ [Phase 4 — not yet]"
echo "Scenario 4: Multimodal Drawing Analysis ...... [Phase 6 — not yet]"
echo "Scenario 5: Zero-Egress Proof ................ [Phase 0 — partial]"
echo ""

# Phase 0: can at least verify backend is up and egress is clean
echo "--- Scenario 5 (partial): Checking backend health ---"
HEALTH=$(curl -s http://127.0.0.1:8000/health 2>/dev/null || echo '{"error":"backend not running"}')
echo "Backend: $HEALTH"

EGRESS=$(curl -s http://127.0.0.1:8000/api/admin/egress 2>/dev/null || echo '{"error":"backend not running"}')
echo "Egress:  $EGRESS"
echo ""
echo "=== Demo run complete ==="
