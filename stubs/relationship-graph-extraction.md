---
type: Stub
title: Relationship Graph Extraction — the taxonomy is declared but not traversable
description: Known gap. The ten-relationship taxonomy is declared in ontology.md and used in prose under `# Related`, but nothing extracts it, so no consumer can traverse the graph and no check can detect a decayed relationship.
memory_tier: working
confidence: 0.0
confidence_sources: 0
review_required: true
tags: [system, governance, review-required]
timestamp: 2026-08-09T00:00:00Z
---

# Relationship Graph Extraction

> ⚠️ STUB: a known, deliberately-tracked gap, not a finished concept.
> It exists so the gap is visible rather than forgotten.

## The Gap

`ontology.md` §Relationship Taxonomy declares ten relationships — `depends-on`,
`implements`, `contradicts`, `supersedes`, `references`, `related-to`, `part-of`,
`derived-from`, `authored-by`, `governs`. AGENTS.MD instructs agents to annotate links
with them in the surrounding prose, deliberately not in the markdown link syntax.

Nothing extracts them. A bundle is therefore a **list of concepts with prose between
them**, not a graph — which is most of what an ontology is for. A consumer receives the
taxonomy as data in the projection and has nothing to apply it to.

## Why this is more than a missing feature

Two of the ten **decay**, and their decay is silent:

- **`supersedes`** — a superseded concept that is still cited reads exactly like a current
  one. V6 exists to guard the reciprocal-frontmatter half of this, and now runs in
  `scripts/okf_check.py`. The prose half — a `# Related` line still pointing at something
  that has since been superseded — is unguarded, because nothing parses `# Related`.
- **`derived-from`** — when the thing a conclusion rested on changes, the conclusion
  survives unchanged and indistinguishable from a live one.

In a legal, regulatory, or safety corpus that is the failure that costs the most, because
the stale version looks identical to the current one and nobody re-reads a concept that
appears settled.

## Measured, 9 August 2026

Against `privacy-act-okf` (104 concepts): **every** concept has a `# Related` section, 332
relationship bullets exist, and **323 (97.3%) parse** once wrapped continuation lines are
joined. All 323 use the bold `**rel**` marker — **none** relies on inferring a relationship
from an English verb.

So this is not prose parsing. It is a bold marker from a closed ten-item vocabulary in the
kit's own format, and the caution against prose parsing does not apply.

The 9 that do not parse are informative: four use unregistered inverse or past-tense forms
(`**referenced-by**` ×3, `**superseded**` ×1), two are truncated at a section boundary, and
three are genuine prose cross-references carrying no relationship at all. The inverse forms
are the finding — authors need to state an edge backwards and the taxonomy gives them no way.

Full staged plan: [docs/PLAN-graph-and-certainty.md](../docs/PLAN-graph-and-certainty.md).

## What filling it involves

Parse `# Related` blocks in `scripts/`, where the format is ours, and emit the edges into
the projection alongside the concepts. Two conditions, both non-negotiable:

1. **Count what is extracted.** An extraction that silently yields zero edges is
   indistinguishable from a bundle with no relationships — the same reasoning that already
   makes an empty registry section fail the build in `build_projection.py`.
2. **An unregistered relationship must fail, not be dropped.** The taxonomy is closed at
   ten, which is exactly what makes this tractable.

Parsing prose is how corpus defects get introduced. It is acceptable here only because the
format is the kit's own and the vocabulary is closed.

## Related

- `depends-on` [ontology.md](../ontology.md) §Relationship Taxonomy — the closed vocabulary
  that makes extraction decidable.
- `related-to` [certainty-vocabulary-reconciliation](certainty-vocabulary-reconciliation.md)
  — the other declared-but-unused structure in the same ontology.
