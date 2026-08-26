# Memory.md — Live Progress Tracker

**Purpose:** running state of build. Update after every work session. AI/human reads this FIRST before touching code — don't re-read whole repo, don't guess state.

**Last updated:** 2026-08-26 (Phase 7 complete)

---

## Current Phase
**Phase 7 — Knowledge Base / Hybrid RAG** (COMPLETE ✅) -> Next: **Phase 8 — End-to-End Flagship Scenario**

See Phases.md for phase definitions and exit criteria.

---

## Status Snapshot

| Field | Value |
|---|---|
| Current phase | Phase 7 (Complete) |
| File/module in progress | none (Phase 7 done) |
| Last completed file | `backend/knowledge_base/embed.py`, `backend/knowledge_base/vector_store.py`, `backend/knowledge_base/hybrid_search.py`, `backend/knowledge_base/ingest.py`, `backend/tools/doc_search.py`, `tests/test_knowledge_base.py` |
| Blocked on | nothing |
| Next action | Phase 8 — End-to-end integration demo assets, flagship engineering scenario verification script (`scripts/run_demo.sh`), and end-to-end integration test |

---

## Completed ✅
- `config/model_registry.yaml` — Declarative model definitions, task tags, VRAM, and fallback chains.
- `config/tool_permissions.yaml` — Scoped filesystem paths and sandbox resource limits.
- `config/network_policy.yaml` — Loopback-only air-gap policy and egress monitor settings.
- `backend/main.py` — FastAPI application entrypoint with lifespan managing EgressMonitor & logging setup.
- `backend/api/routes_chat.py` — Multi-model chat endpoint with auto-classification (code, doc, vision, calc, general_qa), router dispatch, fallback chain cascading, and trace logging.
- `backend/api/routes_upload.py` — File upload ingestion endpoint stub.
- `backend/api/routes_admin.py` — System health, model registry introspection, route preview simulation (`/api/admin/route`), and trace retrieval endpoints.
- `backend/router/registry_loader.py` — YAML parser and validator for model registry with duplicate and fallback validation.
- `backend/router/model_router.py` — Task classifier, tag matcher, fallback chain resolver, and model selector.
- `backend/audit/logger.py` — Structlog configuration with JSON/console pipelines and local log file output.
- `backend/audit/trace_store.py` — SQLite database engine for persisting and querying execution traces, prompts, responses, and latency.
- `backend/serving/vllm_client.py` — Local vLLM client connecting over loopback HTTP with OpenAI-compatible API.
- `backend/serving/ollama_client.py` — Local Ollama client connecting over loopback HTTP with `/api/chat` format.
- `backend/serving/vision_client.py` — Local vision-language model client for multimodal analysis over loopback HTTP.
- `backend/security/egress_monitor.py` — Real-time OS socket watcher and violation logger.
- `backend/security/sandbox_policy.py` — Resource policy and network-none constraint loader.
- `backend/tools/file_io.py` — Directory-scoped file reader, writer, and directory browser with path-traversal protection against `tool_permissions.yaml`.
- `backend/tools/code_sandbox.py` — Isolated code execution engine enforcing `--network none`, timeout, and output capture.
- `backend/tools/spreadsheet.py` — Excel spreadsheet reader, writer, and statistical calculation tool (`openpyxl` & `pandas`).
- `backend/tools/tool_registry.py` — Central discovery, registration, and invocation registry for agent tools with JSON schema serialization and deliverable/doc search tools.
- `backend/tools/doc_search.py` — Hybrid search tool exposing semantic and keyword retrieval to the orchestrator.
- `backend/orchestrator/state.py` — Task lifecycle state management, SQLite checkpoint snapshots, observation accumulation, and human confirmation gates.
- `backend/orchestrator/planner.py` — Structured multi-step plan generation with tool assignments and confirmation flags.
- `backend/orchestrator/executor.py` — ReAct execution loop coordinating model routing, tool dispatch, bounded replanning, and confirmation gates.
- `backend/orchestrator/graph.py` — State graph workflow execution and checkpoint resumption.
- `backend/deliverables/docx_writer.py` — Executive approval notes with memo headers, executive summary, findings, data tables, and formal sign-offs (`python-docx`).
- `backend/deliverables/pptx_writer.py` — Presentation decks with title slide, structured bullet slides, and summary slides (`python-pptx`).
- `backend/deliverables/xlsx_writer.py` — Multi-sheet styled calculation workbooks with header formatting and column auto-sizing (`openpyxl`).
- `backend/ocr_vision/ocr_pipeline.py` — Offline OCR text extraction using local models.
- `backend/ocr_vision/drawing_reader.py` — P&ID engineering drawing parser with ISA 5.1 tag extractor for valves, pumps, vessels, and instrumentation.
- `backend/knowledge_base/embed.py` — Local dense vector embedder with L2 normalization and offline deterministic hash projection.
- `backend/knowledge_base/vector_store.py` — Local vector store with SQLite persistence and exact cosine nearest-neighbor search.
- `backend/knowledge_base/hybrid_search.py` — Hybrid search engine fusing dense semantic embeddings with BM25 keyword matching.
- `backend/knowledge_base/ingest.py` — Document chunking with sliding window overlap and automatic embedding/indexing.
- `sandbox/Dockerfile.sandbox` + `sandbox/entrypoint.sh` — Minimal offline sandbox container image.
- `scripts/setup_env.sh`, `scripts/download_models.sh`, `scripts/run_demo.sh` — Setup scripts with Ollama and HuggingFace download commands.
- `docker-compose.yml` + `Dockerfile.backend` + `frontend/Dockerfile.frontend` — Compose stack.
- `frontend/` — React + Vite + Tailwind v4 instrument panel UI with EgressMonitorPanel, ChatPanel, FileUpload, TaskTrace (with live model roster & traces), and DeliverablePreview.
- `tests/test_egress_monitor.py` — 17 unit and integration tests passing for zero-egress proof.
- `tests/test_audit.py` — Unit tests for logger and SQLite trace store.
- `tests/test_serving.py` — Unit tests for vLLM & Ollama serving clients.
- `tests/test_chat_endpoint.py` — Integration tests for auto-routing (`code` -> `coder-primary`, `document` -> `reasoning-primary`), `/api/admin/route`, and trace logging.
- `tests/test_router.py` — Unit tests for task classification, registry validation, and fallback chains.
- `tests/test_tools.py` — Unit tests for file boundary validation, code sandbox execution & timeout, and spreadsheet operations.
- `tests/test_orchestrator.py` — Unit and integration tests for Planner, TaskState, Executor, confirmation gates, and OrchestrationGraph.
- `tests/test_deliverables.py` — Unit tests for Word documents, PowerPoint decks, and Excel workbooks.
- `tests/test_vision.py` — Unit tests for VisionClient, OCRPipeline, and DrawingReader.
- `tests/test_knowledge_base.py` — Unit tests for Embedder, VectorStore, HybridSearch, DocumentIngestor, and DocSearchTool.

---

## In Progress 🔧
_(none — Phase 7 completed)_

---

## Not Started (Phase 8 & 9 upcoming)
- [ ] Implement Phase 8 flagship scenario demo assets in `demo_assets/` (P&ID diagram, inspection report, technical manual)
- [ ] Connect full multi-step scenario into `scripts/run_demo.sh` and end-to-end integration test `tests/test_e2e_scenario.py`
- [ ] Phase 9 Hardening & Verification

---

## Decisions Log
_(record any decision that deviates from or finalizes something left open in PRD/Architecture/Rules — so it's not re-litigated or forgotten)_

| Date | Decision | Why | Doc affected |
|---|---|---|---|
| 2026-08-26 | Weighted rank fusion ($0.7 \times \text{dense} + 0.3 \times \text{BM25}$) in `backend/knowledge_base/hybrid_search.py` | Balances semantic understanding with exact technical identifier retrieval (tag numbers, ISA codes) | Architecture.md §7 |
| 2026-08-26 | ISA 5.1 regex extraction in `backend/ocr_vision/drawing_reader.py` | Fast offline extraction of valves, pumps, vessels, and instruments from technical drawings | Architecture.md §5 |
| 2026-08-26 | Added `python-docx` and `python-pptx` to backend dependencies | Required for generating Word approval notes and PowerPoint presentations | backend/requirements.txt |
| 2026-08-26 | SQLite checkpointing in `backend/orchestrator/state.py` | Allows full offline task pause, inspection, and human confirmation resumption | Architecture.md §6 |
| 2026-08-26 | Added `openpyxl`, `pandas`, `types-openpyxl`, `pandas-stubs` | Required for spreadsheet tool operations and formula/data evaluation | backend/requirements.txt |
| 2026-08-26 | Rule-based regex task classifier in `backend/router/model_router.py` | Fast, deterministic, zero-inference-overhead task classification across `code`, `vision`, `calc`, `document`, and `general_qa` | Architecture.md §4 |
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

- **2026-08-26 (Phase 7 Complete)** — Implemented Hybrid RAG / Knowledge Base: `Embedder` (dense vector embeddings with L2 normalization), `VectorStore` (SQLite persistence & cosine similarity nearest neighbors), `HybridSearch` (dense vector + BM25 keyword matching with weighted fusion), `DocumentIngestor` (sliding window text chunker & directory indexer), and `DocSearchTool` (registered in `ToolRegistry`). Added `test_knowledge_base.py` — all 72 tests passing across test suite. Mypy and ruff clean. Next: Phase 8 (Flagship Scenario).
- **2026-08-26 (Phase 6 Complete)** — Implemented `VisionClient` (OpenAI-compatible local multimodal VLM client), `OCRPipeline` (offline document OCR with fallback), and `DrawingReader` (ISA 5.1 P&ID equipment and instrument extractor). Added `test_vision.py` — all 65 tests passing across test suite. Mypy and ruff clean.
- **2026-08-26 (Phase 5 Complete)** — Implemented deliverables engine: `DocxWriter` (executive approval notes, memo blocks, tables, formal sign-offs), `PptxWriter` (slide decks with title, content, summary layouts), and `XlsxWriter` (styled multi-sheet calculation workbooks). Added `test_deliverables.py` — all 61 tests passing across test suite. Mypy and ruff clean.
- **2026-08-26 (Phase 4 Complete)** — Built `backend/orchestrator/state.py` (TaskState, SQLite checkpoints, confirmation gating), `backend/orchestrator/planner.py` (structured multi-step plan generation), `backend/orchestrator/executor.py` (ReAct loop, tool coordination, bounded replanning), and `backend/orchestrator/graph.py` (workflow state graph). Added complete unit & integration tests (`test_orchestrator.py`) — all 58 tests passing across test suite. Mypy and ruff clean.
- **2026-08-26 (Phase 3 Complete)** — Implemented standalone tool layer: `ScopedFileIO` (permission-checked against `tool_permissions.yaml`), `CodeSandbox` (`--network none` Docker + timeout management), `SpreadsheetTool` (`openpyxl` & `pandas` tabular inspection & stats), and `ToolRegistry` (tool registration, discovery, schema export, and dispatch). All 51 tests passing.
- **2026-08-26 (Phase 2 Complete)** — Built `backend/router/registry_loader.py` and `backend/router/model_router.py`. Implemented task classification (`code`, `document`, `vision`, `calc`, `general_qa`), declarative registry lookup, and fallback chains. Connected auto-routing to `/api/chat`, `/api/admin/models`, and added `/api/admin/route` preview endpoint. Updated frontend `TaskTrace.tsx` with live model roster and trace stream. Added comprehensive unit & integration tests (`test_router.py`, `test_chat_endpoint.py`) — 39 tests passing.
- **2026-08-26 (Phase 1 Complete)** — Implemented structured audit logger (structlog) and SQLite trace store (`TraceStore`). Implemented local model serving clients (`VLLMClient`, `OllamaClient`). Connected `/api/chat` with local model dispatch, audit trace logging, and offline fallback guidance. Added `/api/admin/traces`. Added comprehensive tests (`test_audit.py`, `test_serving.py`, `test_chat_endpoint.py`) — all 28 tests passing. Mypy and ruff clean.
- **2026-08-26 (Phase 0 Complete)** — Git initialized. Full monorepo scaffolding created: config YAMLs, FastAPI backend with egress monitor and all module stubs, React+Vite+Tailwind frontend with instrument panel design tokens, sandbox container, test suite (17 passed), Docker Compose, and helper scripts. All type checks (mypy) and lints (ruff) green.
- **2026-08-26** — PRD.md, Architecture.md, Rules.md, Phases.md finalized. Memory.md scaffolded.

---

## How to Update This File

- After finishing a file/module: move it to ✅ Completed, one line, what it does.
- Before pausing mid-file: update 🔧 In Progress with exact state + what's left.
- Any deviation from PRD/Architecture/Rules: log in Decisions Log immediately, don't rely on memory of the conversation.
- Every session: add one line to Session Log before ending.
- Never delete old entries — this file is the audit trail of the build itself.
