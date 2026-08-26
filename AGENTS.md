# AGENTS.md

Instructions for AI coding agents working in this repo. Read `Memory.md` first for current build state, then `Rules.md` for hard boundaries before writing any code.

## Dev environment tips

- This is a Python (backend) + React/Streamlit (frontend) monorepo, not JS-only — check `backend/` vs `frontend/` before assuming tooling.
- Use `docker compose up <service_name>` to bring up one service instead of the whole stack (e.g. `docker compose up backend`).
- Backend deps: `pip install -r backend/requirements.txt` inside a venv (`python -m venv .venv && source .venv/bin/activate`). Never install globally.
- Frontend deps: `cd frontend && npm install` (or `pnpm install` if `pnpm-lock.yaml` present — check before assuming).
- Model weights live in `models/`, gitignored, large — never `git add` anything under this path. Pull via `./scripts/download_models.sh` (one-time, network-allowed step only, per `Rules.md` §2.3).
- Config lives in `config/*.yaml` — never hardcode model names, paths, or limits inline. Check `model_registry.yaml` before adding a new model.
- Confirm which phase is active in `Memory.md` before starting work — don't build ahead of the current phase per `Phases.md`.
- No network access should be needed for anything except the one-time setup scripts. If a dev task seems to need network mid-build, stop and flag it — likely a boundary violation per `Rules.md` §1.

## Testing instructions

- Backend tests: `pytest tests/` from repo root, or `pytest tests/test_router.py` to focus one file.
- Focus a single test: `pytest tests/test_router.py -k "test_fallback_chain"`.
- Frontend tests (if present): `cd frontend && npm test`.
- Sandbox isolation test is mandatory after any change touching `backend/tools/code_sandbox.py` or `backend/security/`: `pytest tests/test_egress_monitor.py` must show zero flagged outbound calls, and a deliberate test call must still get caught.
- Type checking: `mypy backend/` before committing any backend change.
- Lint: `ruff check backend/` (Python), `npm run lint` (frontend, if present).
- Fix all test, type, and lint errors until green — do not commit with red CI.
- Add or update tests for any code you change, even if not explicitly asked — especially for router logic, tool error handling, and sandbox isolation (these are safety-critical per `Rules.md`).
- Before merging any change to `backend/router/`, `backend/tools/`, or `backend/security/`, re-run the full test suite, not just the touched file.

## PR instructions

- Title format: `[<phase_name>] <Title>` — e.g. `[Phase 2 - Router] Add fallback chain for OOM models`.
- Run `pytest tests/`, `mypy backend/`, `ruff check backend/` before committing.
- Reference the relevant PRD/Architecture/Rules section in the PR description if the change implements or deviates from spec.
- Any deviation from `PRD.md`, `Architecture.md`, or `Rules.md` must be logged in `Memory.md`'s Decisions Log as part of the same PR — don't leave it undocumented.
- Before requesting merge, run through the `Rules.md` §6 review checklist (no hardcoded models, no unapproved packages, egress monitor still clean, license checked on new deps).
- Update `Memory.md` (Completed / In Progress / Session Log) as part of the PR, not as an afterthought — this is required, not optional.
