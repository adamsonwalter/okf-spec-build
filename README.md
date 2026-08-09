# OKF Bundle Bootstrap Kit

**Open Knowledge Format v0.1 — Self-maintaining knowledge bundle for AI agent projects**

**Source:** [github.com/adamsonwalter/okf-spec-build](https://github.com/adamsonwalter/okf-spec-build)

Drop this into any Claude Cowork (or compatible AI agent) project to get a fully operational, continuously evolving knowledge graph from day one.

---

## What this is

An operating system that turns any project folder into a compounding knowledge base. Agents read the instruction files, build and maintain OKF-compliant markdown concept files, cross-link them into a knowledge graph, and keep everything current as new inputs arrive. The lean core handles most domains; an opt-in `optional/` layer adds confidence/memory machinery for liability-grade work.

Based on:
- [Google Cloud Open Knowledge Format v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- Andrej Karpathy's LLM Wiki pattern (2026)

---

## Two deployment modes from one build

Every bundle built with this kit works in two modes simultaneously:

| Mode | Where | What to use |
|---|---|---|
| **IDE / Agent** | Cursor, Antigravity, Claude Cowork, local git | Full structured folder — subfolders, cross-links, `index.md` navigation, live agent editing |
| **Cloud LLM Project** | Gemini Gem, Claude.ai Project, ChatGPT Project | `projections/<bundle>-master.md` only — one flat file, self-contained, one swap to update |

**Key rule for cloud Projects:** upload the master projection file **only**. Do not upload `index.md` (relative links break with no file system), `log.md`, individual concept files, or `AGENTS.MD`. The projection already embeds the ontology as §0 and all active concepts.

See `playbook/PROJECTION_GUIDE.md` for full details.

For running a generated bundle inside a **per-client Claude Cowork Project** — attaching the
standard OKF folder read-only and keeping client work persistent in the Project folder — see
`playbook/COWORK_PROJECT_GUIDE.md` (thin Project-instructions loader + the two-write-target rule
that keeps the shared standard clean across clients).

## Core vs optional

This kit is split into a lean **core** (always used) and an opt-in **T3
cognitive layer** in `optional/`. Evidence from real operating bundles showed the
heavy layer left almost no trace in normal use, so it is now opt-in — see
`docs/KIT_RESTRUCTURE.md`. For how this kit's dialect relates to the vanilla
Google spec (and why the ontology is our convention, not an OKF requirement), see
`docs/OKF_DIVERGENCE.md`.

## Files in this kit

### Core agent instructions (ALL CAPS — not OKF concepts)

| File | Purpose |
|---|---|
| `AGENTS.MD` | Orchestration state machine. 7 specialist agents: ENRICHMENT, LINK, INDEX, LOG, CONSUMPTION, CONFORMANCE, PROJECTION. |

### Optional T3 cognitive layer (`optional/` — opt-in, liability-grade only)

| File | Purpose |
|---|---|
| `optional/LLM_WIKI.MD` | Wiki operating model. Memory tiers, confidence scoring, supersession, gap-finding. |
| `optional/FEEDBACK_LOOP.MD` | Continuous synthesis loop. Trigger types, contradiction resolution, decay model. |
| `optional/ontology-ext.md` | Opt-in field definitions (`confidence`, `memory_tier`, …) and the V3/V5–V8 conformance rules they trigger. |

### OKF Concept Files (evolve per project)

| File | Purpose |
|---|---|
| `ontology.md` | Single source of truth. Type registry, relationship taxonomy, tag vocabulary. Embedded as §0 in every projection. |
| `index.md` | Bundle root index. Auto-maintained by INDEX_AGENT. **Not for cloud Project upload.** |
| `log.md` | Mutation history. Auto-maintained by LOG_AGENT. **Not for cloud Project upload.** Append before every commit — see `playbook/BUNDLE_COMMIT_CHECKLIST.md`. |

### Directories

| Directory | Purpose |
|---|---|
| `projections/` | **Flat-file exports for cloud LLM Projects.** PROJECTION_AGENT writes here. One master file = one upload. Fully regenerated every run — cannot drift. |
| `deliverables/` | **Optional, per-domain.** Hand-authored client artifacts (interactive HTML tools, dashboards) that PROJECTION_AGENT cannot produce. If one embeds its own snapshot of concept data, it MUST be registered as a Deliverable Parity Contract in `ontology.md` — see below. Hand-edited, so it CAN drift if the contract is skipped. |
| `errata/` (or `coverage/`) | **Created automatically the first time a whole document is ingested.** Holds `type: Coverage Ledger` concepts — the enumeration `STATE: INVENTORY` builds before any concept is written, registered as a Source Coverage Contract in `ontology.md`. |
| `stubs/` | Placeholder concepts for known knowledge gaps. |
| `reports/` | Loop health reports and decay reports. |
| `archive/` | Superseded concepts (never deleted, always traceable). |
| `playbook/` | Domain setup and operations guides — **includes `BUNDLE_COMMIT_CHECKLIST.md`**. |
| `templates/` | Seeds for new bundles — **`log-domain-init.md`** for domain `log.md` on first clone. |
| `scripts/` | **Executable checks.** `okf_check.py` runs CHECK_1–CHECK_9 and V1–V9 in code and exits non-zero. Shipped with the kit, so every generated bundle has it from day one. |
| `tests/` | Tests for `scripts/`. `python3 -m unittest discover -s tests`. |

---

## Naming Convention

```
ALL_CAPS.md   = agent instruction files (read and executed by agents, not indexed as OKF concepts)
lowercase.md  = OKF concept documents (frontmatter required, type required, indexed)
```

---

## Quick Start

### 1. Clone into your project

```bash
git clone https://github.com/adamsonwalter/okf-spec-build .
# or copy files into an existing project root
```

For a **new domain bundle** (not contributing to the kit itself): copy
`templates/log-domain-init.md` → `log.md` and set your domain name + date. Do not keep the
kit's release history in a domain repo's log.

### 2. Start a session in Claude Cowork

Default (T1/T2) — tell Claude: *"Read AGENTS.MD and ontology.md, then ingest [your first document or topic]."*

T3 (liability-grade) — also copy the three files from `optional/` into the root and say: *"Read AGENTS.MD, ontology.md, and the files in optional/, then ingest …"*

The agents will:
- Extract concepts from your input
- Create OKF-compliant `.md` files
- Cross-link them into a knowledge graph
- Build `index.md` and `log.md`
- Track confidence, gaps, and contradictions

### 4. Keep building

Every subsequent session, new inputs are synthesized against existing concepts:
- Confirmations raise confidence
- Contradictions are flagged and resolved
- Inferences from queries are added as new concepts
- Stale concepts are flagged for review

The bundle compounds over time.

### 3. Commit discipline (every bundle)

**Never `git commit` without updating `log.md` first.**

| Session type | What to do before commit |
|---|---|
| Ingest (`"ingest inbox/"`) | Pipeline runs LOG_AGENT automatically — verify `log.md` has today's entries |
| Direct edits (ontology, concepts, deliverables, etc.) | Run `"append log"` or `"repair log"`, then commit |
| Any commit / push request | Orchestrator routes to LOG_AGENT first (AGENTS.MD §BUNDLE COMMIT CHECKLIST) |

Printable checklist: `playbook/BUNDLE_COMMIT_CHECKLIST.md`. Domain log seed:
`templates/log-domain-init.md`.

---

## OKF Conformance

This kit produces bundles conformant with OKF v0.1 (§9):

- ✅ Every concept `.md` has parseable YAML frontmatter
- ✅ Every frontmatter has a non-empty `type` field
- ✅ `index.md` has no frontmatter (except `okf_version` at root)
- ✅ `log.md` uses ISO 8601 date headings, newest-first; not placeholder-only (CHECK_8)
- ✅ (if any are registered) every Deliverable Parity Contract's source concept files and
  deliverable records are in 1:1 correspondence, by identity key — not just by count
- ✅ (if any are registered) every Source Coverage Contract's ledger has zero rows left
  "Not yet checked" — every named unit in a whole-document ingestion was captured, enforced
  at ingestion time by `STATE: INVENTORY` / `GATE_5-COVERAGE`, not just audited after (CHECK_9)

Run the checks yourself, in code:

```bash
python3 scripts/okf_check.py .
```

Exit `0` = conformant, `1` = at least one ERROR, `2` = unreadable. Add `--json` for
machine-readable findings.

Or tell Claude *"validate the bundle"* to run `CONFORMANCE_AGENT`, which runs the same
script first and then reports only the few things code cannot settle — whether a
contested claim names the right open question, whether a Coverage Ledger still matches
its source document, and whether a hand-authored deliverable has drifted at record level.

**Why a script and not just the agent.** An agent-run check that reports PASS and a check
that was never run are indistinguishable afterwards. Every one of CHECK_1–CHECK_9 is
mechanically decidable, so none of them should depend on that distinction.

---

## Agent Reference

| Agent | Trigger phrase |
|---|---|
| Full enrichment cycle | "ingest [content]" |
| Read-only query | "what does the bundle say about [topic]" |
| **Build cloud projection** | **"build projection"** or **"update projection"** or **"export"** |
| **Build tag-scoped slice** | **"build projection [tag]"** |
| Bundle audit | "validate" or "audit the bundle" |
| Rebuild index | "rebuild index" |
| Repair log | "rebuild log" or "repair log" |
| **Commit / push bundle changes** | **LOG_AGENT first** — see `playbook/BUNDLE_COMMIT_CHECKLIST.md` and AGENTS.MD §BUNDLE COMMIT CHECKLIST |
| Check staleness | "check for stale concepts" |
| Extend ontology | Automatic when agent encounters unregistered type |
| **Register a deliverable parity contract** | Automatic the moment a hand-authored `deliverables/` artifact embedding concept data is built — or say **"register deliverable parity"** |
| **Whole-document ingest (PDF, report, transcript)** | Automatic — orchestrator dispatches SOURCE-DOCUMENT MODE, which runs `STATE: INVENTORY` (builds/updates a Coverage Ledger) before writing any concept, and blocks completion (`GATE_5-COVERAGE`) until every ledger row is resolved |

---

## Customising per project

The three ALL CAPS instruction files are static — use them unchanged across all projects. `ontology.md` starts with system types only; ONTOLOGY_AGENT discovers and registers domain types and tags autonomously as it ingests content. You never edit the ontology manually.

If you need to override agent behavior for a specific project, add a `PROJECT_OVERRIDES.MD` at the root. Agents check for this file and apply overrides after loading the base instruction files.

---

## Version

| Component | Version |
|---|---|
| OKF Spec | 0.1 |
| Bundle Bootstrap Kit | 2.3.0 |
| Last updated | 2026-07-03 |

---

© 2026 Walter Adamson | BHP 20 years, Head IT Audit - IT Strategy - Corporate Planning - International Bus Development | 100+ AI workflow solutions delivered | linkedin.com/in/adamson | walter@outcomesnow.com
