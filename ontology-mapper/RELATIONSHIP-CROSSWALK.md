---
type: Reference
title: Mapper-to-OKF Relationship Crosswalk
description: Maps the kinetic mapper's native gate-logic verbs onto the parent kit's ten-relationship taxonomy so the customised mapper emits OKF-conformant links.
okf_version: "0.1"
tags: [governance, system]
timestamp: 2026-06-24T00:00:00Z
---

# Mapper → OKF Relationship Crosswalk

This is the single coupling surface between the mapper and the OKF kit. The general
mapper speaks in gate-logic verbs (requires, gates, exempts, triggers, compounds). The
OKF kit has a fixed ten-relationship taxonomy (`../ontology.md`). The **OKF-customised
mapper writes only OKF relationships**; this table is how it translates. Keep this file
versioned — it is the contract. If the parent taxonomy changes, change it here once.

## The mapping

| Mapper verb (native) | OKF relationship | Prose signal to use | Notes |
|---|---|---|---|
| requires / depends on | `depends-on` | "requires", "cannot run without" | Direct 1:1. |
| implements / follows | `implements` | "implements", "is an instance of" | Direct 1:1. |
| is a limb of / component of | `part-of` | "is part of", "component of" | Each conjunctive limb is part-of the test. |
| gates on (materiality) | `governs` | "gates on", "constrains whether…applies" | A gate constrains the downstream; keep "gates on X" in the prose. |
| exempts / safe-harbour | `governs` | "exempts via", "is carved out by" | An exemption governs applicability; annotate "exempts". |
| triggers | `depends-on` (reversed) | "triggers", "fires when" | Downstream action depends-on the trigger condition. |
| compounds / feeds back | `derived-from` | "derived from", "enriched by" | Compounded/written-back state is derived-from prior + outcome. |
| supersedes / replaces | `supersedes` | "supersedes", "replaces" | Direct 1:1; reciprocal `superseded_by` only under T3. |
| references / see | `references` | "see", "documented in" | Direct 1:1. |
| contradicts | `contradicts` | "conflicts with", "disputes" | Direct 1:1. |
| related / associated | `related-to` | "related", "associated" | Fallback for non-directional links. |
| authored / maintained by | `authored-by` | "authored by", "maintained by" | Direct 1:1. |

## Rules

1. **Three verbs have no clean 1:1** — `gates`, `exempts`, `triggers`. They collapse onto
   `governs` or `depends-on`. The lost nuance is preserved in the **prose signal**, exactly
   as OKF intends (the relationship label lives in natural language, never in link syntax).
2. **No forking the taxonomy.** The customised mapper must not invent new relationship
   words. If a genuine gap appears, raise it through the parent kit's `ONTOLOGY_AGENT`
   extension protocol — do not add it here unilaterally.
3. **Types, not just relationships:** mapper outputs map to OKF types as
   `Pattern`, `Action Type`, `Gate` (registered in `pattern-library/ontology.md`); an
   internal ontology map becomes a `Concept`; a recorded determination becomes a `Decision`.

## Contract version

`crosswalk_version: 1` targeting parent `okf_version: 0.1`. Bump on any change to either
the mapper verbs or the parent taxonomy; CONFORMANCE then checks the two are compatible.
