---
type: Decision
title: Kit Restructure — Demote the Runtime Cognitive Layer to optional/
description: Concrete change splitting the kit into a lean always-on core and an optional T3-only cognitive layer, based on evidence that the operating repo (html-reports-rob) does not use the heavy layer.
tags: [governance, kit-architecture, restructure]
okf_version: "0.1"
timestamp: 2026-06-24
---

## Version history
- 2026-06-24 — v1.0 — Initial restructure sketch. Core/optional split proposed off operating-repo evidence.

---

# Why

Evidence from the operating repo (`html-reports-rob`), generated from this kit:

- All 75 concept files carry only the six standard fields (`type`, `title`,
  `description`, `resource`, `tags`, `timestamp`). That is near-vanilla OKF.
- `confidence`, `memory_tier`, `okf_version`-per-file appear in **1–2 of 78**
  files — leftover leakage, not a working system.
- `LLM_WIKI.MD` and `FEEDBACK_LOOP.MD` did **not** propagate to the operating
  repo at all.
- Generation is done by `scripts/build-okf.py` from `catalog/pages.json` — a
  deterministic build, **not** the six-agent runtime synthesis loop.

Conclusion: the runtime cognitive layer is overcooked for normal use. The
operating repo already voted on it by not using it. Don't delete it — demote it.

# Target structure (AS EXECUTED, v2.0.0)

Core stays at **root** — the kit must drop into a project root so agents read
`AGENTS.MD` in place. A `core/` subfolder would break that, so we did NOT use one.
Only the heavy layer moved.

```
kit/                           # repo root = the bundle root
├── AGENTS.MD                  # core orchestrator + CORE vs OPTIONAL banner
├── ontology.md               # core type/tag/relationship registry
├── index.md  log.md
├── stubs/ reports/ archive/
│
├── optional/                  # pulled in ONLY for T3 (liability-grade) domains
│   ├── LLM_WIKI.MD           # memory tiers, confidence, supersession
│   ├── FEEDBACK_LOOP.MD      # continuous synthesis + decay loop
│   ├── ontology-ext.md       # opt-in field defs + V3/V5–V8 rules
│   └── README.md             # how/when to enable
│
└── docs/
    ├── OKF_DIVERGENCE.md
    └── KIT_RESTRUCTURE.md     # this file
```

> Note: `scripts/build-okf.py` and `catalog/pages.json` live in the OPERATING
> repo (`html-reports-rob`), not in this kit. Generation strategy is a
> per-domain choice (agent pipeline vs. deterministic build); the kit ships the
> agent pipeline.

# Field policy by tier

| Field | Core (T1/T2) | optional/ (T3) |
|---|---|---|
| `type`, `title`, `description`, `tags`, `timestamp`, `resource` | yes | yes |
| `confidence` | no | yes |
| `memory_tier` | no | yes |
| supersession / `archive/` workflow | no | yes |
| contradiction records | no | yes |

# Migration steps (non-destructive)

1. `git mv` `LLM_WIKI.MD` and `FEEDBACK_LOOP.MD` into `optional/`.
2. Split `ontology.md`: keep the type/tag/relationship registry in `core/`;
   move `confidence`/`memory_tier` field defs into `optional/ontology-ext.md`.
3. Trim `AGENTS.MD` to the three agents that actually run in the operating repo
   (build, index, log). Park the enrichment/link/consumption/conformance agents
   as an appendix that `optional/` re-enables.
4. Strip the 1–2 leaked `confidence`/`memory_tier`/per-file `okf_version` lines
   from the operating bundle, or formally promote that domain to T3.
5. Add a one-line README pointer to `docs/OKF_DIVERGENCE.md`.
6. Bump kit to **2.0.0** (MAJOR — file structure changes), with this file as the
   migration note.

# What does NOT change

`ontology.md`, `build-okf.py`, `catalog/pages.json`, `index.md`, `log.md`, and
the six standard fields stay exactly as they are. The lean path gets lighter and
faster to clone per domain; the heavy path is still available, just opt-in.
