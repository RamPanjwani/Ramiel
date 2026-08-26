# Architecture.md — Sovereign On-Premise Agentic AI Workbench

**Status:** Draft v1
**Companion doc:** PRD.md
**Last updated:** 2026-08-26

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         WORKSTATION / GPU SERVER                     │
│                    (physically air-gapped, no outbound route)        │
│                                                                       │
│  ┌───────────────┐      ┌──────────────────────────────────────┐    │
│  │   Frontend     │◄────►│            API Gateway               │    │
│  │  (Web UI)      │      │        (FastAPI, local only)         │    │
│  └───────────────┘      └───────────────┬──────────────────────┘    │
│                                          │                            │
│                          ┌───────────────▼────────────────┐          │
│                          │        Agent Orchestrator       │          │
│                          │  (planner / executor / memory)  │          │
│                          └───┬──────────┬──────────┬───────┘          │
│                              │          │          │                  │
│                 ┌────────────▼──┐  ┌────▼─────┐  ┌─▼────────────┐    │
│                 │  Model Router  │  │  Tool     │  │  Knowledge   │    │
│                 │  (task→model)  │  │  Layer    │  │  Base (RAG)  │    │
│                 └───────┬────────┘  └────┬──────┘  └──────┬───────┘  │
│                         │                │                │          │
│           ┌─────────────▼───┐    ┌───────▼────────┐  ┌────▼──────┐  │
│           │  Model Serving   │    │  Sandbox Exec   │  │  Vector +  │ │
│           │  (vLLM/Ollama    │    │  File I/O       │  │  Keyword   │ │
│           │  multi-model)    │    │  Spreadsheet    │  │  Index     │ │
│           │  - reasoning LLM │    │  Doc Search      │  │  (local)   │ │
│           │  - coding LLM    │    └─────────────────┘  └────────────┘ │
│           │  - vision/OCR    │                                        │
│           └──────────────────┘                                        │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │   Deliverable Generator (.docx / .pptx / .xlsx / code files)   │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │   Audit Log + Network Egress Monitor (proof of zero calls out) │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

No component in this stack has an internet-facing dependency at runtime. All model weights, embeddings, indexes pre-loaded on local disk.

---

## 2. App Flow (Request Lifecycle)

1. **User submits request** via web UI (text, and/or uploaded file — PDF, image, spreadsheet).
2. **API Gateway** receives request, attaches session/task ID, logs it.
3. **Agent Orchestrator** parses intent, produces a step plan (single LLM call to reasoning model, structured output).
4. **Model Router** inspects each planned step, tags it with task type (`code`, `document`, `vision`, `calc`, `general_qa`), selects best-fit model from registry.
5. **Step execution loop**:
   - If step needs a tool → **Tool Layer** invoked (file I/O, sandbox exec, spreadsheet op, KB search).
   - If step needs OCR/vision → routed to vision model, output normalized to structured text, fed back into agent context.
   - If step needs reasoning/drafting → routed to reasoning/coding model per registry tag.
   - Result observed, orchestrator decides: next step, replan, or done.
   - Irreversible actions (file overwrite, final send) → checkpoint, wait for user confirm.
6. **Deliverable Generator** assembles final output file (.docx/.pptx/.xlsx/code) from agent's collected results.
7. **Audit Log** records full trace: models used, tools called, files touched, timestamps.
8. **Response returned** to UI with deliverable + summary + citations (if KB was used).
9. **Network Egress Monitor** runs continuously in background, independent of app — flags/blocks any attempted outbound call, visible in a live panel for demo/audit purposes.

---

## 3. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Model serving | **vLLM** (primary, GPU-efficient multi-model) or **Ollama** (simpler, lower-resource fallback) | Both run fully local, support concurrent model loading, OpenAI-compatible API surface simplifies orchestrator integration |
| Reasoning/document LLM | Open-weight, e.g. **Llama 3.x / Qwen2.5 / DeepSeek-class** (final pick per license + hardware) | Strong general reasoning, open license, various sizes for scaling to hardware |
| Coding LLM | Open-weight code-specialized model, e.g. **Qwen2.5-Coder / DeepSeek-Coder** class | Better code-gen/debug performance than general model |
| Vision/OCR model | Open-weight VLM, e.g. **Qwen2-VL / LLaVA-class**, + dedicated OCR engine (e.g. **PaddleOCR**, fully offline) | Handles drawings/photos; dedicated OCR engine more reliable for dense scanned text than VLM alone |
| Agent orchestration | Custom orchestrator (Python), inspired by ReAct-style loop; optionally built on **LangGraph** (self-hosted, no cloud calls) | Need full control over model routing + checkpointing; LangGraph gives state-graph structure without vendor lock |
| API layer | **FastAPI** | Async, fast, easy to wrap tool calls as endpoints, good typing |
| Frontend | **React + Vite**, or simple **Streamlit** for faster demo build | React for production-grade UI; Streamlit acceptable for demo-speed if timeline tight |
| Sandbox exec | **Docker container**, no network (`--network none`), CPU/mem capped, ephemeral per run | Standard, well-understood isolation; avoids heavier Firecracker/gVisor setup unless security review demands it later |
| Knowledge base / RAG | **Chroma** or **Qdrant** (self-hosted vector DB) + **BM25** hybrid via e.g. **Elasticsearch/OpenSearch** local instance, embeddings via open-weight embedding model (e.g. **BGE-M3**) | Fully local vector+keyword hybrid retrieval, no external embedding API |
| Document generation | **python-docx**, **python-pptx**, **openpyxl** | Standard, local, no cloud dependency |
| Spreadsheet tool ops | **openpyxl** / **pandas** | Read/write/formula support |
| Audit logging | **structlog** → local JSON log files, optionally **SQLite** for queryable trace store | Lightweight, no external log shipping |
| Network egress monitor | OS-level: **iptables** deny-all-outbound rule + **auditd**/**tcpdump** logging any attempted connection, surfaced in a small dashboard | Infra-level proof, not just app-level claim — this is the actual sovereignty evidence |
| Model registry | Simple **YAML/JSON config** + loader module | Declarative, so adding a model = new config entry, not code change |
| Container orchestration (optional, pilot-scale) | **Docker Compose** (demo/single-box), **Kubernetes** only if scaling to multi-user pilot later | Keep demo simple; K8s deferred |

---

## 4. Model Router — Design Notes

Router is config-driven, not hardcoded:

```yaml
# model_registry.yaml
models:
  - id: reasoning-70b
    engine: vllm
    path: /models/llama3-70b-instruct
    task_tags: [document, general_qa, planning]
    min_vram_gb: 80
    fallback: reasoning-8b

  - id: reasoning-8b
    engine: ollama
    path: /models/llama3-8b-instruct
    task_tags: [document, general_qa, planning]
    min_vram_gb: 12
    fallback: null

  - id: coder-32b
    engine: vllm
    path: /models/qwen2.5-coder-32b
    task_tags: [code]
    min_vram_gb: 40
    fallback: coder-7b

  - id: vision-7b
    engine: vllm
    path: /models/qwen2-vl-7b
    task_tags: [vision, drawing_read]
    min_vram_gb: 16
    fallback: null
```

Router logic: classify task tag (small classifier call or rule-based on request metadata) → match tag to registry entries → check available VRAM → select best fit → fallback chain if primary unavailable. Adding a model = new YAML entry + weight file on disk, no code change (per PRD extensibility requirement).

---

## 5. Folder & File Structure

```
sovereign-ai-workbench/
├── README.md
├── PRD.md
├── Architecture.md
├── docker-compose.yml
├── .env.example
│
├── config/
│   ├── model_registry.yaml
│   ├── tool_permissions.yaml        # scoped dirs, sandbox limits
│   └── network_policy.yaml          # egress deny rules reference
│
├── models/                          # local weight storage (gitignored, large)
│   ├── llama3-70b-instruct/
│   ├── qwen2.5-coder-32b/
│   ├── qwen2-vl-7b/
│   └── bge-m3-embeddings/
│
├── backend/
│   ├── main.py                      # FastAPI entrypoint
│   ├── api/
│   │   ├── routes_chat.py
│   │   ├── routes_upload.py
│   │   └── routes_admin.py          # logs, model registry status
│   │
│   ├── orchestrator/
│   │   ├── planner.py               # step-plan generation
│   │   ├── executor.py              # step execution loop
│   │   ├── state.py                 # task state / checkpointing
│   │   └── graph.py                 # LangGraph state graph (if used)
│   │
│   ├── router/
│   │   ├── model_router.py
│   │   └── registry_loader.py
│   │
│   ├── serving/
│   │   ├── vllm_client.py
│   │   ├── ollama_client.py
│   │   └── vision_client.py
│   │
│   ├── tools/
│   │   ├── file_io.py
│   │   ├── code_sandbox.py
│   │   ├── spreadsheet.py
│   │   ├── doc_search.py            # KB retrieval tool
│   │   └── tool_registry.py
│   │
│   ├── ocr_vision/
│   │   ├── ocr_pipeline.py          # PaddleOCR wrapper
│   │   └── drawing_reader.py        # P&ID / drawing specific parsing
│   │
│   ├── knowledge_base/
│   │   ├── ingest.py                # batch/folder-watch ingestion
│   │   ├── embed.py
│   │   ├── vector_store.py          # Chroma/Qdrant wrapper
│   │   └── hybrid_search.py         # vector + BM25 combine
│   │
│   ├── deliverables/
│   │   ├── docx_writer.py
│   │   ├── pptx_writer.py
│   │   ├── xlsx_writer.py
│   │   └── templates/
│   │       ├── approval_note.docx
│   │       └── report_template.pptx
│   │
│   ├── audit/
│   │   ├── logger.py
│   │   └── trace_store.py           # SQLite trace DB
│   │
│   └── security/
│       ├── egress_monitor.py        # tails auditd/tcpdump, flags calls
│       └── sandbox_policy.py
│
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── TaskTrace.tsx        # shows plan/tool calls live
│   │   │   ├── DeliverablePreview.tsx
│   │   │   └── EgressMonitorPanel.tsx  # live "0 external calls" proof
│   │   └── api/client.ts
│   └── vite.config.ts
│
├── sandbox/
│   ├── Dockerfile.sandbox           # isolated code-exec image
│   └── entrypoint.sh
│
├── data/
│   ├── kb_raw/                      # ingested manuals/SOPs (gitignored)
│   ├── kb_index/                    # vector + keyword index storage
│   └── uploads/                     # user-uploaded files, session-scoped
│
├── logs/
│   ├── audit/
│   └── egress/
│
├── demo_assets/
│   ├── sample_scanned_reports/
│   ├── sample_pnid_drawings/
│   └── sample_kb_docs/
│
├── scripts/
│   ├── setup_env.sh
│   ├── download_models.sh           # pulls open-weight models to /models
│   └── run_demo.sh
│
└── tests/
    ├── test_router.py
    ├── test_orchestrator.py
    ├── test_tools.py
    └── test_egress_monitor.py
```

---

## 6. Data Flow for Demo Scenarios (per PRD §6)

**Scenario 1 — scanned inspection report → approval note (.docx):**
`upload → ocr_pipeline.py → orchestrator.planner (reasoning model) → doc_search.py (KB grounding, optional) → orchestrator.executor drafts note → docx_writer.py → deliverable returned`

**Scenario 2 — coding task:**
`request → model_router selects coder model → code generated → code_sandbox.py executes in isolated container → result/error observed → orchestrator iterates if failed → final code + run log returned`

**Scenario 3 — multimodal drawing/P&ID read:**
`upload image → vision_client.py (vision model) → drawing_reader.py structures output → fed to reasoning model for summary/QA → response returned`

**Scenario 4 — zero-egress proof:**
`egress_monitor.py running full session → live panel in frontend (EgressMonitorPanel.tsx) shows outbound attempt count = 0 → log exportable as demo evidence`

---

## 7. Key Architectural Principles

- **Model-agnostic core**: orchestrator and tools never hardcode a model name — always go through router + registry.
- **Config over code**: new models, new tool permissions, new templates = config/file additions, not redeploys.
- **Air-gap enforced at infra layer**: iptables/network namespace deny-all-outbound, not just "the app doesn't call out." App-level discipline alone is not the sovereignty proof.
- **Sandbox isolation**: code execution always network-`none`, resource-capped, ephemeral container per run.
- **Everything logged**: every model call, tool call, file write traceable — needed for both debugging and the sovereignty/audit story.
- **Checkpoint before irreversible action**: orchestrator pauses for explicit user confirm before overwrite/send-type actions.

---

## 8. Open Items for Next Draft

- [ ] Confirm vLLM vs Ollama as primary serving engine (depends on final GPU spec)
- [ ] Decide LangGraph vs fully custom orchestrator loop
- [ ] Confirm Chroma vs Qdrant for vector store
- [ ] Define sandbox resource limits (CPU/mem/time per run)
- [ ] Define upload file size/type limits
