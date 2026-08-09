---
type: Stub
title: Certainty Vocabulary — two systems with nothing tying them together
description: Known gap. A concept can carry a numeric `confidence` and a certainty tag, and no rule relates them, so a concept tagged confirmed with a low confidence is currently legal and undetectable.
memory_tier: working
confidence: 0.0
confidence_sources: 0
review_required: true
tags: [system, governance, review-required]
timestamp: 2026-08-09T00:00:00Z
---

# Certainty Vocabulary Reconciliation

> ⚠️ STUB: a known, deliberately-tracked gap, not a finished concept.
> It exists so the gap is visible rather than forgotten.

## The Gap

Bundles express certainty two ways at once:

- a **number** — `confidence: 0.65` (T3 field, `optional/ontology-ext.md`)
- a **tag** — a domain vocabulary such as `confirmed` / `contested` / `interpretation`

Nothing in `ontology.md` relates them. A concept tagged `confirmed` carrying
`confidence: 0.6` is valid today, and so is a concept carrying two contradictory certainty
tags at once. Neither is detectable, because there is nothing to detect them against.

**This is live, not hypothetical.** In `privacy-act-okf`,
`framework/app-1-3-policy-currency.md` carries `tags: [..., confirmed, interpretation]` —
both certainty tags on one concept — with `confidence: 0.9`. That bundle's own AGENTS.MD
maps the vocabulary to bands (`confirmed` ≥ 0.95, `interpretation` ≤ 0.8), so by its own
stated mapping that concept is simultaneously over and under its band. The mapping lives in
an instruction file, which is prose an agent reads, so nothing enforces it.

## Why the kit cannot simply hard-code the vocabulary

`confirmed` / `contested` / `interpretation` is a **domain** vocabulary, not a kit one. The
kit's System Tags are `system`, `governance`, `stub`, `review-required`, `archived`,
`inference`, `disputed`, `coverage`. Writing the privacy vocabulary into the kit would
impose one domain's epistemics on every bundle — the error the `Required Fields` columns
were added to avoid.

## What filling it involves

The same shape as the Type Registry change in ontology v0.4: **declare it, then let one
rule enforce every declaration.**

Give §Tag Taxonomy an optional certainty band — a tag may declare a `confidence` range and
a mutual-exclusion group. A bundle that uses certainty tags fills those columns; a bundle
that does not leaves them empty and nothing changes. One rule then enforces two things
across every bundle:

- a concept's `confidence` falls inside the declared band of every certainty tag it carries

A range test, so it belongs in `scripts/okf_check.py` rather than in an instruction file.

**Corrected 9 August 2026 — certainty attaches to a claim, not to a document.** An earlier
version of this stub also proposed "at most one tag from a mutual-exclusion group". Measuring
the corpus killed that: three concepts carry `confirmed` *and* `interpretation`, and the
30 July log entry for `app-1-3-policy-currency` records why on purpose — *"Principle
`confirmed`; enforcement dimension `interpretation`."* One concept, two claims, two
certainties. A mutual-exclusion rule would break working practice. An `Exclusive group`
column may still be worth declaring for a bundle that has a real exclusion, but it must not
be applied to this one.

**And the bands themselves are in question, not just the enforcement.** Measured against
`privacy-act-okf`: `confirmed` spans 0.8–1.0 against a stated band of ≥ 0.95, and
`interpretation` spans 0.6–0.95 against ≤ 0.8. **51 of 104 concepts breach the band their own
tag declares.** A rule half a corpus breaks was never the rule its authors were following, and
shipping it as an ERROR would get it switched off — which is what happened to V3.

## Open question for the human

Whether the number or the tag is authoritative when they disagree. That is a judgment about
how the bundle is meant to be read, not something the checker can decide — and it should be
settled before either is enforced, or the rule will simply be dropped by the first bundle it
inconveniences, which is what happened to V3.

## Related

- The registry where a certainty band would be declared is [ontology.md](../ontology.md) — **depends-on**.
- The other declared-but-unused structure is [relationship graph extraction](relationship-graph-extraction.md) — **related-to**.
