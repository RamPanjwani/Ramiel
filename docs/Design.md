# Design.md — Visual Design System

**Status:** Draft v1
**Companion docs:** PRD.md, Architecture.md, Rules.md
**Last updated:** 2026-08-26

Purpose: define colors, typography, layout language, and component approach so the UI reads as a serious instrument for confidential industrial work — not a generic AI-startup demo. This doc is the design lead's brief for anyone building frontend/UX on this project.

---

## 0. Grounding the Brief

**Subject:** a sovereign, air-gapped AI workbench used by refinery engineers, defence-manufacturing staff, and government office workers to do confidential technical work — reading P&IDs, drafting approval notes, running code in a sandbox, verifying nothing has left the building.

**Audience:** technical professionals in high-trust, high-compliance environments. Not consumers. Not a SaaS landing page trying to convert a visitor in 8 seconds. This is a tool people will sit inside for hours, that also has to visibly earn the trust of an IT security officer glancing over someone's shoulder.

**The page's job:** communicate precision, restraint, and evidence — never hype. Every visual choice should feel like it belongs in a control room, not a pitch deck.

**Explicit anti-goal:** avoid every item on this list (current tells of generic AI-generated interfaces):
harsh gradients, lucide-icon soup, pure white backgrounds, rainbow coloring, drop shadows, 3-cards-in-a-row feature grids, emojis, "liquid glass" surfaces, em dashes in copy, Inter/Geist/Space Grotesk as the whole type system, colored left-stripe cards, fake testimonials, bento grids, terminal-window decoration for its own sake, "it's not X, it's Y" copywriting, checkmark bullet lists, 3-tier pricing tables, no real product demos, universally soft corner radius, radial orbs, dot grids, sparkle icons, animated arrows, purple-and-black, neon colors, basic pastel palettes.

Also avoid the three current AI-default looks: (1) warm cream + high-contrast serif + terracotta accent, (2) near-black + single acid-green/vermilion accent, (3) broadsheet hairline-rule newspaper layout. This brief has its own material to draw from instead (see §1).

---

## 1. Design Philosophy: "Instrument Panel"

The subject already has a native visual vocabulary: P&IDs, gauge faces, engineering drawings, control-room consoles, inspection stamps, revision tables, blueprint linework. That vocabulary is where this design pulls from — not SaaS dashboard trends.

**The one sentence:** this interface should look like it was designed by the same discipline that designs a control room — every element earns its place, nothing is decorative, and the whole thing reads as calm authority under real operating conditions.

**Signature element:** a persistent, quietly-present **egress status strip** — a thin instrument-style readout (not a card, not a badge) always visible in the shell, showing live network activity as a moving trace, currently reading zero. This is the one thing this product has that nothing else does — the literal, visual proof of the sovereignty claim — so it gets the design's one deliberate flourish. Everything else stays disciplined around it.

---

## 2. Color

Dark-first. A control room runs dim so operators can read instruments without glare, and dark UI suits long technical sessions (this tool is used for hours, not glanced at). Light mode is secondary — see §2.3.

### 2.1 Core palette (dark mode, primary)

| Token | Hex | Use |
|---|---|---|
| `bg-base` | `#0E1214` | App background — near-black with a cold blue-green undertone, not pure black, not navy |
| `bg-surface` | `#161B1E` | Panels, cards, sidebars |
| `bg-surface-raised` | `#1E2528` | Modals, active/focused panels |
| `line-hairline` | `#2A3236` | Borders, dividers, grid lines — always hairline (1px), never soft drop shadows |
| `text-primary` | `#E4E9EA` | Primary text — off-white, not pure #FFF |
| `text-secondary` | `#8B979B` | Secondary/muted text, labels, captions |
| `signal-amber` | `#D98E2F` | The single accent color — active states, egress strip when idle-safe, key numerals. Chosen deliberately: amber/orange is the color of instrumentation and hazard-adjacent industrial signage, not a SaaS brand color. Kept intentionally more orange/muted than Anthropic's own terracotta accent to avoid reading as a Claude tell. |
| `signal-red` | `#C4453B` | Errors, blocked actions, irreversible-action confirmations only — never decorative |
| `signal-green` | `#4A9E6E` | Success states, "zero egress confirmed" — used sparingly, never as a general accent |

No gradients. No purple. No neon. Color is functional signage, the same way a control panel uses color: green means normal, amber means attention, red means stop — and that's the entire semantic vocabulary. Nothing decorative gets color.

### 2.2 Why this palette, specifically

- Refineries and industrial sites use amber/red/green indicator conventions on physical control panels — this palette borrows that literal, familiar visual language rather than inventing a "brand" one.
- Cold, desaturated background reads as technical/measured rather than either "cozy SaaS" or "hacker terminal."
- Avoids both AI-default looks called out in §0 by construction: not cream+terracotta, not black+single-neon (the accent here is muted amber, paired with an equally important green/red — a 3-color signal system, not a 1-color highlight).

### 2.3 Light mode (secondary, for print/export contexts)

| Token | Hex | Use |
|---|---|---|
| `bg-base` | `#F1F0EC` | Warm paper-white, not pure #FFF — echoes engineering drawing paper |
| `bg-surface` | `#FFFFFF` | Panels |
| `line-hairline` | `#D8D6CF` | Borders |
| `text-primary` | `#1B1F20` | Primary text |
| `signal-amber` | `#B8701F` | Darkened for AA contrast on light bg |

Light mode exists mainly for previewing generated deliverables (approval notes, reports) where paper-white makes sense — not the primary working shell.

---

## 3. Typography

Two-role system, deliberately not a generic sans-only stack (explicitly avoiding Inter/Geist/Space Grotesk as the whole system).

| Role | Typeface | Why |
|---|---|---|
| **Display / headings** | **IBM Plex Sans** (semi-bold/bold) | Designed for technical/enterprise documentation contexts, has real character without being decorative, open-source and self-hostable — fits the no-CDN, air-gapped requirement in Rules.md. |
| **Body text** | **IBM Plex Sans** (regular/medium) | Same family, different weights — keeps the UI cohesive rather than pairing two unrelated grotesques, which is the more common (and more templated) choice. |
| **Data / monospace** | **IBM Plex Mono** | For everything that is literally data: file paths, model IDs, code blocks, the egress log, task IDs, timestamps, calculation steps. Using a real monospace face for actual data — not decoration — is the single typographic signature of this design: it visually separates "this is a verified reading" from "this is prose." |

All three roles come from one family (IBM Plex Sans + IBM Plex Mono), self-hosted as static font files under `frontend/public/fonts/` — zero external font requests, consistent with the air-gap requirement in Rules.md §1.1.

### Type scale (rem, 16px base)

| Token | Size | Weight | Use |
|---|---|---|---|
| `display-lg` | 2.5rem | 600 | Page-level headers only, used rarely |
| `heading` | 1.5rem | 600 | Section headers |
| `subheading` | 1.125rem | 500 | Card/panel titles |
| `body` | 0.9375rem | 400 | Default body text |
| `caption` | 0.8125rem | 400 | Labels, metadata, secondary text |
| `mono-data` | 0.875rem | 400–500 (Plex Mono) | File paths, logs, model IDs, code |

No huge hero numerals, no oversized display type for its own sake — restraint matches the "instrument panel" brief, not a landing page.

---

## 4. Layout Language

### 4.1 Structure principles

- **Grid, not cards-in-a-row.** Avoid the generic 3-feature-card pattern entirely. Where multiple items sit side by side (model registry entries, task steps), use a dense table/list format with hairline row dividers — closer to a revision table on an engineering drawing than a marketing feature grid.
- **No soft shadows.** Depth comes from hairline borders and subtle background-value shifts (`bg-surface` vs `bg-surface-raised`), never blurred `box-shadow`. Hard rule, ties directly to the anti-pattern list in §0.
- **Corner radius: small and consistent, not universally soft.** 4px on interactive elements (buttons, inputs), 0px on data tables and the egress strip — a readout should look drawn with a ruler, not rounded like a bubble.
- **Numbering only where it's real.** Don't add 01/02/03 step markers decoratively. This project has real sequences (Phases.md, agent task steps) — use numbered markers there, and nowhere else.

### 4.2 App shell wireframe

```
+------------------------------------------------------------------+
| [=] Sovereign Workbench      [egress: -^--- 0 calls]      [user] |  <- persistent top strip
+---------------+----------------------------------------------------+
|               |                                                    |
|  Task history |           Main work surface                       |
|  (left rail,  |           (chat + task trace, tabs for             |
|   collapsible)|            active deliverable preview)             |
|               |                                                    |
|  - Task A     |  +----------------------------------------------+ |
|  - Task B     |  | Plan -> Step 1 (vision model)   done          | |
|  - Task C     |  |         Step 2 (KB search)      done          | |
|               |  |         Step 3 (draft note)     running       | |
|               |  +----------------------------------------------+ |
|               |                                                    |
|               |  [ file preview / deliverable panel, right-docked,]|
|               |  [ opens on demand, not a default 50/50 split     ]|
+---------------+----------------------------------------------------+
```

- Left rail: task history, collapsible, quiet (`text-secondary`, not competing for attention).
- Main surface: the task trace is a first-class element, not hidden in a collapsed accordion — showing the plan and step status live is core to the trust story, so it stays visible by default.
- Deliverable preview: docked panel, opens on demand rather than a permanent split, so the chat/trace stays the primary reading surface.
- Egress strip: lives in the top bar, always visible, on every screen — never buried in a settings page.

### 4.3 Motion

Minimal and functional only:
- Task step status changes (pending → running → done) — a simple state change, not a bounce or spring.
- Egress strip — a continuous, low-amplitude trace line (like an oscilloscope idling flat), the one ambient animation in the product, because it's the signature element and it's showing real state, not decoration.
- No hover micro-interactions beyond a background-color shift on interactive elements. No animated arrows, no scroll-triggered reveals — those belong to marketing pages, not a tool used for hours.
- Respect `prefers-reduced-motion` everywhere; the egress trace becomes a static readout when reduced motion is set.

---

## 5. Component Approach

### 5.1 Base library

Use **shadcn/ui** as the primitive layer (unstyled by default, full source ownership, no runtime dependency on any external registry once components are vendored into the repo — consistent with the air-gap requirement). Pull components once during development via CLI, then the component source lives in-repo permanently.

**Do not** reach for decorative animated component kits (Skiper UI, 21st.dev/Magic, or React Bits' more ornamental effects — liquid-glass surfaces, radial orbs, dot-grid backgrounds, sparkle/gradient buttons). These are exactly the aesthetic this brief avoids (§0), and they also introduce external registry/CDN dependencies if pulled at runtime rather than vendored — a direct conflict with the air-gap rule.

Where a genuinely useful interaction pattern exists in one of those libraries (e.g. a well-built data table or command palette), vendor the source in manually and restyle it to this doc's tokens rather than importing the library's default aesthetic wholesale.

### 5.2 Icons

A single, restrained icon set at small sizes for functional markers only (file type, status, action affordances) — never as decoration, never oversized, never in place of text labels for anything non-obvious. Avoid the generic "icon in every card corner" pattern; an icon appears only where it disambiguates faster than a word would.

### 5.3 Charts / data viz

For model performance, task history, or usage views: plain, labeled, hairline-bordered charts (line/bar) in the amber/green/red signal palette only — no rainbow multi-series palettes, no gradient fills. Think oscilloscope/gauge readout, not marketing infographic.

### 5.4 Deliverable previews (docx/pptx/xlsx)

Rendered previews of generated Word/PowerPoint/Excel files should look like the actual target application's output — not restyled to match the app shell. The point is to preview exactly what the user will get; skinning it to the dark instrument-panel theme would misrepresent the deliverable.

---

## 6. Accessibility & Quality Floor

- WCAG AA contrast minimum for all text against its background, checked against both palettes in §2.
- Visible keyboard focus ring on every interactive element — a 1px `signal-amber` outline, consistent with the instrument-panel language (a focus ring is itself a kind of indicator light).
- Fully responsive down to a single-column mobile layout for remote/mobile access use cases, even though primary use is desktop/workstation.
- `prefers-reduced-motion` respected everywhere per §4.3.
- Every icon-only control has a text label on hover/focus and an `aria-label`.

---

## 7. What "Done Well" Looks Like

A person unfamiliar with the project should look at a screenshot and say "this looks like it belongs in a plant control room or an engineering office," not "this looks like an AI startup's landing page." The egress strip should be the first thing a skeptical IT security officer notices and trusts. The task trace should be the first thing an engineer notices and finds legible. Nothing on screen should exist purely to look impressive.

---

## 8. Reference Material Considered (and why most was set aside)

The component/skill ecosystem scanned for this brief (Skiper UI, React Bits, ThreeUI, 21st.dev/Magic, shadcn registries and MCP, the `canvas-design` art-philosophy skill, Vercel's `web-design-guidelines`/`react-best-practices` skills) skews toward consumer SaaS, marketing sites, and portfolio/gallery-grade visual flourish — liquid glass, animated arrows, gradient buttons, bento grids, 3D reconstructions. None of that vocabulary fits a confidential industrial tool, and using it would actively undercut the trust story this product depends on.

**What was kept:**
- **shadcn/ui** as an unstyled primitive base (§5.1) — structurally useful, aesthetically neutral until restyled.
- **Vercel's `web-design-guidelines` and `react-best-practices` skills** — the accessibility, forms, performance, and dark-mode/theming rule categories are genuinely applicable and worth running as a review pass once the UI is built, independent of their default visual style.
- **IBM Plex** typeface family — not from the scanned list, chosen specifically because it was designed for this kind of technical/enterprise context and is safely self-hostable.

**What was explicitly rejected:** any library or skill whose primary value proposition is decorative motion, glassmorphism, gradient-driven branding, or marketing-page composition (Skiper UI's animated effects, 21st.dev/Magic's UI-generation defaults, React Bits' more ornamental components, the `canvas-design` art-piece philosophy skill, ThreeUI's shader-driven renderers) — all aimed at a fundamentally different brief than this one.

---

## 9. Open Items for Next Draft

- [ ] Confirm IBM Plex license (SIL Open Font License) is acceptable for target orgs — verify per Rules.md §2.4 license-check discipline
- [ ] Build a component inventory (buttons, inputs, table, modal, egress strip) as a Figma/Storybook reference before frontend build starts
- [ ] Decide whether light mode gets full parity or stays deliverable-preview-only
- [ ] Screenshot-review pass once Phase 4+ UI exists — check against §0 anti-pattern list before calling any screen done
