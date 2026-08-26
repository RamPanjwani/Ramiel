# Rules.md — Boundaries, Libraries, Error Handling

**Status:** Draft v1
**Companion docs:** PRD.md, Architecture.md
**Last updated:** 2026-08-26

Purpose: hard constraints for anyone (human or AI) writing code in this repo. Sovereignty claim only holds if these are followed without exception.

---

## 1. Absolute Boundaries (never violate)

1. **No network egress, ever, from any component.** No package may make an outbound HTTP call, DNS lookup, telemetry ping, license check, or update check at runtime. This includes "harmless" things like crash reporters, analytics SDKs, font CDNs, auto-updaters.
2. **No cloud API calls.** No OpenAI, Anthropic, Google, Azure, AWS SDKs — not even as a "fallback" or "dev convenience." If a library has an optional cloud mode, disable it explicitly in config, don't just "not use" it.
3. **No proprietary/closed-weight models.** Open-weight only, license-verified (see §4).
4. **No silent data leaves disk.** Uploaded files, KB content, logs, generated deliverables all stay under `data/` and `logs/`. No component writes outside the repo's data dirs without explicit user-approved export step.
5. **Sandbox exec always network-isolated.** `--network none` non-negotiable on code-exec containers. No exceptions for "just this one package install at runtime."
6. **No hardcoded model names in orchestrator/tool code.** Always go through model_router + registry (per Architecture.md §4). Hardcoding breaks extensibility requirement in PRD.
7. **Irreversible actions require explicit user confirmation.** File overwrite, external send, delete — agent must checkpoint and wait, never auto-proceed.
8. **No telemetry/analytics packages**, even disabled-by-default ones, unless network-audited and proven inert offline.

Violating any of these is a blocker, not a style nit. Flag immediately if a dependency or design forces a violation — don't route around it quietly.

---

## 2. Libraries — Use / Avoid

### 2.1 Approved (offline-capable, verified no phone-home)
| Purpose | Use |
|---|---|
| Model serving | vLLM, Ollama |
| Orchestration | LangGraph (self-hosted only — never LangSmith cloud tracing), or custom |
| API | FastAPI, Uvicorn |
| Vector DB | Chroma (local mode), Qdrant (self-hosted) |
| Keyword search | OpenSearch/Elasticsearch (self-hosted, no cloud plugins) |
| Embeddings | BGE-M3 or similar open-weight, run locally |
| OCR | PaddleOCR (offline mode), Tesseract |
| Docs | python-docx, python-pptx, openpyxl |
| Data | pandas, numpy |
| Logging | structlog, stdlib logging |
| Frontend | React, Vite, or Streamlit |
| Sandbox | Docker (local daemon only) |

### 2.2 Banned outright
- `openai`, `anthropic`, `google-generativeai`, `boto3` (Bedrock use), Azure OpenAI SDKs
- Any SDK requiring an API key to a hosted service for core function
- `sentry-sdk`, Segment, Mixpanel, PostHog cloud mode, or any crash/analytics reporter defaulting to remote endpoint
- `requests`/`httpx` calls to any non-localhost address inside runtime code paths (fine in one-time setup/download scripts only, see §2.3)
- Pickle-based deserialization of untrusted data (`pickle.load` on external input) — RCE risk
- `eval`/`exec` on any user- or model-generated string outside the sandboxed exec path

### 2.3 Conditional — allowed only in setup/build scripts, never runtime
- Model weight download scripts (`scripts/download_models.sh`) may hit network *once*, at setup time, human-triggered, clearly separated from the running app. Runtime app must never reach these scripts.

### 2.4 License check required before adding any model or package
Open-weight ≠ automatically clear for enterprise/government internal use. Check license (Llama Community License, Apache 2.0, MIT, etc.) against org's actual use case before adding to `model_registry.yaml`. Flag ambiguous licenses, don't assume.

---

## 3. Error Handling

### 3.1 General principles
- Fail loud, fail local. Never swallow exceptions silently — this is confidential-data software, silent failure can mean silent data mishandling.
- Every tool call (file I/O, sandbox exec, spreadsheet op, KB search) wrapped in try/except with structured log entry: what failed, task ID, timestamp, model/tool involved.
- User-facing errors: plain language, no stack trace dumped to UI. Full trace goes to `logs/audit/`.
- Agent orchestrator: on step failure, don't just retry blindly — log failure, attempt bounded replan (max N retries per step, configurable), then surface to user if still failing. No infinite retry loops.

### 3.2 Model serving failures
- If preferred model OOMs or unavailable → fallback chain per registry (Architecture.md §4) → if all fallbacks exhausted, surface clear error to user, don't hang silently.
- Timeout every model call. No unbounded waits.

### 3.3 Sandbox execution failures
- Capture stdout/stderr/exit code always, even on crash.
- Resource limit breach (CPU/mem/time) → kill container, log as resource-limit error, not generic failure — user needs to know if the code itself was fine but limits too tight.
- Sandbox crash must never crash the orchestrator process — isolate failure domain.

### 3.4 File/data errors
- Malformed upload (corrupt PDF, unreadable scan) → OCR/parse failure returned as explicit "could not read this file" to user, never silently skipped.
- Never overwrite a file without a confirmed diff/preview shown to user first (ties to irreversible-action rule §1.7).

### 3.5 KB / retrieval errors
- Empty retrieval result ≠ error — surface as "no matching internal documents found," let agent proceed with general knowledge but flag clearly in output that no KB grounding was used for that claim.
- Index corruption/unavailability → hard error, don't silently fall back to ungrounded answers without telling user.

---

## 4. AI Agent Behavioral Boundaries

### 4.1 What the agent MUST do
- State which model handled which step, in the visible task trace (per Architecture.md TaskTrace.tsx).
- Cite KB source docs when grounding an answer in internal manuals/SOPs.
- Show calculation steps, not just final numbers, for any engineering/financial calc.
- Ask for confirmation before: overwriting files, deleting anything, finalizing/sending a deliverable, running code that modifies files outside sandbox scratch space.
- Stop and report if a planned step would require network access — never route around a blocked call by finding another path to reach the internet.

### 4.2 What the agent MUST NOT do
- Must not fabricate KB citations — if it can't find a source, say so, don't invent a plausible-looking one.
- Must not silently downgrade to a different model without noting it in the trace.
- Must not execute code changes to its own orchestration logic, permissions, or the egress monitor. Self-modification of security-relevant code is out of scope entirely, not just gated.
- Must not treat "user asked nicely" or "user says it's urgent" as override for boundaries in §1 or §4.1. Boundaries are structural, not persuadable.
- Must not summarize/paraphrase confidential source content into a location outside the approved data dirs (e.g. no writing extracted trade-secret content into a public-facing log meant for demo purposes — scrub or synthetic-ize demo logs).

### 4.3 Human-in-the-loop checkpoints (mandatory, per PRD §5.2)
- Before file overwrite
- Before sending/exporting anything external (e.g. email draft — draft only, human sends)
- Before running code that touches anything outside sandbox scratch dir
- Before finalizing a deliverable that will be treated as an official approval note (needs human sign-off, tool drafts, doesn't approve)

---

## 5. Code Quality Baseline

- Type hints required on all Python function signatures (backend).
- No bare `except:` — always catch specific exceptions.
- Config values (paths, limits, model IDs) never hardcoded inline — pull from `config/*.yaml`.
- Secrets/keys (if any local service needs them, e.g. internal DB) via `.env`, never committed, `.env.example` kept in sync.
- Tests required for: model router fallback logic, sandbox isolation (network-none enforcement), egress monitor (must correctly flag a deliberate test outbound call).

---

## 6. Review Checklist (before merging any PR touching core paths)

- [ ] No new package added without checking §2.1–2.4
- [ ] No hardcoded model name outside registry
- [ ] New tool call wrapped in proper error handling per §3
- [ ] Any irreversible action gated behind confirmation per §4.3
- [ ] Egress monitor still shows zero calls with new code active
- [ ] License checked if new model/package added
