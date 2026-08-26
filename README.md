# Sovereign On-Premise Agentic AI Workbench

Self-hosted, air-gapped AI workbench for confidential industrial work — refineries, PSUs, defence-linked manufacturing, government offices. Runs entirely on org's own GPU hardware. Nothing leaves the premises, ever.

Built on open-weight multimodal LLMs. Multi-model backend auto-routes tasks (coding vs document vs vision) to the right model. Acts as a real agent — plans, calls local tools, iterates — not just chat. Produces real deliverables: Word/PPT/Excel files, verified code, calculations with shown steps. Grounds itself in the org's own manuals/SOPs via a local knowledge base. Proves zero external network calls, live.

---

## Why

Confidential data (P&IDs, financials, unreleased designs, correspondence) can't touch cloud AI tools by policy. Result today: manual work, or staff quietly pasting confidential material into banned public tools anyway. This closes that gap with a genuinely usable, fully local alternative.

---

## Status

Pre-build. Spec complete, Phase 0 (skeleton) not yet started. See `Memory.md` for live progress.

---

## Docs

| File | What it covers |
|---|---|
| [`PRD.md`](./PRD.md) | Problem, target users, features, scope, demo acceptance criteria |
| [`Architecture.md`](./Architecture.md) | App flow, tech stack, folder structure, model router design |
| [`Rules.md`](./Rules.md) | Hard boundaries — approved/banned libraries, error handling, agent behavioral limits |
| [`Phases.md`](./Phases.md) | Build broken into 11 sequential/parallel phases with exit criteria |
| [`Memory.md`](./Memory.md) | Live progress tracker — read this first before touching code |

Read in that order if new to the project. `Memory.md` always reflects current build state.

---

## Core Requirements (non-negotiable)

- **Zero network egress** — infra-level enforced (iptables deny-all-outbound), not just app discipline.
- **Open-weight models only** — no cloud AI APIs, no closed-weight models.
- **Multi-model, config-driven** — new models added via registry entry, no code redesign.
- **Real agent** — multi-step planning, tool use, iteration, not single-shot chat.
- **Real deliverables** — .docx/.pptx/.xlsx/code, not just chat replies.

Full detail in `Rules.md`.

---

## Tech Stack (summary)

Model serving: vLLM / Ollama · Orchestration: LangGraph or custom · API: FastAPI · Frontend: React/Vite or Streamlit · Vector DB: Chroma/Qdrant · OCR: PaddleOCR · Sandbox: Docker (network-isolated) · Docs: python-docx/pptx/openpyxl

Full stack + rationale in `Architecture.md` §3.

---

## Folder Structure

```
sovereign-ai-workbench/
├── config/           # model registry, tool permissions, network policy
├── models/           # local weight storage (gitignored)
├── backend/          # FastAPI app: orchestrator, router, tools, KB, security
├── frontend/         # React/Streamlit UI
├── sandbox/          # isolated code-exec container
├── data/             # KB index, uploads (gitignored)
├── logs/             # audit + egress logs
├── demo_assets/      # sample scanned reports, P&IDs, KB docs
├── scripts/          # setup, model download, demo runner
└── tests/
```

Full breakdown in `Architecture.md` §5.

---

## Getting Started

```bash
# 1. clone repo
git clone <repo-url> && cd sovereign-ai-workbench

# 2. one-time setup (network required for this step ONLY, per Rules.md §2.3)
./scripts/setup_env.sh
./scripts/download_models.sh

# 3. bring up local stack (fully offline from here on)
docker compose up

# 4. run demo scenarios
./scripts/run_demo.sh
```

Setup script details TBD — update once Phase 0 lands.

---

## Demo Scenarios

1. Model auto-selection across ≥2 task types
2. Scanned inspection report → approval note (.docx), end-to-end agentic
3. Coding task, sandbox-executed and verified
4. Multimodal drawing/scan understanding
5. Live proof of zero external network calls across the session

Full acceptance criteria in `PRD.md` §6.

---

## Contributing / Working on This Repo

- Read `Memory.md` before starting any session — don't re-derive state from scratch.
- Follow `Rules.md` boundaries strictly — sovereignty claim breaks if violated once.
- Follow `Phases.md` order — don't build Phase N+1 before Phase N's exit criteria pass.
- Update `Memory.md` before ending any session (completed items, in-progress state, decisions log).

---

## License

TBD.
