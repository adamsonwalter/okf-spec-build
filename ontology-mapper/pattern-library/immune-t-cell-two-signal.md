---
type: Pattern
title: Immune T-Cell Two-Signal Activation
description: Conjunctive AND-gate with a materiality co-stimulator and an active tolerance action, imported from adaptive immunology.
resource: https://en.wikipedia.org/wiki/T_cell#Activation
tags: [pattern, gate-logic, materiality, exemption, compounding]
timestamp: 2026-06-24T00:00:00Z
---

# Immune T-Cell Two-Signal Activation

Structural source for any obligation that fires only when two or more independent
conditions co-occur.

## Structural Match
- **AND-gate:** activation needs Signal 1 (antigen) *and* Signal 2 (co-stimulation); either alone is insufficient.
- **Materiality gate:** co-stimulation is a separate, modulatable "does this matter enough to act" signal.
- **Active tolerance:** Signal 1 without Signal 2 drives anergy — tolerance is an applied action, not passive silence.
- **Compounding:** activated clones persist as memory, so future responses are faster.

## Kinetic Actions
- Signal 1 only → `induce-tolerance` (park as "seen, not actioned").
- Signal 1 + Signal 2 → `activate-and-clone` (commit, escalate).
- Outcome → memory clones (the writeback that compounds).

## OKF Relationship Map
- This pattern **governs** any multi-limb obligation test (it constrains when action is allowed).
- Each limb is **part-of** the conjunctive gate.
- The materiality signal **depends-on** situational context.
- Future responses are **derived-from** retained memory of prior encounters.
- Pairs with [Substantial Transformation (Customs)](substantial-transformation-customs.md) — **related-to** — when one limb is an undefined "substantial" term.

## Transfer Notes
Best when the source concept has a clean conjunctive structure and you need a principled
"one limb satisfied, not all" action rather than silently dropping the case.
