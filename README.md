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
| `AGENTS.MD` | Orchestration state machine. Specialist agents with fixed execution order. Core agents run on the six standard fields; optional behaviours activate only when `optional/` is loaded. |

### Optional T3 cognitive layer (`optional/` — opt-in, liability-grade only)

| File | Purpose |
|---|---|
| `optional/LLM_WIKI.MD` | Wiki operating model. Memory tiers, confidence scoring, supersession, gap-finding. |
| `optional/FEEDBACK_LOOP.MD` | Continuous synthesis loop. Trigger types, contradiction resolution, decay model. |
| `optional/ontology-ext.md` | Opt-in field definitions (`confidence`, `memory_tier`, …) and the V3/V5–V8 conformance rules they trigger. |

### OKF Concept Files (evolve per project)

| File | Purpose |
|---|---|
| `ontology.md` | Single source of truth. Type registry, relationship taxonomy, tag vocabulary. |
| `index.md` | Bundle root index. Auto-maintained by INDEX_AGENT. |
| `log.md` | Mutation history. Auto-maintained by LOG_AGENT. |

### Directories

| Directory | Purpose |
|---|---|
| `stubs/` | Placeholder concepts for known knowledge gaps. |
| `reports/` | Loop health reports and decay reports. |
| `archive/` | Superseded concepts (never deleted, always traceable). |

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

---

## OKF Conformance

This kit produces bundles conformant with OKF v0.1 (§9):

- ✅ Every concept `.md` has parseable YAML frontmatter
- ✅ Every frontmatter has a non-empty `type` field
- ✅ `index.md` has no frontmatter (except `okf_version` at root)
- ✅ `log.md` uses ISO 8601 date headings, newest-first

Run `CONFORMANCE_AGENT` at any time by telling Claude: *"validate the bundle"*.

---

## Agent Reference

| Agent | Trigger phrase |
|---|---|
| Full enrichment cycle | "ingest [content]" |
| Read-only query | "what does the bundle say about [topic]" |
| Bundle audit | "validate" or "audit the bundle" |
| Rebuild index | "rebuild index" |
| Repair log | "rebuild log" |
| Check staleness | "check for stale concepts" |
| Extend ontology | Automatic when agent encounters unregistered type |

---

## Customising per project

The three ALL CAPS instruction files are static — use them unchanged across all projects. `ontology.md` starts with system types only; ONTOLOGY_AGENT discovers and registers domain types and tags autonomously as it ingests content. You never edit the ontology manually.

If you need to override agent behavior for a specific project, add a `PROJECT_OVERRIDES.MD` at the root. Agents check for this file and apply overrides after loading the base instruction files.

---

## Version

| Component | Version |
|---|---|
| OKF Spec | 0.1 |
| Bundle Bootstrap Kit | 2.0 |
| Last updated | 2026-06-24 |

---

© 2026 Walter Adamson | BHP 20 years, Head IT Audit - IT Strategy - Corporate Planning - International Bus Development | 100+ AI workflow solutions delivered | linkedin.com/in/adamson | walter@outcomesnow.com
