---
type: Ontology
title: Pattern Library Ontology
description: Type registry, relationship taxonomy, and tag vocabulary for the kinetic pattern library — a conformant OKF sub-bundle governed by the parent kit's contract.
okf_version: "0.1"
timestamp: 2026-06-24T00:00:00Z
tags: [ontology, system, governance]
---

> This ontology governs the pattern-library bundle only. It REUSES the parent kit's
> relationship taxonomy verbatim (see ../../ontology.md) so that patterns link with the
> same semantics as every other concept in the OKF estate. It adds the project-specific
> types the mapper needs (`Pattern`, `Action Type`, `Gate`). All agents MUST consult it
> before creating a new `type` or tag in this bundle.

---

# Type Registry

## Project-Specific Types (this bundle)

| Type | Description | Typical Body Sections |
|---|---|---|
| `Pattern` | A transferable structural + kinetic pattern imported from an unrelated domain. | Structural Match, Kinetic Actions, OKF Relationship Map, Transfer Notes |
| `Action Type` | A governed action the ontology can execute (inputs, outputs, writeback effect). | Purpose, Inputs, Outputs, Governance, Writeback |
| `Gate` | A decidable validation checkpoint with a pass criterion checkable from material in context. | Purpose, Checklist, Pass Criterion |

## Core Types (inherited from parent kit)

`Concept`, `Playbook`, `Decision`, `Reference`, `Process`, `System`, and the
governance types are defined in `../../ontology.md` and are valid here without redefinition.

---

# Relationship Taxonomy (inherited — do not fork)

This bundle uses the parent kit's ten relationships unchanged:
`depends-on`, `implements`, `contradicts`, `supersedes`, `references`,
`related-to`, `part-of`, `derived-from`, `authored-by`, `governs`.

The mapper's native gate-logic verbs map onto these — see
`../RELATIONSHIP-CROSSWALK.md`. Patterns MUST annotate links using the OKF
relationship word in the surrounding prose (never in the link syntax).

---

# Tag Taxonomy

## System Tags (reserved — inherited)
`system`, `governance`, `stub`, `review-required`, `archived`.

## Domain Tags (this bundle)

| Tag | Meaning |
|---|---|
| `pattern` | A transferable kinetic pattern. |
| `gate-logic` | Concerns conjunctive / AND-gate structure. |
| `materiality` | Concerns a threshold or "significant effect" gate. |
| `exemption` | Concerns a tolerance / safe-harbour mechanism. |
| `compounding` | Concerns a feedback / writeback loop. |
| `certainty` | Concerns graded confidence before action. |

---

# Validation Rules (core profile)

This bundle runs the parent kit's CORE conformance only (T1/T2):

| Rule | Check | Severity |
|---|---|---|
| V1 | Every concept's `type` is registered (here or in parent `ontology.md`) | ERROR |
| V2 | Every concept's `tags` are registered | WARNING |
| V4 | Every `type: Stub` concept is in a `stubs/` subdirectory | WARNING |

T3 rules (V3, V5–V8) are inert unless the parent `optional/` layer is loaded.

---

# Ontology Version History

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-06-24 | Initial pattern-library ontology; registers Pattern, Action Type, Gate. |
