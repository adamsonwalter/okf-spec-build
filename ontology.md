---
type: Ontology
title: Bundle Ontology
description: Single source of truth for all concept types, relationship semantics, tag taxonomy, and validation rules in this OKF bundle.
memory_tier: semantic
confidence: 1.0
okf_version: "0.1"
timestamp: 2026-06-19T00:00:00Z
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

| Type | Description | Created By |
|---|---|---|
| `Ontology` | This file. The bundle's type and relationship registry. | Human / ONTOLOGY_AGENT |
| `Stub` | A placeholder for a known gap. Confidence 0.0. | ENRICHMENT_AGENT (gap-finder) |
| `Inference` | A relationship or claim derived by an agent from existing concepts. | CONSUMPTION_AGENT |
| `Agent Instruction` | An instruction file for agent behavior (ALL CAPS .md files). | Human |
| `Loop Health Report` | Periodic diagnostic snapshot of bundle health metrics. | LOG_AGENT |
| `Decay Report` | List of stale, isolated, or low-confidence concepts. | CONFORMANCE_AGENT |
| `Contradiction Record` | A logged contradiction event and its resolution. | ENRICHMENT_AGENT |

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
Unregistered tags trigger a Type Orphan gap flag (see LLM_WIKI.MD §GAP-FINDING).

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
