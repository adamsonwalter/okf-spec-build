# CHANGELOG

Version history for the OKF Bundle Bootstrap Kit.
This file tracks changes to the kit itself (AGENTS.MD, LLM_WIKI.MD, FEEDBACK_LOOP.MD, ontology.md).
It is NOT the same as `log.md`, which tracks mutations to your project's knowledge bundle.

Format: [Semantic Versioning](https://semver.org) — MAJOR.MINOR.PATCH

---

## [1.1.0] — 2026-06-19

### Added
- `FEEDBACK_LOOP.MD`: Self-Improvement Events section defining seven auditable
  event types (Tier Promotion, Inference Added, Contradiction Resolved, Stub Filled,
  Ontology Extended, Link Density Increase, Confidence Threshold Crossed).
- `FEEDBACK_LOOP.MD`: Wiki Evolution Report spec — `reports/wiki-evolution.md`
  auto-maintained by LOG_AGENT as the human-readable self-improvement ledger.
- `CHANGELOG.md`: This file. Kit version history, separate from bundle `log.md`.

### Changed
- `README.md`: Removed incorrect instruction to manually pre-populate ontology types
  and tags. ONTOLOGY_AGENT handles this autonomously during ingestion.

---

## [1.0.0] — 2026-06-19

### Added
- `AGENTS.MD`: Six-agent orchestration state machine (OKF_ORCHESTRATOR,
  ENRICHMENT_AGENT, LINK_AGENT, INDEX_AGENT, LOG_AGENT, CONSUMPTION_AGENT,
  CONFORMANCE_AGENT). Fixed the three OKF v0.1 conformance gaps from the
  original AGENTS.MD design: GATE_5 link validation against bundle filesystem
  not index.md; index.md format (no frontmatter); log.md ISO 8601 format.
- `LLM_WIKI.MD`: Wiki operating model. Four memory tiers, confidence scoring
  model, supersession protocol, gap-finding (four gap types), compounding loop
  principle, wiki behavioral rules.
- `FEEDBACK_LOOP.MD`: Continuous synthesis loop. Five-state pipeline
  (SENSE→SYNTHESIZE→MUTATE→VALIDATE→AWAIT), four trigger types, semantic delta
  classification, contradiction resolver, knowledge decay model, multi-agent
  coordination rules, loop health metrics.
- `ontology.md`: Bundle ontology as an OKF concept (type: Ontology). Type
  registry (13 core types + 7 system types), relationship taxonomy (10 types),
  tag taxonomy, concept hierarchy rules, validation rules (V1–V8),
  ONTOLOGY_AGENT extension protocol, deprecated types registry.
- `index.md`: OKF-conformant root index scaffold with okf_version: "0.1".
- `log.md`: Starter mutation log with initialization entry.
- `README.md`: Quick-start guide, file reference, naming convention,
  agent trigger reference.
- `.gitignore`: OS, editor, temp agent lock files.
- `stubs/`, `reports/`, `archive/`: Placeholder directories with `.gitkeep`.

### Conformance
- Validated against OKF v0.1 SPEC.md (GoogleCloudPlatform/knowledge-catalog).
- All three original conformance gaps corrected.

---

## Versioning Policy

| Change type | Version bump | Example |
|---|---|---|
| New agent, new protocol, new spec section | MINOR | 1.0.0 → 1.1.0 |
| Bug fix, wording correction, format repair | PATCH | 1.1.0 → 1.1.1 |
| Breaking change to agent contracts or file structure | MAJOR | 1.x.x → 2.0.0 |

Breaking changes require a migration note explaining how existing bundles are affected.
