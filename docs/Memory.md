# Memory.md — Live Progress Tracker

**Purpose:** running state of build. Update after every work session. AI/human reads this FIRST before touching code — don't re-read whole repo, don't guess state.

**Last updated:** 2026-08-26 (Phase 1 complete)

---

## Current Phase
**Phase 1 — Single Model, Basic Chat** (COMPLETE ✅) -> Next: **Phase 2 — Model Registry & Router**

See Phases.md for phase definitions and exit criteria.

---

## Status Snapshot

| Field | Value |
|---|---|
| Current phase | Phase 1 (Complete) |
| File/module in progress | none (Phase 1 done) |
| Last completed file | `backend/api/routes_chat.py`, `backend/serving/vllm_client.py`, `tests/test_chat_endpoint.py` |
| Blocked on | nothing |
| Next action | Phase 2 — Multi-model registry loader, task tag router & fallback chain |

---

## Completed ✅
- `config/model_registry.yaml` — Declarative model definitions, task tags, VRAM, and fallback chains.
- `config/tool_permissions.yaml` — Scoped filesystem paths and sandbox resource limits.
- `config/network_policy.yaml` — Loopback-only air-gap policy and egress monitor settings.
- `backend/main.py` — FastAPI application entrypoint with lifespan managing EgressMonitor & logging setup.
- `backend/api/routes_chat.py` — Phase 1 chat endpoint dispatching to local vLLM/Ollama model serving with offline fallback guidance and trace logging.
- `backend/api/routes_upload.py` — File upload ingestion endpoint stub.
- `backend/api/routes_admin.py` — System health, model roster, live egress telemetry, and execution trace retrieval endpoints.
- `backend/audit/logger.py` — Structlog configuration with JSON/console pipelines and local log file output.
- `backend/audit/trace_store.py` — SQLite database engine for persisting and querying execution traces, prompts, responses, and latency.
- `backend/serving/vllm_client.py` — Local vLLM client connecting over loopback HTTP with OpenAI-compatible API.
- `backend/serving/ollama_client.py` — Local Ollama client connecting over loopback HTTP with `/api/chat` format.
- `backend/security/egress_monitor.py` — Real-time OS socket watcher and violation logger.
- `backend/security/sandbox_policy.py` — Resource policy and network-none constraint loader.
- `backend/orchestrator/*` — Stubs for Planner, Executor, TaskState, and LangGraph machine.
- `backend/router/*` — Stubs for ModelRouter and RegistryLoader.
- `backend/tools/*` — Stubs for ScopedFileIO, CodeSandbox, SpreadsheetTool, DocSearchTool, ToolRegistry.
- `backend/ocr_vision/*` — Stubs for OCRPipeline and DrawingReader.
- `backend/knowledge_base/*` — Stubs for DocumentIngestor, Embedder, VectorStore, HybridSearch.
- `backend/deliverables/*` — Stubs for DocxWriter, PptxWriter, XlsxWriter.
- `sandbox/Dockerfile.sandbox` + `sandbox/entrypoint.sh` — Minimal offline sandbox container image.
- `scripts/setup_env.sh`, `scripts/download_models.sh`, `scripts/run_demo.sh` — Setup scripts with Ollama and HuggingFace download commands.
- `docker-compose.yml` + `Dockerfile.backend` + `frontend/Dockerfile.frontend` — Compose stack.
- `frontend/` — React + Vite + Tailwind v4 instrument panel UI with EgressMonitorPanel, ChatPanel, FileUpload, TaskTrace, and DeliverablePreview.
- `tests/test_egress_monitor.py` — 17 unit and integration tests passing for zero-egress proof.
- `tests/test_audit.py` — Unit tests for logger and SQLite trace store.
- `tests/test_serving.py` — Unit tests for vLLM & Ollama serving clients.
- `tests/test_chat_endpoint.py` — Integration tests for `/api/chat`, `/api/admin/traces`, and `/api/admin/health`.

---

## In Progress 🔧
_(none — Phase 1 completed)_

---

## Not Started (Phase 2 upcoming)
- [ ] Implement `backend/router/registry_loader.py` to parse and validate `config/model_registry.yaml`
- [ ] Implement `backend/router/model_router.py` with tag-based classification, VRAM estimation, and fallback chains
- [ ] Un-skip and implement `tests/test_router.py`
- [ ] Connect router to chat flow / orchestrator for multi-model dispatch
- [ ] Update frontend TaskTrace component with dynamic model routing info

---

## Decisions Log
_(record any decision that deviates from or finalizes something left open in PRD/Architecture/Rules — so it's not re-litigated or forgotten)_

| Date | Decision | Why | Doc affected |
|---|---|---|---|
| 2026-08-26 | SQLite chosen for local trace store (`backend/audit/trace_store.py`) | Zero external dependencies, fast queryable relational format, robust on-prem persistence | Architecture.md, Rules.md |
| 2026-08-26 | Added `python-multipart` to requirements | Required for FastAPI file upload support | backend/requirements.txt |
| 2026-08-26 | Frontend implemented using React + Vite + Tailwind v4 with full Instrument Panel design tokens | Design.md specifies a complete custom UI system (oscilloscope-style egress strip, dark palette, hairline borders) | Architecture.md, Design.md |
| 2026-08-26 | Mypy dev requirements added: `types-PyYAML`, `types-psutil` | Required for clean type checking of YAML loading and psutil network connection inspection | backend/requirements.txt |

---

## Known Issues / Tech Debt

- none yet

---

## Session Log
_(short entries, newest on top — what happened, what's next. Keeps context across chat switches without re-reading whole codebase)_

- **2026-08-26 (Phase 1 Complete)** — Implemented structured audit logger (structlog) and SQLite trace store (`TraceStore`). Implemented local model serving clients (`VLLMClient`, `OllamaClient`). Connected `/api/chat` with local model dispatch, audit trace logging, and offline fallback guidance. Added `/api/admin/traces`. Added comprehensive tests (`test_audit.py`, `test_serving.py`, `test_chat_endpoint.py`) — all 28 tests passing. Mypy and ruff clean. Next: Phase 2 (Model Registry & Router).
- **2026-08-26 (Phase 0 Complete)** — Git initialized. Full monorepo scaffolding created: config YAMLs, FastAPI backend with egress monitor and all module stubs, React+Vite+Tailwind frontend with instrument panel design tokens, sandbox container, test suite (17 passed), Docker Compose, and helper scripts. All type checks (mypy) and lints (ruff) green.
- **2026-08-26** — PRD.md, Architecture.md, Rules.md, Phases.md finalized. Memory.md scaffolded.

---

## How to Update This File

- After finishing a file/module: move it to ✅ Completed, one line, what it does.
- Before pausing mid-file: update 🔧 In Progress with exact state + what's left.
- Any deviation from PRD/Architecture/Rules: log in Decisions Log immediately, don't rely on memory of the conversation.
- Every session: add one line to Session Log before ending.
- Never delete old entries — this file is the audit trail of the build itself.
