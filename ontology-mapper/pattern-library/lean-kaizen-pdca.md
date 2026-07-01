---
type: Pattern
title: Lean Kaizen / PDCA
description: Governed compounding backbone — Plan-Do-Check-Act with andon materiality stop and standard-work writeback, imported from lean manufacturing.
resource: https://en.wikipedia.org/wiki/PDCA
tags: [pattern, compounding, materiality, exemption]
timestamp: 2026-06-24T00:00:00Z
---

# Lean Kaizen / PDCA

Structural source for the compounding / writeback limb the other patterns assume but
do not govern.

## Structural Match
- **Compounding loop (primary):** every PDCA cycle updates "standard work" — the baseline ratchets up.
- **Materiality gate:** the andon cord stops the line for defects above a severity; below it, log and continue.
- **Tolerance:** control limits define a tolerated band; only excursions intervene.
- **Defect prevention:** standard work + poka-yoke cut false negatives at source.

## Kinetic Actions
- Improvement idea → `plan-do-check-act` as a bounded, measured experiment.
- Defect above threshold → `stop-and-escalate`.
- Validated improvement → `update-standard-work` (the compounding writeback).

## OKF Relationship Map
- This pattern **governs** the writeback discipline of any self-improving ontology.
- A new standard is **derived-from** a validated experiment and **supersedes** the prior standard.
- The andon stop **depends-on** crossing the materiality threshold.
- Supplies the governance the compounding loops in [Immune T-Cell Two-Signal](immune-t-cell-two-signal.md) and [Notifiable Disease Surveillance](notifiable-disease-surveillance.md) assume — **related-to** both.

## Transfer Notes
Pair with a gating pattern (immune or customs) for the conjunctive limbs; PDCA stops
"compounding" from degenerating into uncontrolled drift.
