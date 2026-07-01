---
type: Pattern
title: Notifiable Disease Surveillance
description: Graded certainty (suspected/probable/confirmed) with deadline-bound mandatory action and sentinel escalation, imported from public health.
resource: https://en.wikipedia.org/wiki/Notifiable_disease
tags: [pattern, certainty, materiality, compounding]
timestamp: 2026-06-24T00:00:00Z
---

# Notifiable Disease Surveillance

Structural source for obligations that scale with certainty or severity and carry
reporting deadlines.

## Structural Match
- **Graded conjunctive definition:** suspected / probable / confirmed via explicit criteria combinations.
- **Materiality gate:** notification is mandatory only for listed conditions or above a severity threshold.
- **Tolerance:** endemic baseline is tolerated; only exceedance triggers action.
- **Compounding:** confirmed cases recalibrate baselines and case definitions.

## Kinetic Actions
- Suspected → `monitor-and-collect`.
- Probable/confirmed above threshold → `mandatory-notify` within a fixed window.
- Baseline exceedance → `escalate-to-sentinel-review`.
- Outcome → `update-baseline` / `refine-case-definition`.

## OKF Relationship Map
- This pattern **governs** any obligation with deadline-bound, certainty-graded action.
- The notify action **depends-on** reaching the confidence/severity threshold.
- Recalibrated baselines are **derived-from** confirmed outcomes.
- Extends [Immune T-Cell Two-Signal](immune-t-cell-two-signal.md) — **related-to** — by adding graded certainty and time-bound action to a static gate.

## Transfer Notes
Use when an obligation only bites above a threshold *and* within a deadline, and when
staged certainty before a costly action is valuable.
