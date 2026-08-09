# Bundle Update Log

## 2026-08-09

* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — new. Runs CHECK_1–CHECK_9 and V1–V9 in code, exit 0/1/2, `--json` available. The kit previously shipped no executable code, so every check was agent judgment; `build_projection.py` existed only in the `privacy-act-okf` instance and never came back upstream. Verified against both this kit and that bundle.
* **Kit**: [tests/test_okf_check.py](tests/test_okf_check.py) — new. 39 tests, one failing bundle per check plus a passing baseline.
* **Kit**: [ontology.md](ontology.md) — v0.3 → v0.4. Type Registry gained `Required Sections` and `Required Fields` on all three type tables plus a universal required-frontmatter list; `Typical Body Sections` retained as advisory so positional parsers still work. Added V9 to enforce them, and the V1–V9 reserved / `V-<slug>` bundle-rule naming convention, generalised from the live V5/V6 collision between this kit and `privacy-act-okf`.
* **Kit**: [AGENTS.MD](AGENTS.MD) — CONFORMANCE_AGENT must now run `scripts/okf_check.py` first and report its output, and must report NOT RUN rather than PASS if the script is missing. Its judgment is scoped to the three checks code cannot settle.
* **Kit**: [README.md](README.md) — registered `scripts/` and `tests/`; the conformance section now leads with the command.
* **Kit**: [ontology.md](ontology.md) — v0.4 → v0.5. Wrote down the conventions `okf_check.py` already enforces, so the spec and the code agree. V4 now carries its `archive/` exemption in the rule text; it previously contradicted §Concept Hierarchy Rules 5 outright for an archived stub, and only the checker knew the resolution. New §Conventions the checker depends on covers the `**Worked example**` marker (load-bearing — `**Example**` would make the checker read an illustration as a live contract), the rule that a subtree with its own `ontology.md` is a separate bundle, and the directories that are not concept trees.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.4.0, then v2.4.1 for the above plus the V3 presence fix, which had reached log.md and the commit message but not the changelog.
* **Kit**: [docs/PLAN-graph-and-certainty.md](docs/PLAN-graph-and-certainty.md) — new. Staged plan for the two stubs, written against measurements of `privacy-act-okf` rather than against the spec, because they disagree. Part A (relationships): 104/104 concepts carry a `# Related` section, 323 of 332 bullets (97.3%) parse once wrapped lines are joined, and all 323 use the bold `**rel**` marker — none relies on inferring a relationship from an English verb, so this is not prose parsing and the standing caution against it does not apply. Four bullets use unregistered inverse forms, which is the real finding. Two to three days, one decision. Part B (certainty): 51 of 104 concepts breach the band their own tag declares, so the work starts with three questions for a human, not with a check. **Plan only — nothing implemented.**
* **Update**: [stubs/certainty-vocabulary-reconciliation.md](stubs/certainty-vocabulary-reconciliation.md) — corrected. It proposed "at most one tag from a mutual-exclusion group"; the corpus disproves that. Three concepts carry `confirmed` and `interpretation` deliberately — principle confirmed, enforcement dimension interpretation — so certainty attaches to a claim, not to a document, and a mutual-exclusion rule would break working practice. Also records that the stated bands themselves are in question, not just their enforcement.
* **Update**: [stubs/relationship-graph-extraction.md](stubs/relationship-graph-extraction.md) — added the measurements and the three named classes of parse failure.
* **Gap**: [stubs/relationship-graph-extraction.md](stubs/relationship-graph-extraction.md) — recorded the declared-but-unextracted relationship taxonomy. A bundle is a list of concepts with prose between them, not a graph, which is most of what an ontology is for. Two of the ten relationships decay silently: a `supersedes` edge still cited in prose, and a `derived-from` conclusion whose input changed. V6 now guards the reciprocal-frontmatter half in code; the prose half is unguarded because nothing parses `# Related`. States the two conditions any extraction must meet — count what is extracted, and fail on an unregistered relationship rather than dropping it.
* **Gap**: [stubs/certainty-vocabulary-reconciliation.md](stubs/certainty-vocabulary-reconciliation.md) — recorded that a numeric `confidence` and a certainty tag can disagree with nothing relating them. Live case: `privacy-act-okf`'s `app-1-3-policy-currency.md` carries both `confirmed` and `interpretation` at confidence 0.9, and that bundle's own AGENTS.MD band mapping (confirmed ≥ 0.95, interpretation ≤ 0.8) puts it simultaneously over and under — but the mapping lives in an instruction file, so nothing enforces it. Proposes the same shape as the v0.4 Type Registry change: declare bands and exclusion groups in §Tag Taxonomy, let one rule enforce every declaration. Leaves the human question open — whether the number or the tag wins when they disagree.
* **Kit**: [index.md](index.md) — registered the two new stubs.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — V3 now tests `confidence_sources` for presence, not truth. `confidence_sources: 0` is a declared zero and correct for a Stub at confidence 0.0; treating it as absent flagged every properly-formed stub, including the kit's own `trigger-c-scheduler`. Test added.

## 2026-07-03

* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.3.0: Source Coverage Contracts, generalised from the `directors-guide-ai-governance` bundle omitting four recurring content boxes despite a full sequential read.
* **Kit**: [ontology.md](ontology.md) — Added §Source Coverage Contracts, type `Coverage Ledger` (CORE, all tiers), tag `coverage` (ontology v0.2 → v0.3).
* **Kit**: [AGENTS.MD](AGENTS.MD) — ORCHESTRATOR: SOURCE-DOCUMENT MODE vs NOTE MODE routing split. ENRICHMENT_AGENT: new `STATE: INVENTORY`, `GATE_1-INVENTORY`, `GATE_5-COVERAGE`. CONFORMANCE_AGENT: `CHECK_9`. BUNDLE INVARIANTS: #11. QUICK-START: step 1b.
* **Kit**: [playbook/RAPID_OKF_PLAYBOOK.md](playbook/RAPID_OKF_PLAYBOOK.md) — New Step 4a (coverage ledger, all tiers, before the tier-gated quality pass).
* **Kit**: [playbook/OKF_QUICKSTART.md](playbook/OKF_QUICKSTART.md) — Setup checklist and anti-patterns note the coverage-ledger step.
* **Kit**: [README.md](README.md) — Conformance checklist, Agent Reference table, directories table, and version bumped to 2.3.0.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.2.2: propagate commit checklist to all generated bundles.
* **Creation**: [playbook/BUNDLE_COMMIT_CHECKLIST.md](playbook/BUNDLE_COMMIT_CHECKLIST.md) — Printable log-before-commit gate (Paths A/B/C).
* **Creation**: [templates/log-domain-init.md](templates/log-domain-init.md) — Domain log seed for new bundle clones.
* **Kit**: [AGENTS.MD](AGENTS.MD) — §BUNDLE COMMIT CHECKLIST applies to all bundles; QUICK-START steps 0 and 8.
* **Kit**: [README.md](README.md), [playbook/OKF_QUICKSTART.md](playbook/OKF_QUICKSTART.md), [playbook/RAPID_OKF_PLAYBOOK.md](playbook/RAPID_OKF_PLAYBOOK.md), [playbook/COWORK_PROJECT_GUIDE.md](playbook/COWORK_PROJECT_GUIDE.md), [playbook/PROJECTION_GUIDE.md](playbook/PROJECTION_GUIDE.md) — Commit discipline wired into setup/update flows.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.2.1: LOG_AGENT commit gate, log backfill, CHECK_8.
* **Kit**: [README.md](README.md) — Kit-maintenance commit trigger in Agent Reference table.
* **Kit**: [log.md](log.md) — Restored full mutation history after v2.0.0 placeholder wipe; backfilled v1.1.1–v2.2.0.
* **Kit**: [AGENTS.MD](AGENTS.MD) — LOG_AGENT mandatory before commit on kit-maintenance path; **Kit**/**Restructure** verbs; CHECK_8; KIT-MAINTENANCE COMMIT CHECKLIST.
* **Kit**: [AGENTS.MD](AGENTS.MD) — Deliverable Parity Contracts: GATE_3-PARITY, GATE_4-PARITY, CHECK_7, invariant #10, QUICK-START step 7.
* **Kit**: [ontology.md](ontology.md) — Added §Deliverable Parity Contracts (ontology v0.2).
* **Creation**: [playbook/COWORK_PROJECT_GUIDE.md](playbook/COWORK_PROJECT_GUIDE.md) — Per-client Claude Cowork Project setup guide.
* **Kit**: [README.md](README.md) — `deliverables/` directory, conformance checklist, kit version 2.2.
* **Kit**: [playbook/RAPID_OKF_PLAYBOOK.md](playbook/RAPID_OKF_PLAYBOOK.md) — Step 6b bespoke interactive deliverables.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.2.0 release notes.

## 2026-07-01

* **Kit**: [AGENTS.MD](AGENTS.MD) — Added PROJECTION_AGENT (two-deployment-mode cloud LLM export).
* **Creation**: [playbook/PROJECTION_GUIDE.md](playbook/PROJECTION_GUIDE.md) — Projection build workflow.
* **Creation**: [projections/](projections/) — Flat-file export directory scaffold.
* **Kit**: [AGENTS.MD](AGENTS.MD) — Fixed BUNDLE ROOT `index.md` format example YAML `---` fences.
* **Creation**: [ontology-mapper/](ontology-mapper/) — Opt-in kinetic ontology mapper module (kit v2.1.0).

## 2026-06-24

* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.0.0 BREAKING: core/optional split.
* **Restructure**: [FEEDBACK_LOOP.MD](optional/FEEDBACK_LOOP.MD) — Moved from root to `optional/` (cognitive layer demoted).
* **Restructure**: [LLM_WIKI.MD](optional/LLM_WIKI.MD) — Moved from root to `optional/`.
* **Creation**: [docs/KIT_RESTRUCTURE.md](docs/KIT_RESTRUCTURE.md) — Decision record for restructure.
* **Creation**: [docs/OKF_DIVERGENCE.md](docs/OKF_DIVERGENCE.md) — Spec floor vs kit dialect.
* **Creation**: [optional/ontology-ext.md](optional/ontology-ext.md) — T3 optional field definitions.
* **Creation**: [playbook/OKF_QUICKSTART.md](playbook/OKF_QUICKSTART.md) — Quick-start checklist.
* **Creation**: [playbook/RAPID_OKF_PLAYBOOK.md](playbook/RAPID_OKF_PLAYBOOK.md) — Rapid domain bootstrap playbook.
* **Kit**: [README.md](README.md), [AGENTS.MD](AGENTS.MD), [ontology.md](ontology.md) — Core vs optional banner and documentation.

## 2026-06-20

* **Kit**: [index.md](index.md) — Wrapped `okf_version` in YAML fences (v1.1.1).
* **Kit**: [AGENTS.MD](AGENTS.MD) — Rule #3 `index.md` frontmatter exception clarified.
* **Gap**: [stubs/trigger-c-scheduler.md](stubs/trigger-c-scheduler.md) — Trigger C has no automatic scheduler; stub recorded.

## 2026-06-19

* **Kit**: [README.md](README.md) — Added canonical repo URL and clone instructions.
* **Kit**: [.gitignore](.gitignore) — Ignore local `*.command` helper scripts.
* **Initialization**: Bundle bootstrap kit v1.0.0 installed. AGENTS.MD, LLM_WIKI.MD, FEEDBACK_LOOP.MD loaded as agent instructions.
* **Creation**: [ontology.md](ontology.md) — Initial ontology v0.1 with system types, core knowledge types, relationship taxonomy, and tag vocabulary.
* **Creation**: [index.md](index.md) — Root index scaffold created. Awaiting first concept ingestion.
* **Creation**: [reports/wiki-evolution.md](reports/wiki-evolution.md) — Self-improvement ledger initialised. Awaiting first self-improvement event.
