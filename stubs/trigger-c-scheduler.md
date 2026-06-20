---
type: Stub
title: Trigger C Activation — External Scheduler
description: Known gap. The time-based decay/staleness trigger (FEEDBACK_LOOP.MD §Trigger C) has no automatic activator and must be wired to an external scheduler.
memory_tier: working
confidence: 0.0
confidence_sources: 0
review_required: true
tags: [system, governance, review-required]
timestamp: 2026-06-19T00:00:00Z
---

# Trigger C Activation — External Scheduler

> ⚠️ STUB: This is a known, deliberately-tracked gap, not a finished concept.
> It exists so the gap is visible rather than forgotten. Fill it when Trigger C
> is actually wired to a scheduler.

## The Gap

The feedback loop has four triggers (FEEDBACK_LOOP.MD §TRIGGER TYPES). Three are
reactive and fire automatically while an agent session is running:

- **A — Input-Triggered**: a human/agent supplies new content.
- **B — Query-Triggered**: a CONSUMPTION_AGENT answer yields a new inference.
- **D — Contradiction-Triggered**: new input conflicts with an existing concept.

**C — Time-Triggered** is the exception. It governs decay and staleness sweeps:

- `timestamp` older than 90 days on a `memory_tier: semantic` concept
- `confidence` below 0.40
- any concept flagged `stale: true`

Nothing in the bundle wakes itself up. The bundle is a passive file set; it has no
clock. Trigger C therefore only runs when an agent next happens to operate on the
bundle and chooses to run a sweep. Left alone, stale and low-confidence concepts
accumulate silently — the decay model exists but never executes.

## What "Filled" Looks Like

This stub is resolved when BOTH of the following exist:

1. **An external scheduler** (e.g. a weekly scheduled task) that opens the bundle
   and instructs OKF_ORCHESTRATOR to run a Trigger C sweep, producing a
   `type: Decay Report` in `reports/`.
2. **A documented activation contract** — a `## Trigger C Activation` section added
   to FEEDBACK_LOOP.MD specifying the cadence, the exact instruction passed to the
   orchestrator, and where the decay report is written.

## Acceptance Criteria

- [ ] Scheduler created (cadence chosen: weekly suggested).
- [ ] Sweep instruction defined and tested against a bundle with ≥1 stale concept.
- [ ] `reports/` receives a dated Decay Report on each run.
- [ ] FEEDBACK_LOOP.MD documents the activation contract.
- [ ] On completion: change `type` from `Stub` to `Playbook`, set
      `confidence` ≥ 0.50, remove `review_required`, move this file out of `stubs/`
      into its semantic home, and log a `**Self-Improvement** [Gap Closed]` entry.

## Why a Stub and Not a Decision Yet

No scheduler has been chosen or wired. Recording this as a `confidence: 0.0` stub
makes the gap a first-class, indexed object (per LLM_WIKI.MD §GAP-FINDING) so it
surfaces in conformance sweeps and the root index instead of living only in chat.
