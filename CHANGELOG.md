# CHANGELOG

Version history for the OKF Bundle Bootstrap Kit.
This file tracks changes to the kit itself (AGENTS.MD, LLM_WIKI.MD, FEEDBACK_LOOP.MD, ontology.md).
It is NOT the same as `log.md`, which tracks mutations to your project's knowledge bundle.

Format: [Semantic Versioning](https://semver.org) — MAJOR.MINOR.PATCH

---

## [2.0.0] — 2026-06-24

### Changed (BREAKING — file structure)
- Demoted the runtime cognitive layer to opt-in. `LLM_WIKI.MD` and
  `FEEDBACK_LOOP.MD` moved from root into `optional/`. Core stays at root
  (`AGENTS.MD`, `ontology.md`, `index.md`, `log.md`) so the kit still drops into
  a project root unchanged.
- `AGENTS.MD`: added a "CORE vs OPTIONAL" banner. Optional-layer instructions
  (confidence, memory tiers, supersession, decay) are inert unless `optional/`
  files are present.
- `README.md`: reworked file tables and quick-start for the core/optional split;
  version bumped to 2.0.
- `ontology.md`: annotated that `Inference`, `Loop Health Report`, `Decay
  Report`, `Contradiction Record`, and the `confidence`/`memory_tier` fields are
  optional-layer; their rules (V3, V5–V8) now live in `optional/ontology-ext.md`.

### Added
- `optional/ontology-ext.md`: opt-in field definitions and T3-gated conformance
  rules (V3, V5–V8).
- `optional/README.md`: how/when to enable the T3 layer.
- `docs/OKF_DIVERGENCE.md`: spec floor vs. this kit's stricter dialect; the
  read/write asymmetry; confirms the ontology is a kit convention, not an OKF
  requirement.
- `docs/KIT_RESTRUCTURE.md`: decision record behind this split, with operating-
  repo evidence.

### Migration
- Existing T3 bundles: copy `optional/*` into the bundle root and instruct the
  agent to read them, as before. T1/T2 bundles need no change — they were already
  running on the six standard fields.

---

## [1.1.1] — 2026-06-19

### Fixed
- `index.md`: Wrapped the root `okf_version: "0.1"` declaration in `---` fences.
  It was a bare line, so per SPEC §4.1 a strict parser read it as body text, not a
  frontmatter block — the version declaration silently did not count.
- `AGENTS.MD`: Reworded conformance rule #3. It previously asserted index.md has "NO
  frontmatter (body only)", which contradicted the root index.md carrying `okf_version`.
  Rule now states the SPEC §11 exception: only the bundle-root index.md may carry a single
  fenced `okf_version` block.

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
