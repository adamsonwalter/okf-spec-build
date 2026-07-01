---
name: okf-kinetic-ontology-mapper
description: OKF-customised kinetic ontology mapper. Decomposes any concept, regulation or system into gates, thresholds, exemptions and feedback loops, imports battle-tested cross-domain patterns, and emits OKF-conformant concept files whose links use the parent kit's ten-relationship taxonomy. Writes validated patterns back to the governed pattern-library OKF bundle (Seam B), so compounding rides the kit's conformance, index, log and supersession instead of a hand-rolled log. Enforces the invisibility contract on all client output. This is the customised, OKF-coupled sibling of the general kinetic-ontology-mapper — use it inside an OKF estate; use the general one elsewhere.
version: 1.0
author: Walter Adamson
date: 2026-06-24
---

<!-- ───────────── VERSION HISTORY ─────────────
  1.0  2026-06-24  Forked from general kinetic-ontology-mapper v1.1. Relationship verbs
                   mapped to the OKF taxonomy via RELATIONSHIP-CROSSWALK.md; outputs emit
                   OKF-conformant frontmatter; pattern library is now a governed OKF
                   sub-bundle (Seam B) written back via the ENRICHMENT→LINK→INDEX→LOG
                   pipeline rather than a flat compounding log.
  ──────────────────────────────────────────────-->

# OKF Kinetic Ontology Mapper (customised, OKF-coupled)

**Version:** 1.0 · **Date:** 2026-06-24

This is the **OKF-customised** mapper. It is a deliberate, decoupled sibling of the
general-purpose `kinetic-ontology-mapper`: same analytical engine, but it speaks OKF and
compounds inside an OKF bundle. The duplication is intentional — a specialised mapper for
the OKF estate yields cleaner, conformant output than bending the general one each time.

## What is different from the general mapper

1. **Relationships are OKF relationships.** The mapper's native verbs (requires, gates,
   exempts, triggers, compounds) are translated to the parent kit's ten-relationship
   taxonomy via [RELATIONSHIP-CROSSWALK.md](RELATIONSHIP-CROSSWALK.md). No new relationship
   words are invented; gate nuance is preserved in prose, per OKF convention.
2. **Output is OKF-conformant.** Every artifact the mapper writes carries valid frontmatter
   with a registered `type` (`Pattern`, `Action Type`, `Gate`, `Concept`, `Decision`), so it
   drops straight into a bundle and passes CONFORMANCE V1/V2/V4.
3. **Compounding is governed (Seam B).** Validated patterns are written to
   [pattern-library/](pattern-library/) — a conformant OKF sub-bundle — through the parent
   `ENRICHMENT → LINK → INDEX → LOG` pipeline. The library inherits conformance checks,
   bidirectional links, index regeneration, supersession and git history for free.

## Decoupling contract (how to update without fragility)

The only coupling surface is [RELATIONSHIP-CROSSWALK.md](RELATIONSHIP-CROSSWALK.md) plus the
type registry in [pattern-library/ontology.md](pattern-library/ontology.md). As long as
those stay aligned with the parent `../ontology.md`, this mapper and the kit update
independently. The crosswalk declares `crosswalk_version` against the parent `okf_version`;
CONFORMANCE checks the two are compatible. Change the contract in one place, not across files.

## Core workflow (unchanged engine, OKF outputs)

**Task 1 — Structural decomposition.** Break the concept into entities, gates, thresholds,
exemptions, feedback loops. Emit an internal map as a `type: Concept` file.

**Task 2 — Pattern import.** Pull 2–3 patterns from [pattern-library/](pattern-library/)
(or discover new ones) that share gate logic, thresholds, exemptions, or compounding.

**Task 3 — Kinetic mapping.** Map components one-to-one; define governed `Action Type`
files; design the writeback. **All links use OKF relationship words from the crosswalk.**

**Task 4 — Client output (invisibility).** Produce the client-clean deliverable. Apply the
Invisibility Gate — no internal terms, no method language, client's perspective only.

## Decidable gates (same four)

Reuse the general mapper's gate set — structural fidelity, kinetic-pattern quality,
invisibility, actionability & compounding — with one addition: a passing run that discovers
a new pattern MUST write it back to `pattern-library/` via the OKF pipeline, not a flat log.

## Invisibility contract (highest precedence)

Identical to the general mapper: strip every internal method, framework and process term
from any client-facing output. The reader sees only their own world — risks, decisions,
actions, outcomes. The OKF machinery, like all method, stays invisible.

## Folder structure

```
ontology-mapper/                         # optional, decoupled in-repo module
├── SKILL.md                             # this file
├── RELATIONSHIP-CROSSWALK.md            # the coupling contract (mapper verbs → OKF taxonomy)
├── CHANGELOG.md
├── outputs/                             # runtime client + internal artifacts
└── pattern-library/                     # Seam B — a conformant OKF sub-bundle
    ├── ontology.md                      # registers Pattern, Action Type, Gate
    ├── index.md                         # no frontmatter except okf_version
    ├── log.md                           # governed writeback record
    └── *.md                             # Pattern concept files (OKF frontmatter + links)
```

This module is opt-in. If `ontology-mapper/` is absent from a bundle, the core kit is
unaffected — exactly the CORE-vs-OPTIONAL decoupling the kit already uses for `optional/`.
