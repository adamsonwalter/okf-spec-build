# LLM_WIKI.MD — Wiki Operating Model
# OKF Operating Bundle | Companion to AGENTS.MD
# Convention: ALL CAPS filenames are agent instructions, not OKF concept documents.
# Do NOT add YAML frontmatter to this file. Do NOT index this file in index.md.

---

## PURPOSE

This file defines how agents treat the OKF bundle as a compounding LLM wiki —
not a static document store, not a RAG retrieval index, but a living knowledge
representation that grows more accurate and more connected with every input.

The core principle (Karpathy, 2026): **knowledge is compiled once and kept
current, not re-derived on every query.** The goal is not to answer questions.
It is to maintain an accurate, growing representation of what is known.
Questions are queries over that representation.

This shifts agent behavior from question-answering to knowledge management.

---

## MEMORY ARCHITECTURE

The wiki operates across four tiers. Every concept in the OKF bundle has an
implicit tier assignment, tracked by the `memory_tier` frontmatter field
(optional; agents infer tier when absent).

### Tier 1 — Working Memory
**Scope:** Concepts extracted from the current input session.
**Lifespan:** Until FEEDBACK_LOOP confirms they are stable or redundant.
**Frontmatter marker:** `memory_tier: working`
**Agent behavior:** Treat as provisional. Do not link heavily. Flag for review.

### Tier 2 — Episodic Memory
**Scope:** Concepts confirmed across two or more independent input sessions.
**Lifespan:** Until superseded or confidence decays below threshold (see §CONFIDENCE).
**Frontmatter marker:** `memory_tier: episodic`
**Agent behavior:** Link freely. Include in index.md entries. Surface in queries.

### Tier 3 — Semantic Memory
**Scope:** Concepts with broad cross-links, high confidence, and stable type
classification. Core nodes of the knowledge graph.
**Frontmatter marker:** `memory_tier: semantic`
**Agent behavior:** Treat as authoritative. Contradiction requires high-confidence
new input before mutation. Consult ontology.md before reclassifying type.

### Tier 4 — Procedural Memory
**Scope:** How-to knowledge: playbooks, workflows, agent instructions,
decision protocols. Structurally distinct from factual concepts.
**Frontmatter marker:** `memory_tier: procedural`
**Agent behavior:** Never derive procedural knowledge from factual concepts alone.
Require explicit human-authored or agent-validated source. Cross-link to
the semantic concepts the procedure operates on.

---

## CONFIDENCE MODEL

Every concept carries a confidence score, tracked in frontmatter:

```yaml
confidence: 0.85        # float 0.0–1.0
confidence_sources: 3   # number of independent inputs confirming this concept
confidence_updated: 2026-06-19T10:00:00Z
```

### Scoring Rules

| Condition | Delta |
|---|---|
| First extraction from a single input | 0.50 |
| Confirmed by second independent input | +0.20 |
| Each additional independent confirmation | +0.05 (cap 0.95) |
| Contradicted by new input (unresolved) | −0.15 |
| Contradiction resolved in favor of this concept | +0.10 |
| Contradiction resolved against this concept | SUPERSEDE (see §SUPERSESSION) |
| Not referenced in any query for 30 days | −0.05 |
| Not updated in 90 days (stale signal) | flag `stale: true` in frontmatter |

**Confidence threshold rules:**
- `< 0.40` → flag concept with `review_required: true`. Suppress from Tier 2+.
- `0.40–0.69` → Tier 1 (Working). Index but annotate as provisional.
- `0.70–0.89` → Tier 2 (Episodic). Full participation in graph.
- `0.90+` → Tier 3 (Semantic). Authoritative. Mutation requires explicit gate.

---

## SUPERSESSION PROTOCOL

When a concept is replaced by a more current or accurate version:

1. The OLD concept file is NOT deleted.
2. Inject into the OLD concept's frontmatter:
   ```yaml
   superseded_by: /path/to/new-concept.md
   superseded_at: 2026-06-19T10:00:00Z
   supersession_reason: "More recent input contradicts core claim. See new concept."
   memory_tier: archived
   ```
3. In the OLD concept's body, prepend:
   ```
   > ⚠️ SUPERSEDED: This concept has been replaced by [New Concept](/path/to/new-concept.md).
   ```
4. The NEW concept's frontmatter includes:
   ```yaml
   supersedes: /path/to/old-concept.md
   ```
5. LOG_AGENT records a `**Supersession**` entry in log.md.
6. INDEX_AGENT removes the old concept from active index sections.
   Archived concepts may appear in a `## Archived` section if desired.

---

## GAP-FINDING

Agents actively identify what is NOT known. After each ENRICHMENT cycle, run:

### Gap Type 1 — Broken Link Targets
Any link in the bundle pointing to a file that does not exist is a knowledge
gap. LOG_AGENT records it as `**Gap**: [concept name] referenced but not yet written`.
ENRICHMENT_AGENT creates a stub concept for the gap target with:
```yaml
type: Stub
confidence: 0.0
review_required: true
```
The stub is a placeholder: a known gap made explicit rather than invisible.

### Gap Type 2 — Isolated Nodes
Any concept with zero incoming or outgoing links after LINK_AGENT runs is
potentially isolated. Flag with `isolated: true` in frontmatter.
On next ENRICHMENT cycle, attempt to find relationships or flag for human review.

### Gap Type 3 — Type Orphans
Any concept whose `type` value is not registered in ontology.md is a type gap.
ENRICHMENT_AGENT should propose the type addition to ontology.md. Do not
silently accept unregistered types — surface them.

### Gap Type 4 — Confidence Voids
Any semantic region (subdirectory or tag cluster) where all concepts have
`confidence < 0.60` is a void zone. Flag the parent index.md with:
```
> ⚠️ CONFIDENCE VOID: Concepts in this section are provisional. Independent verification needed.
```

---

## COMPOUNDING LOOP PRINCIPLE

Every query run against the bundle is an opportunity to compound knowledge:

1. **Query** arrives at CONSUMPTION_AGENT.
2. CONSUMPTION_AGENT synthesizes an answer from existing concepts.
3. If the synthesis reveals a new relationship, inference, or gap:
   → Pass the finding to OKF_ORCHESTRATOR as a new input.
   → ENRICHMENT_AGENT adds it as a concept with `type: Inference` and
     `confidence: 0.55` (higher than stub, lower than confirmed).
4. The inference becomes linkable, searchable, and refinable on future queries.

This transforms every answered question into a permanent increment to the graph.
Answers do not evaporate — they sediment.

---

## WIKI AGENT BEHAVIORAL RULES

These override default ENRICHMENT_AGENT behavior when operating in wiki mode:

1. **Never delete.** Archive via supersession. Deletion is irreversible;
   supersession is traversable.

2. **Never overwrite without compare.** Always load the existing concept and
   diff against new input before writing. Additive mutation is preferred.

3. **Always promote tier.** When a concept accumulates enough confirmations
   to cross a tier threshold, update `memory_tier` in frontmatter immediately.

4. **Stubs are first-class.** A stub is better than a broken link. Create stubs
   eagerly. Fill them lazily (when input arrives that covers the gap).

5. **Queries compound.** Every CONSUMPTION_AGENT response that synthesizes
   new information triggers a follow-up ENRICHMENT cycle.

6. **Log everything.** The log.md is the audit trail of how knowledge evolved.
   It must be possible to reconstruct the bundle's intellectual history from log.md alone.
