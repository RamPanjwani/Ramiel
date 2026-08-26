# PRD: Sovereign On-Premise Agentic AI Workbench

**Status:** Draft v1
**Owner:** [fill in]
**Last updated:** 2026-08-26

---

## 1. Problem

Refineries, PSUs, defence-linked manufacturing, govt offices produce heavy volume of sensitive knowledge work — approval notes, board decks, engineering calcs, internal tool code, scanned drawings/inspection reports. Cloud AI (Claude, Codex etc) banned by policy since data confidential: P&IDs, financials, vendor talks, unreleased designs, correspondence.

Result: two bad paths.
1. Work done manually → productivity loss.
2. Staff paste confidential data into public tools anyway → policy violated, silent leak risk.

Open-weight reasoning models now good enough for real assistant. But no deployable system exists today industrial users can actually work with like Claude/Codex, fully air-gapped.

---

## 2. Goal

Build self-hosted, air-gapped AI workbench, runs entirely on org's own GPU server. Nothing leaves premises — ever, provably.

Core requirements:
- Multi-model backend, not locked to one model. Auto-picks right model per task (coding vs summarization vs vision differ).
- New open-weight models pluggable later without redesign.
- Real agent, not chatbot: plans multi-step work, calls local tools (file I/O, sandboxed code exec, spreadsheet ops, internal doc search), iterates till done.
- Multimodal: scanned PDFs, handwritten notes, engineering drawings, photos — on-device OCR + vision models.
- Real deliverables out: Word/PPT/Excel files, working code, calculations with shown steps — not just chat text.
- Grounds answers in org's own manuals/SOPs/correspondence via local knowledge base connector. No external calls.

---

## 3. Target Users

| User | Context | Needs |
|---|---|---|
| Plant/process engineer | Refinery, PSU | Summarize inspection reports, draft approval notes, read P&IDs |
| Design/manufacturing engineer | Defence-linked mfg | Engineering calcs with shown work, review drawings |
| Internal tools developer | Any org unit | Write/run code in sandbox, no cloud IDE assistants allowed |
| Admin/office staff | Govt office | Draft board presentations, correspondence, Excel work |
| IT/security officer | All orgs | Needs proof of zero external egress before approving deployment |

Common trait: works with confidential data, policy-barred from cloud AI, currently either doing manual work or covertly using banned tools.

---

## 4. Scope

### 4.1 In scope (v1 / demo-ready)
- Local multi-model serving backend (open-weight models only)
- Task-based model router (auto-selects model per request type)
- Model registry designed for pluggable addition of new models
- Agent orchestration loop: plan → tool call → observe → iterate → deliver
- Tool set: file read/write, sandboxed code execution, spreadsheet read/write, internal document search (RAG over local KB)
- On-device OCR + vision model pipeline for scanned docs/drawings/photos
- Document generation: .docx, .pptx, .xlsx output
- Local knowledge base connector (ingest manuals/SOPs/correspondence, index locally)
- Network isolation + visible proof-of-no-egress (logs / network monitor)

### 4.2 Out of scope (v1)
- Multi-user auth/RBAC hardening (single workstation demo scope)
- Fine-tuning / training pipeline
- Mobile client
- Cloud fallback of any kind (explicitly forbidden, not just unscoped)
- Formal accreditation / security certification (defence-grade cert is future work)

---

## 5. Key Features (detailed)

### 5.1 Multi-model backend + auto-routing
- Run ≥2 open-weight models concurrently (e.g., one reasoning/coding-strong model, one general/document model; vision model as 3rd if separate).
- Router classifies incoming task (coding / document / vision / calc / general) and dispatches to best-fit model.
- Model registry = config-driven (model path, context length, task-affinity tags, hardware footprint) so adding a model = registry entry, not code rewrite.
- Fallback: if preferred model unavailable/OOM, route to next-best per registry.

### 5.2 Agentic execution
- Planner breaks user request into steps.
- Executor calls tools per step, observes result, replans if needed (ReAct-style or similar loop).
- Task state persisted so long multi-step jobs survive restarts.
- Human-in-loop checkpoint before irreversible actions (e.g., overwriting a file, sending output) — user preference note: irreversible actions always get plain clear confirmation, no shorthand.

### 5.3 Tool layer
- File read/write (scoped to approved local directories)
- Sandboxed code execution (isolated container/VM, no network egress, resource limits)
- Spreadsheet ops (read/write xlsx, formulas)
- Internal document search (vector/keyword hybrid search over local KB index)
- Each tool call logged (what, when, which model invoked it)

### 5.4 Multimodal ingestion
- OCR pipeline for scanned PDFs, handwritten notes (on-device engine, e.g. open OCR models)
- Vision model for engineering drawings / P&ID interpretation, photographs
- Output of vision/OCR stage feeds back into agent context as structured text/findings

### 5.5 Deliverable generation
- Approval notes, reports → .docx
- Presentations → .pptx
- Calculations, data tables → .xlsx, steps shown not just final number
- Code → runnable files + sandbox execution log as proof

### 5.6 Local knowledge base
- Ingest org manuals/SOPs/correspondence (batch upload, local folder watch)
- Local embedding + index, fully on-prem
- Retrieval grounds agent answers, citations back to source doc

### 5.7 Sovereignty proof
- Network monitor/log visible during demo showing zero outbound calls across whole session
- Air-gap enforced at infra level (no outbound route exists, not just app-level block) — this is the actual security claim, treat as hard requirement not soft goal

---

## 6. Demo / Acceptance Criteria

Must demonstrate on single workstation/server, mid-range GPU (scale down to smaller open-weight model if 120B-class hardware unavailable):

1. **Model auto-selection** — show router picking different models for ≥2 distinct task types (e.g. coding task vs document summarization task), visible in logs.
2. **End-to-end agentic task** — feed scanned inspection report → agent extracts key findings → drafts approval note as .docx, unattended multi-step run.
3. **Coding task** — agent writes code, executes in sandbox, verifies result (e.g. test pass), shows output.
4. **Multimodal task** — image or scanned P&ID/drawing understanding, agent produces correct structured read-out.
5. **Zero-egress proof** — network monitor/logs shown live or as recording, confirming no external call across entire demo session.

Demo data: open-source models + publicly available sample docs (sample scanned PDFs, open-dataset P&IDs). No proprietary data required for demo.

---

## 7. Non-Functional Requirements

- **Air-gap**: hard infra-level network isolation, not app-level toggle.
- **Auditability**: every model call, tool call, file write logged with timestamp + actor.
- **Hardware flexibility**: must degrade gracefully to smaller model class on lesser GPU, without code changes (registry/config swap only).
- **Extensibility**: adding new open-weight model = config change, target <1 day integration effort.
- **Reliability**: agent loop must checkpoint/resume on long multi-step tasks.
- **Data residency**: all KB indexes, model weights, logs, generated files stay on local disk. No telemetry phone-home anywhere in stack (check every dependency, not just the LLM calls).

---

## 8. Risks / Open Questions

| Risk | Note |
|---|---|
| 120B-class hardware not available at venue | Mitigated by smaller-model fallback path — needs testing, not just stated |
| OCR/vision accuracy on poor-quality scans | Needs eval set of realistic degraded samples |
| Router misclassifying task → wrong model → bad output | Needs eval harness per task type before demo |
| Sandbox escape / code exec safety | Sandbox must be network-isolated + resource-capped regardless of code trust |
| "Some dependency phones home" undermining sovereignty claim | Full dependency audit needed, not just LLM API layer |
| Model licensing (open-weight ≠ always free for internal enterprise use) | Verify license terms per model in registry |

---

## 9. Success Metrics (post-demo / pilot)

- Task completion rate for real end-user requests without manual rescue
- Time saved vs manual baseline per task type (approval note drafting, drawing review, etc.)
- Zero confirmed external network calls in production audit logs
- Number of models addable to registry without core code changes (target: yes, always)
- User adoption vs continued manual workflow / shadow use of banned cloud tools (proxy for whether tool actually replaces the risky behavior)

---

## 10. Open Items for Next Draft

- [ ] Confirm target GPU spec(s) for demo vs pilot vs production
- [ ] Finalize initial model shortlist per task category
- [ ] Define sandbox tech (Docker/Firecracker/gVisor etc)
- [ ] Define KB ingestion format support list
- [ ] Define approval-note/report templates per target org type
