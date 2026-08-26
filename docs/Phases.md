# Phases.md — Build Plan

**Status:** Draft v1
**Companion docs:** PRD.md, Architecture.md, Rules.md
**Last updated:** 2026-08-26

Rule: each phase must run and demo standalone before next starts. No phase depends on unfinished work from a later phase.

---

## Phase 0 — Environment & Skeleton
**Goal:** empty but running system, air-gap proven from day one.

- Repo scaffold per Architecture.md §5 folder structure
- Docker Compose skeleton (backend, frontend, sandbox stub, no models yet)
- `config/model_registry.yaml`, `tool_permissions.yaml`, `network_policy.yaml` — empty/stub versions
- Network egress monitor (`egress_monitor.py`) running, iptables deny-all-outbound in place
- FastAPI hello-world endpoint, React/Streamlit hello-world page, talking to each other locally
- CI check: egress monitor test proves a deliberate test outbound call gets flagged

**Exit criteria:** app boots, UI loads, zero-egress monitor visibly running and logging. No AI yet.

---

## Phase 1 — Single Model, Basic Chat
**Goal:** one open-weight model answering questions locally, no agent behavior yet.

- Pull one reasoning model (e.g. smaller Llama/Qwen class) via `download_models.sh`, one-time setup script only
- vLLM or Ollama serving it locally
- Basic chat endpoint: user message → model → response, no tools, no memory
- Audit logger capturing every call (model, timestamp, task ID)
- Frontend: simple chat panel

**Exit criteria:** working local chatbot, fully offline, logged.

---

## Phase 2 — Model Registry & Router
**Goal:** multi-model backend, task-based auto-selection (core PRD requirement).

- Fill out `model_registry.yaml` with ≥2 models (reasoning + coder)
- Build `model_router.py`: task classification → registry lookup → dispatch
- Fallback chain logic (per Architecture.md §4)
- Task trace UI panel showing which model handled which request
- Add coder model, test router picks it for code-flavored prompts vs reasoning model for general Q&A

**Exit criteria:** demo shows router picking different models for 2 distinct task types — first demo acceptance criterion (PRD §6.1) met.

---

## Phase 3 — Tool Layer (non-agentic first)
**Goal:** wire up individual tools as callable functions, tested standalone before agent loop uses them.

- `file_io.py` — scoped read/write, permission-checked against `tool_permissions.yaml`
- `code_sandbox.py` — Docker container, `--network none`, resource caps, stdout/stderr/exit code capture
- `spreadsheet.py` — read/write xlsx via openpyxl
- Each tool has direct API endpoint for manual testing (not yet agent-invoked)
- Error handling per Rules.md §3 implemented and tested per tool

**Exit criteria:** each tool callable and verified in isolation, sandbox network-isolation test passes.

---

## Phase 4 — Agent Orchestrator (planning + execution loop)
**Goal:** actual agent behavior — multi-step plan, tool calls, iteration.

- `planner.py` — request → step plan (structured output from reasoning model)
- `executor.py` — step-by-step execution, calls router + tools, observes, replans on failure (bounded retries per Rules.md §3.1)
- `state.py` — task state persistence/checkpointing
- Human-in-loop confirmation gate before irreversible actions (Rules.md §4.3)
- Task trace UI extended to show full plan + step-by-step progress live

**Exit criteria:** agent can carry a 3+ step task end-to-end with at least one tool call per step, checkpoints correctly before irreversible action.

---

## Phase 5 — Deliverable Generation
**Goal:** real output files, not just chat text.

- `docx_writer.py` with approval-note template
- `pptx_writer.py`, `xlsx_writer.py`
- Wire deliverable generator into orchestrator's final step
- Calculation tasks show steps, not just final numbers (PRD §5.5)
- Coding task: sandbox-verified code + run log as downloadable output

**Exit criteria:** demo shows a coding task run and verified in sandbox (PRD §6.3) and a calc task with shown steps.

---

## Phase 6 — Multimodal (OCR + Vision)
**Goal:** scanned docs, drawings, photos understood and usable by agent.

- Add vision model to registry (`vision-7b` or similar)
- `ocr_pipeline.py` (PaddleOCR offline) for scanned PDFs/handwritten notes
- `drawing_reader.py` for P&ID/engineering-drawing-specific structuring
- Router extended to dispatch vision/OCR-tagged steps correctly
- Test with `demo_assets/sample_scanned_reports/` and `sample_pnid_drawings/`

**Exit criteria:** demo shows multimodal task — image/scan understanding with correct structured read-out (PRD §6.4).

---

## Phase 7 — Knowledge Base / RAG
**Goal:** ground answers in org's own manuals/SOPs/correspondence.

- `ingest.py` — batch/folder-watch ingestion of `demo_assets/sample_kb_docs/`
- `embed.py` + local vector store (Chroma/Qdrant)
- `hybrid_search.py` — vector + BM25 combine
- `doc_search.py` tool wired into agent, citations surfaced in output
- Empty-retrieval handling per Rules.md §3.5 (flag when no KB grounding used)

**Exit criteria:** agent answer correctly cites a source doc from local KB; ungrounded fallback clearly flagged when no match found.

---

## Phase 8 — End-to-End Flagship Demo Scenario
**Goal:** full PRD §6.2 scenario working unattended.

- Scanned inspection report → OCR → key findings extracted → KB-grounded context (if relevant SOP exists) → approval note drafted → `.docx` output → human-confirm checkpoint before "final"
- Full task trace visible start to finish
- Egress monitor shows zero calls across entire run

**Exit criteria:** this single flow, run live, is the centerpiece demo. Must work reliably, not just once.

---

## Phase 9 — Hardening & Demo Polish
**Goal:** stability, presentability, sovereignty proof packaging.

- Resource/timeout tuning across model calls and sandbox
- UI polish (EgressMonitorPanel, DeliverablePreview, error states shown cleanly)
- Full dependency audit — confirm nothing phones home anywhere in stack (Rules.md §1.8)
- Package exportable egress log/recording as demo evidence artifact
- Run through all PRD §6 acceptance criteria end-to-end as a rehearsal
- Fallback plan tested: smaller model swap-in via registry only, no code change, confirms extensibility claim

**Exit criteria:** all 5 PRD §6 demo acceptance criteria pass in one continuous session.

---

## Phase 10 (Post-Demo / Future) — Pilot Readiness
**Out of demo scope, listed for roadmap continuity only:**

- Multi-user auth/RBAC
- Kubernetes scaling if multi-user pilot needed
- Formal security accreditation process
- Fine-tuning pipeline for org-specific data
- Broader template library (approval notes, reports, correspondence types)

---

## Phase Dependency Summary

```
Phase 0 (skeleton + egress proof)
   → Phase 1 (single model chat)
      → Phase 2 (router, multi-model)
         → Phase 3 (tools, standalone)
            → Phase 4 (agent loop)
               → Phase 5 (deliverables)
               → Phase 6 (multimodal)
               → Phase 7 (KB/RAG)
                  → Phase 8 (flagship e2e demo)
                     → Phase 9 (hardening/polish)
                        → Phase 10 (post-demo, future)
```

Phases 5, 6, 7 can run in parallel once Phase 4 done — each depends on orchestrator existing, not on each other.
