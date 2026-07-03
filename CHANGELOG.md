# CHANGELOG

Version history for the OKF Bundle Bootstrap Kit.
This file tracks changes to the kit itself (AGENTS.MD, LLM_WIKI.MD, FEEDBACK_LOOP.MD, ontology.md).
It is NOT the same as `log.md`, which tracks mutations to your project's knowledge bundle.

Format: [Semantic Versioning](https://semver.org) — MAJOR.MINOR.PATCH

---

## [2.2.0] — 2026-07-03

### Added — new protocol (generalised from a live bundle bug)
- `ontology.md`: new **§Deliverable Parity Contracts** section (v0.1 → v0.2) — an opt-in
  registry for hand-authored interactive deliverables (`deliverables/`, e.g. an HTML decision
  tool) that embed their own denormalized snapshot of a concept subdirectory. Empty template
  row + one illustrative worked example (not a live contract in the seed ontology). Format:
  Contract ID, Deliverable file, Source scope, Identity key, Severity.
- `AGENTS.MD` — `ENRICHMENT_AGENT`: new `GATE_3-PARITY` (on concept creation) and
  `GATE_4-PARITY` (on concept retirement/archival) — if the mutated file falls inside a
  registered contract's `Source scope`, the pass is not complete until the matching deliverable
  record is added/removed in the SAME batch. Unconditional — not gated on "does this seem like
  a significant enough change."
- `AGENTS.MD` — `CONFORMANCE_AGENT`: new `CHECK_7` — diffs every registered contract's source
  files against the deliverable's records by `Identity key` (not just a count) and names the
  specific missing/extra records in the report. Skipped (not failed) when no contracts exist.
- `AGENTS.MD` — `ORCHESTRATOR`: new routing entry — a request to register a deliverable, or a
  description of a newly-built one, dispatches `ONTOLOGY_AGENT` to add the contract row.
- `AGENTS.MD` — `BUNDLE INVARIANTS`: new invariant #9 (parity contracts enforced same-batch,
  unconditionally).
- `AGENTS.MD` — `QUICK-START FOR NEW BUNDLE`: new step 7 — register a contract the same session
  a bespoke deliverable is built, not retroactively.
- `playbook/RAPID_OKF_PLAYBOOK.md`: new **Step 6b** (building a bespoke interactive deliverable)
  and a `deliverables/` row in the template-repo folder list (optional, per-domain).
- `README.md`: `deliverables/` added to the directory table; conformance checklist and Agent
  Reference table both note the new contract mechanism.

### Root cause this fixes
- In the `privacy-act-okf` bundle, two Scenario concepts (H, I) were created on 30 Jun and 2 Jul
  2026 but the bundle's interactive decision-map deliverable was not updated — the old
  instruction ("update the deliverable if the new material changes scenarios…") was conditional
  and easy to read as not applying to a purely *additive* new scenario. That bundle now carries
  its own live contract and passes parity; this release makes the fix structural across every
  future bundle built from this kit, not a one-off patch to a single instruction file.

### Notes
- No new `type`s or `tag`s. No breaking change to existing agent contracts — CHECK_7 and the two
  new gates are no-ops for any bundle with zero registered contracts (the overwhelming majority).

---

## [2.1.0] — 2026-06-24

### Added (opt-in module — does not touch core)
- `ontology-mapper/`: an OKF-customised kinetic ontology mapper, decoupled and opt-in
  (removing the folder leaves the core kit unaffected, same as `optional/`).
- `ontology-mapper/RELATIONSHIP-CROSSWALK.md`: the single coupling contract mapping the
  mapper's gate-logic verbs onto the kit's ten-relationship taxonomy
  (`crosswalk_version: 1` vs `okf_version: 0.1`).
- **Seam B** — `ontology-mapper/pattern-library/`: a conformant OKF sub-bundle that turns
  the mapper's pattern library into governed knowledge (own `ontology.md` registering
  `Pattern`/`Action Type`/`Gate`, plus `index.md`, `log.md`, four seed patterns). Pattern
  writeback now uses ENRICHMENT→LINK→INDEX→LOG instead of a flat log.

### Notes
- The general-purpose `kinetic-ontology-mapper` stays a standalone skill outside this repo.
  This module is its specialised, OKF-coupled sibling; the duplication is intentional.

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
