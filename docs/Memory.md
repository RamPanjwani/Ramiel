# Memory.md — Live Progress Tracker

**Purpose:** running state of build. Update after every work session. AI/human reads this FIRST before touching code — don't re-read whole repo, don't guess state.

**Last updated:** 2026-08-26 (repo not yet started — scaffold only)

---

## Current Phase
**Phase 0 — Environment & Skeleton** (not started)

See Phases.md for phase definitions and exit criteria.

---

## Status Snapshot

| Field | Value |
|---|---|
| Current phase | Phase 0 |
| File/module in progress | none yet |
| Last completed file | none yet |
| Blocked on | nothing |
| Next action | scaffold repo per Architecture.md §5 |

---

## Completed ✅
_(none yet — move items here from "In Progress" once done + tested)_

---

## In Progress 🔧
_(nothing yet — update this every session, be specific: file path, what's left, why paused)_

Format to use:
```
- [ ] path/to/file.py — what's done, what's left, any blocker
```

---

## Not Started (upcoming, per current phase)
- [ ] Repo scaffold (folder structure per Architecture.md §5)
- [ ] docker-compose.yml skeleton
- [ ] config/model_registry.yaml (stub)
- [ ] config/tool_permissions.yaml (stub)
- [ ] config/network_policy.yaml (stub)
- [ ] backend/security/egress_monitor.py + iptables deny-all rule
- [ ] backend/main.py hello-world FastAPI
- [ ] frontend hello-world page
- [ ] egress monitor test (deliberate outbound call gets flagged)

---

## Decisions Log
_(record any decision that deviates from or finalizes something left open in PRD/Architecture/Rules — so it's not re-litigated or forgotten)_

| Date | Decision | Why | Doc affected |
|---|---|---|---|
| — | none yet | — | — |

---

## Known Issues / Tech Debt
_(anything shipped imperfect on purpose to keep moving — log it so it isn't forgotten)_

- none yet

---

## Session Log
_(short entries, newest on top — what happened, what's next. Keeps context across chat switches without re-reading whole codebase)_

- **2026-08-26** — PRD.md, Architecture.md, Rules.md, Phases.md finalized. Memory.md scaffolded. No code written yet. Next: start Phase 0 repo scaffold.

---

## How to Update This File

- After finishing a file/module: move it to ✅ Completed, one line, what it does.
- Before pausing mid-file: update 🔧 In Progress with exact state + what's left.
- Any deviation from PRD/Architecture/Rules: log in Decisions Log immediately, don't rely on memory of the conversation.
- Every session: add one line to Session Log before ending.
- Never delete old entries — this file is the audit trail of the build itself.
