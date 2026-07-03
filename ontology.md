---
type: Ontology
title: Bundle Ontology
description: Single source of truth for all concept types, relationship semantics, tag taxonomy, and validation rules in this OKF bundle.
memory_tier: semantic
confidence: 1.0
okf_version: "0.1"
timestamp: 2026-07-03T05:26:26Z
tags: [ontology, system, governance]
---

> This file is maintained by agents (ENRICHMENT_AGENT, ONTOLOGY_AGENT) and by humans.
> It is the authoritative registry for this bundle. All agents MUST consult it before
> creating a new `type`, registering a new relationship, or adding tags.
> To extend the ontology: add an entry in the correct section below and update `timestamp`.
> Never delete entries — deprecate them (see §DEPRECATED TYPES).

---

# Type Registry

All valid values for the `type` frontmatter field in this bundle.
Agents MUST reject or flag any concept using a `type` not listed here,
and propose an addition via the ONTOLOGY_AGENT (see §EXTENDING).

## Core Knowledge Types

| Type | Description | Typical Body Sections |
|---|---|---|
| `Concept` | A discrete idea, entity, or domain term. | Schema, Examples, Citations |
| `Playbook` | Step-by-step procedure for a known task. | Trigger, Steps, Outcome |
| `Decision` | A recorded decision with context and rationale. | Context, Options, Chosen, Rationale |
| `API Endpoint` | An external or internal API surface. | Schema, Authentication, Examples |
| `Metric` | A measurable quantity with definition and source. | Formula, Source, Caveats |
| `Reference` | A pointer to an external source or document. | Summary, Citations |
| `Glossary Term` | A domain vocabulary definition. | Definition, Related Terms |
| `Person` | A named individual (role-based, not PII). | Role, Expertise, Related Concepts |
| `Organisation` | A company, team, or institution. | Description, Relationships |
| `Event` | A time-bound occurrence. | Date, Participants, Outcome |
| `Dataset` | A named collection of data. | Schema, Source, Access |
| `System` | A software system, platform, or tool. | Description, API Endpoint refs |
| `Process` | A recurring business or technical workflow. | Steps, Actors, Inputs, Outputs |

## Memory & Governance Types (system-managed)

> NOTE (v2.0): `Inference`, `Loop Health Report`, `Decay Report`, and
> `Contradiction Record`, plus the `confidence`/`memory_tier` fields, belong to
> the OPTIONAL T3 cognitive layer. A default (T1/T2) bundle does not use them.
> Field and rule definitions live in `optional/ontology-ext.md`.
>
> NOTE (v0.3): `Coverage Ledger` is the one exception — it is CORE, not
> optional-layer, and applies at every effort tier (T1/T2/T3). It is a
> completeness check (was everything captured?), not a correctness or
> confidence mechanism (is it right?), so it carries none of the T3
> confidence/memory-tier machinery and costs nothing extra for a T1 bundle to
> use on a whole-document ingestion.

| Type | Description | Created By |
|---|---|---|
| `Ontology` | This file. The bundle's type and relationship registry. | Human / ONTOLOGY_AGENT |
| `Stub` | A placeholder for a known gap. Confidence 0.0. | ENRICHMENT_AGENT (gap-finder) |
| `Inference` | A relationship or claim derived by an agent from existing concepts. | CONSUMPTION_AGENT |
| `Agent Instruction` | An instruction file for agent behavior (ALL CAPS .md files). | Human |
| `Loop Health Report` | Periodic diagnostic snapshot of bundle health metrics. | LOG_AGENT |
| `Decay Report` | List of stale, isolated, or low-confidence concepts. | CONFORMANCE_AGENT |
| `Contradiction Record` | A logged contradiction event and its resolution. | ENRICHMENT_AGENT |
| `Coverage Ledger` | An exhaustive inventory of every named structural unit in a source document (Box/Table/Figure/callout/appendix/quote), mapped to the bundle file(s) that capture it, with a Status column (Captured / Partial / N/A / Not yet checked). Built by ENRICHMENT_AGENT's `STATE: INVENTORY` on every SOURCE-DOCUMENT MODE ingestion — the mechanical completeness gate that checks whether everything was captured, distinct from correctness checks on what *is* captured. | ENRICHMENT_AGENT (STATE: INVENTORY) |

## Project-Specific Types

> Add domain-specific types below as the bundle grows.
> Format: `| Type | Description | Typical Body Sections |`

*(empty at bundle initialisation — add as needed)*

---

# Relationship Taxonomy

Cross-links between concepts carry meaning inferred from surrounding prose.
This taxonomy standardises that meaning for agents and human readers.

Agents SHOULD annotate links with a relationship label in the surrounding prose.
The label does NOT appear in the markdown link syntax — it appears as natural language.

| Relationship | Direction | Prose signal | Example |
|---|---|---|---|
| `depends-on` | A → B | "requires", "built on", "cannot run without" | System A depends on API B |
| `implements` | A → B | "implements", "is an instance of", "follows" | Playbook implements Process |
| `contradicts` | A ↔ B | "disputes", "conflicts with", "challenges" | Decision A contradicts Metric B |
| `supersedes` | A → B | "replaces", "supersedes", "updates" | Concept A supersedes Concept B |
| `references` | A → B | "see", "refer to", "documented in" | Playbook references Dataset |
| `related-to` | A ↔ B | "related", "connected", "associated" | Concept A related to Concept B |
| `part-of` | A → B | "belongs to", "is part of", "component of" | Metric is part of System |
| `derived-from` | A → B | "derived from", "based on", "calculated using" | Metric derived from Dataset |
| `authored-by` | A → B | "authored by", "written by", "maintained by" | Playbook authored by Person |
| `governs` | A → B | "governs", "constrains", "regulates" | Ontology governs all Concepts |

---

# Tag Taxonomy

All valid tags for the `tags` frontmatter field.
Tags are lowercase, hyphenated. Agents MUST use registered tags.
Unregistered tags trigger a Type Orphan gap flag (T3 only; see `optional/LLM_WIKI.MD` §GAP-FINDING).

## System Tags (reserved)

| Tag | Meaning |
|---|---|
| `system` | Bundle infrastructure: ontology, instructions, health reports |
| `governance` | Policies, rules, constraints |
| `stub` | Incomplete / placeholder concept |
| `review-required` | Needs human or agent verification |
| `archived` | Superseded or deprecated |
| `inference` | Agent-derived, not directly sourced |
| `disputed` | Contains an unresolved contradiction |
| `coverage` | A Coverage Ledger or other bundle-completeness audit artifact |

## Domain Tags

> Add project-specific tags below as the bundle grows.
> Format: `| tag-name | meaning |`

*(empty at bundle initialisation — add as needed)*

---

# Concept Hierarchy Rules

OKF does not enforce a taxonomy, but this bundle follows these hierarchy conventions
to keep the directory structure navigable:

1. **Subdirectory = semantic group.** Group related concepts under a subdirectory
   when three or more concepts share a tag or parent type.

2. **No more than three levels deep.** `root/domain/subdomain/concept.md`.
   Deeper nesting degrades traversal. Flatten if you hit four levels.

3. **Stub concepts live in `stubs/`.** All `type: Stub` files go here until filled.
   When a stub is filled (content added, confidence > 0.50), ENRICHMENT_AGENT moves
   the file to its correct semantic subdirectory.

4. **Reports live in `reports/`.** All `type: Loop Health Report` and `type: Decay Report`
   files go here. Excluded from the main index.md sections; listed under `## Reports`.

5. **Archived concepts live in `archive/`.** All superseded concepts are moved here
   after supersession. They retain their frontmatter and body. They are excluded from
   active index.md sections but included in `## Archive` for auditability.

---

# Validation Rules

CONFORMANCE_AGENT checks these rules in addition to OKF v0.1 base conformance (§9):

| Rule | Check | Severity |
|---|---|---|
| V1 | Every concept's `type` is registered in this Ontology | ERROR |
| V2 | Every concept's `tags` are registered in this Ontology | WARNING |
| V3 | No concept has `confidence` without `confidence_sources` | WARNING |
| V4 | Every `type: Stub` concept is in the `stubs/` subdirectory | WARNING |
| V5 | Every `type: Inference` has `inferred_from` listing at least one source | ERROR |
| V6 | No concept has `superseded_by` without a reciprocal `supersedes` in the target | ERROR |
| V7 | Every contradiction comment `<!-- CONFLICT -->` has a corresponding LOG entry | WARNING |
| V8 | This `ontology.md` file has `memory_tier: semantic` and `confidence: 1.0` | ERROR |

---

# Deliverable Parity Contracts

> Most derived output never needs this section: `projections/` files are **regenerated in full**
> every time PROJECTION_AGENT runs, so they cannot silently drift. This section exists for a
> narrower, riskier case — a **hand-authored, self-contained interactive artifact** (an HTML/JS
> decision tool, a dashboard, a slide-deck generator, an embedded lookup table, etc.) that carries
> its **own denormalized snapshot** of one or more concept subdirectories, because it needs custom
> rendering PROJECTION_AGENT's flat-markdown output cannot produce. That snapshot is hand-edited,
> not regenerated — so the moment a concept is added, retired, or renamed and the deliverable is
> not touched in the same pass, it silently goes stale. Register a contract here **the first time**
> such a deliverable is built, and CONFORMANCE_AGENT will catch drift automatically from then on
> instead of relying on someone noticing.

**Format** — one row per deliverable that embeds a source-concept snapshot:

| Field | Meaning |
|---|---|
| `Contract ID` | Short slug identifying the contract. |
| `Deliverable file` | Path to the artifact, relative to bundle root (typically under `deliverables/`). |
| `Source scope` | The concept subdirectory, or a `type`/`tag` filter, being mirrored. |
| `Identity key` | How ONE record in the deliverable maps 1:1 to ONE source file (a lettered/numbered `id`, a filename slug, a title match…). CONFORMANCE_AGENT diffs on this key, not just a count, so it can name exactly which record is missing or extra — not just report "counts don't match". |
| `Severity` | `ERROR` (the deliverable ships broken or misleading to an end user/client) or `WARNING` (cosmetic drift only). Default to `ERROR` for anything client-facing. |

| Contract ID | Deliverable file | Source scope | Identity key | Severity |
|---|---|---|---|---|
| *(none at bundle initialisation — register the first time a hand-authored deliverable snapshots concept data; see worked example below)* | — | — | — | — |

**Worked example** (illustrative only — this is not a live contract in this seed ontology; shown
so a domain builder can copy the pattern exactly):

| Contract ID | Deliverable file | Source scope | Identity key | Severity |
|---|---|---|---|---|
| `scenario-decision-map` | `deliverables/app-1-7-trigger-test-decision-map.html` | `scenarios/scenario-*.md` (one row per file) | Scenario letter — the concept's `title: "Scenario X — …"` matched against the deliverable's embedded `id` field | ERROR |

This is the exact fix applied retroactively to the `privacy-act-okf` bundle after its
`scenarios/` directory grew to nine concepts (A–I) while its interactive decision-map deliverable
had silently stalled at seven (A–G) for several days — an *additive* new Scenario concept did not
read, on a first pass, like it triggered "update the deliverable", because the old instruction was
conditional ("if the new material changes scenarios…") rather than unconditional on any create/
retire event. See CHANGELOG.md [2.2.0] and AGENTS.MD §ENRICHMENT_AGENT / §CONFORMANCE_AGENT for
how this is now enforced unconditionally, at write time and at audit time, for every bundle built
from this kit — not just the one where the gap was first found.

---

# Source Coverage Contracts

> **Not the same problem as Deliverable Parity Contracts, above.** That section catches
> *concept → hand-authored deliverable* drift (a snapshot embedded in an HTML/JS artifact
> going stale after the source concepts change). This section catches a different failure:
> *source document → bundle* drift, where a named unit in the original source (a Box, Table,
> Figure, recurring callout, appendix, or cited case) was simply never transcribed into any
> concept file in the first place. There is no deliverable involved — the miss is in
> ENRICHMENT_AGENT's own INGEST/MAP pass, not in a downstream artifact. A bundle can be
> perfectly internally-conformant (every CHECK_1–8 passes) while still failing this, because
> none of those checks ever look back at the source document.
>
> **Enforced at ingestion time, not just audited afterwards.** AGENTS.MD §ENRICHMENT_AGENT's
> `STATE: INVENTORY` and `GATE_5-COVERAGE` make building this ledger a mandatory, blocking
> step of any SOURCE-DOCUMENT MODE ingestion — the pipeline cannot hand off to
> LINK_AGENT/LOG_AGENT while any ledger row is unresolved. CHECK_9 (AGENTS.MD
> §CONFORMANCE_AGENT) is the safety net for a bundle predating this mechanism, or a session
> that skipped STATE: INVENTORY — it is not the primary defence.

**Format** — one row per source document being tracked for bundle completeness:

| Field | Meaning |
|---|---|
| `Contract ID` | Short slug identifying the contract. |
| `Coverage ledger file` | Path to the `type: Coverage Ledger` concept enumerating every named unit in the source. |
| `Source document` | The source PDF/text being tracked (with version/date). |
| `Identity key` | How ONE row in the ledger maps to ONE structural unit in the source (a Box/Table/Figure number, a page-anchored callout label, an appendix letter). |
| `Severity` | `ERROR` if an uncaptured unit would misrepresent the source's scope to a reader relying on the bundle as complete (e.g. a director-facing checklist item, a safety procedure, a compliance clause); `WARNING` if cosmetic (e.g. a front-matter foreword). |

| Contract ID | Coverage ledger file | Source document | Identity key | Severity |
|---|---|---|---|---|
| *(none at bundle initialisation — register the first time a whole source document is ingested; see worked example below)* | — | — | — | — |

**Worked example** (illustrative only — this is not a live contract in this seed ontology; shown
so a domain builder can copy the pattern exactly):

| Contract ID | Coverage ledger file | Source document | Identity key | Severity |
|---|---|---|---|---|
| `directors-guide-coverage` | `errata/source-coverage-ledger.md` | *A Director's Guide to AI Governance* (AICD/HTI, v2, June 2026) | Box N / Table N / Figure N / page-anchored callout label / Appendix letter | ERROR |

This is the exact fix applied retroactively to the `directors-guide-ai-governance` bundle after
its 2026-07-03 canonical re-ingestion — despite a full sequential read of a 56-page source PDF —
still omitted four recurring "Questions for directors to ask" / "Governance red flags" boxes
entirely, plus three further named units (a "Ways boards can harness AI" box, an illustrative
example box, and a closing outlook section) that only surfaced once an exhaustive enumeration was
built after the fact. Root cause: a single self-review pass is correlated with its own blind
spots — it notices what looks substantively interesting and silently deprioritises what looks
repetitive or formulaic, even when the latter is real, required content. A second, independent
review caught the initial gap; building the ledger to close it then surfaced the rest
mechanically, without anyone re-reading the source a third time. See CHANGELOG.md [2.3.0] and
AGENTS.MD §ENRICHMENT_AGENT (`STATE: INVENTORY`, `GATE_5-COVERAGE`) / §CONFORMANCE_AGENT
(`CHECK_9`) for how this is now enforced unconditionally, at ingestion time and at audit time,
for every bundle built from this kit — not just the one where the gap was first found.

---

# ONTOLOGY_AGENT — Extension Protocol

When ENRICHMENT_AGENT encounters an unregistered `type` or `tag`, it does NOT silently
accept it. It triggers ONTOLOGY_AGENT:

```
AGENT: ONTOLOGY_AGENT
TRIGGER: Unregistered type or tag detected during ENRICHMENT or CONFORMANCE

ACTIONS:
  1. Propose the new type or tag entry in the correct section of ontology.md.
  2. Include: name, description, typical use, example concept.
  3. Write the proposed addition as a <!-- PROPOSED: --> comment at the bottom
     of the appropriate section in ontology.md.
  4. Set `review_required: true` in ontology.md frontmatter.
  5. LOG_AGENT records: **Ontology Proposal**: [type/tag name] — awaiting approval.
  6. HALT. Do not write the concept using the unregistered type until approved.

APPROVAL:
  A human (or agent with explicit authority) removes the <!-- PROPOSED: --> comment
  and promotes the entry to the active table. Removes `review_required: true`.
  LOG_AGENT records: **Ontology Extension**: [type/tag name] — approved and registered.

REJECTION:
  Human removes the <!-- PROPOSED: --> comment without promoting it.
  ENRICHMENT_AGENT maps the rejected concept to the nearest registered type.
```

---

# Deprecated Types

Types that were once valid but are no longer in use. Agents encountering these
types in existing concept files should flag for migration, not auto-migrate.

| Deprecated Type | Replaced By | Migration Note |
|---|---|---|
| *(none at initialisation)* | — | — |

---

# Ontology Version History

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-06-19 | Initial ontology for bundle bootstrap kit |
| 0.2 | 2026-07-03 | Added **§Deliverable Parity Contracts** — an opt-in registry for hand-authored interactive deliverables that embed a denormalized snapshot of a concept subdirectory. Generalises a bundle-specific fix (`privacy-act-okf` scenario/decision-map drift) into a reusable kit pattern. Empty template + one illustrative worked example; no live contract in this seed ontology. Paired with AGENTS.MD changes enforcing it at write time (ENRICHMENT_AGENT) and audit time (CONFORMANCE_AGENT CHECK_7). No new types/tags. |
| 0.3 | 2026-07-03 | Added type `Coverage Ledger` (Memory & Governance Types) and tag `coverage` (System Tags), plus new **§Source Coverage Contracts** — a *different* completeness mechanism from §Deliverable Parity Contracts: that section catches concept→deliverable drift; this one catches source-document→bundle omission, which involves no deliverable at all. Generalises a bundle-specific fix (`directors-guide-ai-governance` re-ingestion silently omitting four recurring content boxes despite a full sequential read) into a reusable kit pattern. Empty template + one illustrative worked example; no live contract in this seed ontology. Paired with AGENTS.MD changes enforcing it at ingestion time (ENRICHMENT_AGENT `STATE: INVENTORY` + `GATE_5-COVERAGE`, mandatory in the new SOURCE-DOCUMENT MODE) and audit time (CONFORMANCE_AGENT CHECK_9). See CHANGELOG.md [2.3.0]. |
