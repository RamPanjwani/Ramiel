# Memory.md — Live Progress Tracker

**Purpose:** running state of build. Update after every work session. AI/human reads this FIRST before touching code — don't re-read whole repo, don't guess state.

**Last updated:** 2026-08-26 (Phase 0 complete)

---

## Current Phase
**Phase 0 — Environment & Skeleton** (COMPLETE ✅) -> Next: **Phase 1 — Single Model, Basic Chat**

See Phases.md for phase definitions and exit criteria.

---

## Status Snapshot

| Field | Value |
|---|---|
| Current phase | Phase 0 (Complete) |
| File/module in progress | none (Phase 0 done) |
| Last completed file | `frontend/src/App.tsx`, `tests/test_egress_monitor.py` |
| Blocked on | nothing |
| Next action | Phase 1 — Download & wire single model serving (vLLM/Ollama) |

---

## Completed ✅
- `config/model_registry.yaml` — Declarative model definitions, task tags, VRAM, and fallback chains.
- `config/tool_permissions.yaml` — Scoped filesystem paths and sandbox resource limits.
- `config/network_policy.yaml` — Loopback-only air-gap policy and egress monitor settings.
- `backend/main.py` — FastAPI application entrypoint with lifespan managing EgressMonitor.
- `backend/api/routes_chat.py` — Chat endpoint with typed Pydantic models.
- `backend/api/routes_upload.py` — File upload ingestion endpoint stub.
- `backend/api/routes_admin.py` — System health, model roster, and live egress telemetry endpoints.
- `backend/security/egress_monitor.py` — Real-time OS socket watcher and violation logger.
- `backend/security/sandbox_policy.py` — Resource policy and network-none constraint loader.
- `backend/orchestrator/*` — Stubs for Planner, Executor, TaskState, and LangGraph machine.
- `backend/router/*` — Stubs for ModelRouter and RegistryLoader.
- `backend/serving/*` — Stubs for VLLMClient, OllamaClient, and VisionClient.
- `backend/tools/*` — Stubs for ScopedFileIO, CodeSandbox, SpreadsheetTool, DocSearchTool, ToolRegistry.
- `backend/ocr_vision/*` — Stubs for OCRPipeline and DrawingReader.
- `backend/knowledge_base/*` — Stubs for DocumentIngestor, Embedder, VectorStore, HybridSearch.
- `backend/deliverables/*` — Stubs for DocxWriter, PptxWriter, XlsxWriter.
- `backend/audit/*` — Stubs for Logger (structlog) and TraceStore (SQLite).
- `sandbox/Dockerfile.sandbox` + `sandbox/entrypoint.sh` — Minimal offline sandbox container image.
- `scripts/setup_env.sh`, `scripts/download_models.sh`, `scripts/run_demo.sh` — Environment and demo runner scripts.
- `docker-compose.yml` + `Dockerfile.backend` + `frontend/Dockerfile.frontend` — Compose stack.
- `frontend/` — React + Vite + Tailwind v4 instrument panel UI with EgressMonitorPanel, ChatPanel, FileUpload, TaskTrace, and DeliverablePreview.
- `tests/test_egress_monitor.py` — 17 unit and integration tests passing for zero-egress proof.

---

## In Progress 🔧
_(none — Phase 0 completed)_

---

## Not Started (Phase 1 upcoming)
- [ ] `./scripts/download_models.sh` implementation for single reasoning model
- [ ] `backend/serving/vllm_client.py` and/or `backend/serving/ollama_client.py` implementation
- [ ] Connect `backend/api/routes_chat.py` to local model serving
- [ ] Connect `backend/audit/logger.py` structured logging to chat flow
- [ ] Verify basic chat responses in frontend ChatPanel

---

## Decisions Log
_(record any decision that deviates from or finalizes something left open in PRD/Architecture/Rules — so it's not re-litigated or forgotten)_

| Date | Decision | Why | Doc affected |
|---|---|---|---|
| 2026-08-26 | Frontend implemented using React + Vite + Tailwind v4 with full Instrument Panel design tokens | Design.md specifies a complete custom UI system (oscilloscope-style egress strip, dark palette, hairline borders) | Architecture.md, Design.md |
| 2026-08-26 | Mypy dev requirements added: `types-PyYAML`, `types-psutil` | Required for clean type checking of YAML loading and psutil network connection inspection | backend/requirements.txt |

---

## Known Issues / Tech Debt

- none yet

---

## Session Log
_(short entries, newest on top — what happened, what's next. Keeps context across chat switches without re-reading whole codebase)_

- **2026-08-26 (Phase 0 Complete)** — Git initialized. Full monorepo scaffolding created: config YAMLs, FastAPI backend with egress monitor and all module stubs, React+Vite+Tailwind frontend with instrument panel design tokens, sandbox container, test suite (17 passed), Docker Compose, and helper scripts. All type checks (mypy) and lints (ruff) green. Next: Phase 1 (Single model, basic chat).
- **2026-08-26** — PRD.md, Architecture.md, Rules.md, Phases.md finalized. Memory.md scaffolded.

---

## How to Update This File

- After finishing a file/module: move it to ✅ Completed, one line, what it does.
- Before pausing mid-file: update 🔧 In Progress with exact state + what's left.
- Any deviation from PRD/Architecture/Rules: log in Decisions Log immediately, don't rely on memory of the conversation.
- Every session: add one line to Session Log before ending.
- Never delete old entries — this file is the audit trail of the build itself.
