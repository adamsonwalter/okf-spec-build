# FEEDBACK_LOOP.MD — Continuous Synthesis Loop
# OKF Operating Bundle | Companion to AGENTS.MD and LLM_WIKI.MD
# Convention: ALL CAPS filenames are agent instructions, not OKF concept documents.
# Do NOT add YAML frontmatter to this file. Do NOT index this file in index.md.

---

## PURPOSE

This file defines the continuous synthesis loop that keeps the OKF knowledge
bundle current as new inputs arrive over time. It governs WHEN agents trigger,
HOW they compare new knowledge against existing knowledge, and HOW contradictions,
confirmations, and gaps are resolved.

Without this loop, the bundle is a write-once archive.
With it, the bundle is a self-updating knowledge graph.

---

## LOOP OVERVIEW

```
┌─────────────────────────────────────────────────────┐
│                   SENSE                             │
│   New input arrives (document, query result,        │
│   inference from CONSUMPTION_AGENT, time trigger)   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  SYNTHESIZE                         │
│   ENRICHMENT_AGENT extracts concepts.               │
│   For each concept: load existing node if present.  │
│   Compute semantic delta: NEW / CONFIRM / CONTRADICT│
└──────────────────────┬──────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐  ┌─────▼────┐  ┌────▼──────┐
    │  NEW    │  │ CONFIRM  │  │ CONTRADICT│
    │ Create  │  │ +score   │  │ Resolve   │
    │ concept │  │ +promote │  │ protocol  │
    └────┬────┘  └─────┬────┘  └────┬──────┘
         └─────────────┼─────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   MUTATE                            │
│   Write/update concept files.                       │
│   LINK_AGENT injects/updates cross-links.           │
│   INDEX_AGENT rebuilds affected index.md files.     │
│   LOG_AGENT appends mutation record.                │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  VALIDATE                           │
│   CONFORMANCE_AGENT spot-checks mutated files.      │
│   All new concepts have `type`. No orphaned links.  │
│   Confidence scores updated.                        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                    AWAIT                            │
│   Bundle is stable. Await next trigger.             │
│   Passive: gap-finder runs, flags stale nodes.      │
└─────────────────────────────────────────────────────┘
```

---

## TRIGGER TYPES

The loop activates on four trigger classes. Each class routes differently.

### Trigger A — Input-Triggered (primary)
**Condition:** A human or upstream agent supplies new content for ingestion.
**Route:** Full pipeline: SENSE → SYNTHESIZE → MUTATE → VALIDATE → AWAIT.
**Examples:** Research document, meeting notes, web fetch result, file upload.

### Trigger B — Query-Triggered (compounding)
**Condition:** CONSUMPTION_AGENT generates an answer that contains a synthesis,
inference, or relationship not already represented in the bundle.
**Route:** CONSUMPTION_AGENT passes the inference to OKF_ORCHESTRATOR.
OKF_ORCHESTRATOR runs a targeted ENRICHMENT cycle for the inferred concept only.
**Frontmatter on inferred concepts:**
```yaml
type: Inference
confidence: 0.55
inferred_from: [/path/to/source-a.md, /path/to/source-b.md]
```

### Trigger C — Time-Triggered (decay + staleness)
**Condition:** LOG_AGENT or a scheduled check detects:
- Any concept with `timestamp` older than 90 days and `memory_tier: semantic`
- Any concept with `confidence` below 0.40
- Any concept flagged `stale: true`
**Route:** CONFORMANCE_AGENT generates a staleness report.
OKF_ORCHESTRATOR surfaces it for human review or triggers a targeted re-enrichment
if a refresh source is available.
**Do NOT auto-delete stale concepts.** Flag only. Human decides.

### Trigger D — Contradiction-Triggered (resolution)
**Condition:** During SYNTHESIZE, a new input directly contradicts an existing concept.
**Route:** CONTRADICTION_RESOLVER sub-protocol (see §CONTRADICTION).
**Do NOT proceed to MUTATE until contradiction is resolved.**

---

## SYNTHESIZE — SEMANTIC DELTA CLASSIFICATION

When ENRICHMENT_AGENT loads an existing concept to compare against new input,
it classifies the delta using these three categories:

### Delta: NEW
The extracted concept has no match in BUNDLE_MANIFEST.
Action: MUTATE_CREATE (per AGENTS.MD). Set `confidence: 0.50`.

### Delta: CONFIRM
The extracted concept matches an existing concept and the new input:
- Does not contradict any frontmatter field or body claim, AND
- Adds information OR simply re-states what exists.

Action:
1. Increment `confidence_sources` by 1.
2. Recalculate `confidence` per LLM_WIKI.MD scoring rules.
3. If confidence crosses a tier threshold, update `memory_tier`.
4. Append any net-new body content to the existing concept under a
   `## [Source Date] Update` heading. Do not rewrite existing sections.
5. Update `timestamp` to now.

### Delta: CONTRADICT
The extracted concept matches an existing concept but the new input directly
contradicts a claim, fact, or relationship in the existing concept.
Action: Route to CONTRADICTION_RESOLVER. Do not write to file yet.

---

## CONTRADICTION RESOLVER

This sub-protocol runs inside the SYNTHESIZE state before any file mutation.

### Step 1 — Classify the contradiction

| Type | Description | Example |
|---|---|---|
| FACTUAL | A specific claim conflicts (dates, numbers, names) | "Founded 2010" vs "Founded 2012" |
| RELATIONAL | A link between two concepts is disputed | A→B exists but new input says A→C |
| CATEGORICAL | The `type` of a concept is disputed | `type: API Endpoint` vs `type: Webhook` |
| SUPERSESSION | New input is explicitly more recent and replaces old | Updated spec, revised policy |

### Step 2 — Apply resolution rule

**FACTUAL contradiction:**
- Compare `timestamp` of new input vs. existing concept's `timestamp`.
- If new input is provably more recent: accept new input. Flag old claim with
  `<!-- SUPERSEDED CLAIM: [old value] — replaced [date] -->`.
- If timestamps are equal or unclear: inject CONFLICT comment in both versions.
  Set `review_required: true`. Do not change confidence. Await human resolution.

**RELATIONAL contradiction:**
- Do not remove the existing link.
- Add the new link as an alternative.
- Annotate both links:
  ```
  [Concept B](/path/b.md) <!-- DISPUTED: see also [Concept C](/path/c.md) -->
  ```
- Set `review_required: true` on both concept files.

**CATEGORICAL contradiction:**
- Do not change `type` until resolved.
- Add to frontmatter:
  ```yaml
  type_disputed: true
  type_alternatives: ["API Endpoint", "Webhook"]
  review_required: true
  ```

**SUPERSESSION:**
- Invoke the Supersession Protocol from LLM_WIKI.MD.
- Old concept is archived. New concept is created. Links updated.

### Step 3 — After resolution
- Remove `review_required: true` from frontmatter.
- Update confidence per LLM_WIKI.MD rules.
- LOG_AGENT records `**Contradiction Resolved**` with both concept paths.

---

## KNOWLEDGE DECAY MODEL

Knowledge in the bundle is not static. Agents apply a passive decay model
during Trigger C (time-triggered) sweeps.

### Decay Signals

| Signal | Frontmatter marker | Threshold |
|---|---|---|
| Not updated | `stale: true` | `timestamp` > 90 days |
| Not linked to by anything | `isolated: true` | 0 incoming links |
| Low confidence | `review_required: true` | `confidence < 0.40` |
| Superseded | `memory_tier: archived` | `superseded_by` present |

### Decay Response Rules
- Decay signals are **flags only**. Nothing is deleted automatically.
- CONFORMANCE_AGENT includes all flagged concepts in its decay report.
- The report is a concept file: `type: Decay Report`, written to `reports/` subdirectory.
- Agents surface the report to the human on next interaction.

---

## MULTI-AGENT COORDINATION RULES

When multiple agents or sessions operate on the same bundle concurrently:

1. **Claim files before mutating.** Before ENRICHMENT_AGENT writes to a concept
   file, it checks for a `_lock` comment at the top of the file:
   ```
   <!-- LOCKED by [agent-id] at [timestamp] -->
   ```
   If locked, queue the mutation. Do not write over a lock.

2. **Release locks after write.** Remove the `<!-- LOCKED -->` comment after
   the file is written and GATE_4 passes.

3. **Shared vs. private scope.**
   - Concepts in the main bundle are shared across all agents.
   - Working-tier concepts MAY be prefixed with the agent's session ID
     (e.g., `session-abc123-hypothesis.md`) until promoted to Episodic.
   - Promoted concepts lose the session prefix and move into the main bundle.

4. **LOG_AGENT is the authority.** In any dispute about ordering, the
   `log.md` timestamp sequence is the canonical record of what happened first.

---

## SELF-IMPROVEMENT EVENTS

Self-improvement is distinct from mutation. A concept being updated is not
self-improvement. The wiki has self-improved when it becomes MORE ACCURATE,
MORE CONNECTED, or MORE CERTAIN than it was before — without a human supplying
the new fact directly.

LOG_AGENT MUST record a `**Self-Improvement**` entry for each of the following
events. These entries are the evidentiary record that the wiki evolved.

| Event | Definition | LOG entry format |
|---|---|---|
| **Tier Promotion** | A concept's `memory_tier` advances (Working→Episodic, Episodic→Semantic) | `**Self-Improvement** [Tier Promotion]: [concept](path) promoted from [old] to [new] — confidence [score]` |
| **Inference Added** | CONSUMPTION_AGENT derived a new concept not present in any source input | `**Self-Improvement** [Inference]: [concept](path) derived from [source-a](path) + [source-b](path)` |
| **Contradiction Resolved** | A disputed concept reached resolution, increasing accuracy | `**Self-Improvement** [Contradiction Resolved]: [concept](path) — [old claim] replaced by [new claim]` |
| **Stub Filled** | A `type: Stub` concept was populated with real content | `**Self-Improvement** [Gap Closed]: [concept](path) — stub filled from [source]` |
| **Ontology Extended** | ONTOLOGY_AGENT registered a new type or tag from observed content | `**Self-Improvement** [Ontology Extended]: type "[new type]" registered — first seen in [concept](path)` |
| **Link Density Increase** | A previously isolated concept gained two or more cross-links | `**Self-Improvement** [Graph Densified]: [concept](path) connected to [n] nodes — was isolated` |
| **Confidence Threshold Crossed** | A concept's confidence crosses 0.70 or 0.90 for the first time | `**Self-Improvement** [Confidence Threshold]: [concept](path) crossed [0.70/0.90] — now [score]` |

These entries appear in `log.md` alongside standard mutation entries.
They are ALSO aggregated into the `reports/wiki-evolution.md` report (see below).

---

## WIKI EVOLUTION REPORT

`reports/wiki-evolution.md` is a dedicated, auto-maintained concept that gives
a human-readable answer to: **"how has this wiki improved over time?"**

```yaml
---
type: Loop Health Report
title: Wiki Evolution
description: Chronological record of all self-improvement events in this bundle.
memory_tier: semantic
timestamp: <auto-updated on every write>
tags: [system, governance]
---
```

### Body format

```
# Wiki Evolution

## Summary

| Metric | Value |
|---|---|
| Total self-improvement events | N |
| Tier promotions | N |
| Inferences added | N |
| Contradictions resolved | N |
| Stubs filled | N |
| Ontology extensions | N |
| Confidence thresholds crossed | N |
| Graph densification events | N |
| Bundle started | YYYY-MM-DD |
| Last self-improvement | YYYY-MM-DD |

## Event Log (newest first)

### YYYY-MM-DD

* [Tier Promotion] [concept](path) promoted Working→Episodic — confidence 0.72
* [Inference] [concept](path) derived from [source-a] + [source-b]

### YYYY-MM-DD

* [Ontology Extended] type "Case Study" registered — first seen in [concept](path)
```

LOG_AGENT appends to `reports/wiki-evolution.md` every time a self-improvement
event is recorded. The Summary table is recalculated on each write.

---

## FEEDBACK LOOP HEALTH METRICS

LOG_AGENT tracks these metrics in a `reports/loop-health.md` concept:

```yaml
type: Loop Health Report
timestamp: <auto>
```

| Metric | Description |
|---|---|
| `concepts_created_total` | Running count of all created concepts |
| `concepts_updated_total` | Running count of all updated concepts |
| `concepts_archived_total` | Running count of all superseded concepts |
| `contradictions_resolved` | Count of contradiction events resolved |
| `contradictions_pending` | Count of unresolved contradictions (review_required) |
| `stale_concepts` | Count of concepts with `stale: true` |
| `stub_concepts` | Count of concepts with `type: Stub` |
| `avg_confidence` | Mean confidence score across all active concepts |
| `isolated_concepts` | Count of concepts with zero links |
| `loop_cycles` | Total number of SENSE→AWAIT cycles completed |

Update `reports/loop-health.md` on every LOG step. This file is the
diagnostic instrument for the bundle's knowledge health over time.
