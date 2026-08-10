---
type: Reference
title: OKF Dialect — How This Kit Relates To Google OKF v0.2
description: Authoritative note on where this kit tracks the Google spec, where it writes more than the spec requires, and which divergences are debt to pay rather than choices to keep.
tags: [governance, conformance, divergence]
okf_version: "0.2"
timestamp: 2026-08-10
---

## Version history
- 2026-06-24 — v1.0 — Initial divergence note. Separates spec floor from kit dialect; flags the read/write asymmetry; reclassifies the runtime cognitive layer as optional.
- 2026-08-10 — v2.0 — Re-based on **OKF v0.2**, which supersedes v0.1. Divergences are now sorted into three classes: superseded-field debt (fix), additive extension (keep — the spec blesses these), and producer-side strictness (keep, but never call it conformance). Section references updated: conformance moved from §9 to §11.

---

# The spec moved. This document tracks v0.2.

**OKF v0.2 was published on 2026-07-24** (`GoogleCloudPlatform/knowledge-catalog` PR #227)
and **supersedes v0.1** — §13 says so in terms. This kit was written against v0.1 and this
note previously described that relationship. Everything below is now stated against v0.2.

The version matters because v0.2 is not merely additive. It retires two things this kit
uses (§13.1), and it answers, in the format itself, two questions this kit had to invent
its own machinery for: *how much should I trust this* and *is it still true*.

**The floor is unchanged.** A bundle is conformant with v0.2 (§11) if every non-reserved
`.md` file has parseable YAML frontmatter, every frontmatter has a non-empty `type`, and
`index.md` / `log.md` follow §8 and §9. `type` remains the only always-required key; §4.1
states that a concept carrying just `type` is fully conformant.

---

# The one rule to remember

**We write a stricter OKF than we read.** That principle is unchanged and still correct.
v0.2 adds a constraint on what "stricter" is allowed to mean:

> **Strictness must be additive, never a redefinition.**

A house rule that requires *more* than the spec is fine. A rule that rejects something the
spec declares conformant is not — that is where a dialect stops being a dialect and starts
being a different format. §11 is explicit that a consumer MUST NOT reject a bundle for
missing optional fields, unknown `type` values, unknown keys, broken cross-links, or a
missing `index.md`.

- *Reading:* anything conformant with v0.2 (or v0.1, under the §13 fallbacks) we consume.
- *Writing:* we emit the dialect below.
- *Never:* report a spec-conformant bundle as non-conformant. Report it as outside our
  dialect, which is a different and honest statement.

---

# Class A — superseded-field debt

These are **not choices**. They are places where the kit writes against a revision that no
longer exists, and they are the migration backlog.

| # | What the kit does | v0.2 | Reference |
|---|---|---|---|
| A1 | `timestamp` on every concept | Superseded by `generated: { by, at }`. Consumers MAY fall back to a legacy `timestamp`. | §5.2, §13.1 |
| A2 | `# Citations` body section carries provenance (and V3 accepts it as "showing your working") | Superseded by the `sources` frontmatter family with per-claim footnotes keyed to `sources[].id` | §5.1, §13.1 |
| A3 | `okf_version: "0.1"` in bundle-root `index.md` | `okf_version: "0.2"` | §12 |
| A4 | Conformance cited as "§9" throughout | Conformance is **§11**. Index is §8, log is §9, Attested Computation is §10. | §8–§11 |

`generated.at` is a straight rename of `timestamp` and migrates mechanically.
`generated.by` and `verified` do not — they require someone to say who produced and who
confirmed each concept, which is a judgment, not a transform. Record the decision, do not
guess it into 116 files.

---

# Class B — additive extensions (conformant; keep)

Everything here is a new frontmatter key, a new `type` value, or a body convention. §4.1
is explicit that producers MAY add keys, that consumers SHOULD preserve unknown keys on
round-trip and MUST NOT reject documents carrying them, and §4.1 also states that `type`
values are not registered centrally. **A v0.2 consumer is therefore already required to
tolerate all of this.** These extensions are conformant today and need no spec change.

| # | Extension | Why the spec has nothing to say | Where |
|---|---|---|---|
| B1 | `Coverage Ledger` type + §Source Coverage Contracts + `STATE: INVENTORY` / `GATE_5-COVERAGE` | OKF has no notion of **completeness**. Every §11 criterion is satisfiable by a bundle that transcribed 60% of its source document. | `ontology.md`, `AGENTS.MD` |
| B2 | §Authority Posture + V13 | v0.2 has trust tiers (*how well verified*) but no **authority scope** (*is this bundle the authority, or carrying context*). Different axis; only appears with more than one bundle. | `ontology.md` |
| B3 | Ten directional relationship markers in `# Related` | §6.1 states links are untyped and the relationship "is conveyed by the surrounding prose". This reads a delimited marker from a closed set out of that prose. | `ontology.md`, `okf_graph.py` |
| B4 | §Deliverable Parity Contracts + CHECK_7 | Drift between concepts and a hand-authored artifact is a production concern, not a format one. | `ontology.md` |
| B5 | `supersedes` / `superseded_by` + `archive/` | Partially overlaps §5.4 `status: deprecated`, but adds the reciprocal edge and retention that `status` alone does not. Adopt `status` **as well**; they answer different halves. | `ontology.md`, V6 |
| B6 | `confidence`, `memory_tier`, certainty bands (T3 layer) | See the note below — this one is additive but **contested on the merits**. | `optional/ontology-ext.md` |

## B6 — the one extension v0.2 argues with

§5.1 declines to store a credibility score, by name and with reasoning:

> it does not store a credibility score: a score is subjective, unportable across
> consumers, and goes stale. Credibility is *inferred* from the signals, not stored.

v0.2's answer to "how much should I trust this" is the **derived trust tier** (§5.3):
`unverified` with no `verified` key, `machine-confirmed` when verified only by non-`human:`
actors, `human-reviewed` when a `human:` actor has verified it. Derived, never stored, so it
cannot drift from what actually happened.

A stored `confidence: 0.9` is a number somebody chose, and nothing regenerates it when the
underlying authority changes. A trust tier is auditable: it names who confirmed the concept
and when.

**Decision:** adopt `generated` / `verified` and derived trust tiers as the primary trust
signal. The certainty *tags* (`confirmed`, `contested`, `interpretation`) may stay — they
describe how settled a *claim* is, which is a genuinely different question from who verified
the *document*, and D5 records evidence that a concept can legitimately carry more than one.
The stored float is what v0.2 supersedes in substance, and the certainty bands (V12) go with
it if the float goes.

Do not resolve this by bulk re-grading. D4's operative constraint stands: a reader must be
able to explain why they are not seeing something.

---

# Class C — producer-side strictness (keep; never call it conformance)

Legitimate house rules about what we **emit**. Each requires more than v0.2 asks. None may
ever cause a spec-conformant bundle to be reported as non-conformant.

| # | Kit rule | v0.2 position | Status |
|---|---|---|---|
| C1 | Required on every concept: `type`, `title`, `description`, `tags`, `timestamp` (V9) | `type` is the only always-required key; a concept carrying just `type` is fully conformant (§4.1) | House rule. `timestamp` → `generated` per A1. |
| C2 | Closed `type` vocabulary, unregistered types fail (V1, ERROR) | §1 lists a fixed taxonomy as a **non-goal**; §4.1 says types are not registered centrally and consumers MUST tolerate unknown ones | House rule. Strongest divergence in the kit; keep it, and never export it as a conformance claim. |
| C3 | `ontology.md` required; a bundle without one is not a valid kit bundle | Not required, not mentioned | House rule. |
| C4 | `resource` required on `type: Reference` | `resource` is Recommended, never required | House rule, via the Required Fields column. |
| C5 | Broken internal links are a WARNING (CHECK_5) | §6.1: consumers MUST tolerate broken links — they may be not-yet-written knowledge | Compliant, because a warning is not a rejection. Must stay a warning. |

## The boundary problem (open)

The kit's bundle root **is** the repo root, so concepts, agent instructions, machinery
(`okf-kit/`), working state (`inbox/`) and derived exports (`projections/`) share one tree.
`okf_check.py` handles this with a private `EXCLUDED_DIRS` set (D10).

Measured on `privacy-act-okf` (10 Aug 2026): **33 `.md` files** outside the reserved
`index.md` / `log.md` carry no frontmatter — `README.md`, 13 under `inbox/processed/`, and
six under `deliverables/` including three lowercase files. Under a literal §11.1 walk of the
tree ("every non-reserved `.md` file"), that bundle does not conform. It passes our checker
only because our checker knows the exclusions, and a third-party v0.2 consumer does not.

This is a real gap, not a formality: it is the difference between a bundle we can hand to
someone and one that only validates in our own tooling. Two ways to close it, unresolved:

1. **Declare the boundary** — publish the exclusion set in `ontology.md` where a consumer
   reads it, rather than only in code.
2. **Move the boundary** — put concepts under a `bundle/` subdirectory so the shippable
   artifact is a subtree with nothing else in it.

(2) is what `google-okf-generator` does, and it is the stronger answer. (1) is far cheaper
and can ship first.

---

# What is NOT part of the spec (and never was)

Unchanged from v1.0 of this note, with one correction. These are the kit's inventions:
`confidence`, `memory_tier`, supersession/`archive`, contradiction records, the
feedback-decay loop, and the multi-agent runtime. See `docs/KIT_RESTRUCTURE.md` — these live
in an optional layer that only liability-grade (T3) domains pull in.

**Correction:** the previous note said an ontology is "our convention, not an OKF
requirement," and that remains true. What has changed is the reason it must stay a
convention: v0.2 §1 lists a fixed type taxonomy as an explicit **non-goal**, so a closed
vocabulary is not merely absent from the spec — it is something the spec has decided against.
That does not make it wrong for us. It makes it permanently ours, and it means the registry
half of our ontology is not a candidate for upstream contribution. The governance half
(B1, B2, B3) is.
