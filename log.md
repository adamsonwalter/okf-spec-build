# Bundle Update Log

## 2026-08-11 (later)

* **Kit**: two further CI faults, both only visible once the checks actually ran. (1) `projections/okf-spec-build-master.md`/`.json` were committed in `6d04cb8` — written by running `okf_project.py` on the kit to *reproduce* the failure, then swept in by `git add -A`. The kit holds no knowledge and registers no artefacts, so their presence made the new guard project the kit and fail exactly as before. Removed, and `.gitignore`d so a stray local run cannot be committed again; a bundle gets its own `.gitignore` from `okf_new_bundle.py`, so nothing is inherited. (2) `bundle-conformance.yml` lived in `.github/workflows/`, so GitHub ran it **in the kit**, where there is no `okf-kit/` submodule and it failed at the first step. It is a template, not a live workflow — moved to `templates/` beside `check.command` and `log-domain-init.md`, with `okf_new_bundle.py` and `README.md` updated. Verified by scaffolding a throwaway bundle and confirming it still receives `.github/workflows/conformance.yml`.

* **Kit**: [.github/workflows/conformance.yml](.github/workflows/conformance.yml), [.github/workflows/bundle-conformance.yml](.github/workflows/bundle-conformance.yml) — **CI had never passed, in any repo, since the day it was added** (`4fb9f04`, 10 Aug). Two independent causes, both now fixed, neither a bundle defect. (1) Every projection embeds its build time, so `git diff --quiet -- projections` after a rebuild was *always* non-empty — the "projections are up to date" step **could not pass**. It now excludes the two build stamps and nothing else; verified both directions, so a real concept change still fails. (2) The kit's own guard, `ls -A projections | grep -v README`, saw `by-tag/` and projected **the kit** — which holds no knowledge and registers no artefacts, failing with "written but not registered". Now guarded on a built `projections/*-master.md`.
* **Kit**: [docs/DECISIONS.md](docs/DECISIONS.md) — **D13**. A check that can only ever fail is the same failure as a check that never ran, wearing the opposite mask: it reports a problem that is not there until people stop reading it, and then a real drift lands in the noise. Records the both-directions verification and the one hole left open deliberately.

## 2026-08-11

* **Kit**: [docs/STATE_OF_PLAY.md](docs/STATE_OF_PLAY.md) — new. A cold-read recount of where the OKF work stands after the 10 August v0.2 migration: what the three repos are each for now, why trust tiers replaced the stored `confidence` float, the format-versus-factory split between the spec and this kit, the three-class divergence rule that keeps the dialect on-spec, what can and cannot go upstream from the ontology, and the five open items ranked with whose call each one is. `CHANGELOG.md` and `log.md` record what changed; this records what it means and what is still undecided. Linked from `README.md`.

## 2026-08-10 (later)

* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — staleness as a **warning that never gates**. Added `is_stale()` (the §5.5 predicate) and **V17**, WARNING by construction: §10.5 mandates refusal only for a failing attestation and offers "warn or refuse" for staleness, and §5.3 calls the family advisory signals rather than access control. Added `--today YYYY-MM-DD` so a horizon can be chosen against what it will actually stale out, rather than guessed. v2.12.0.
* **Kit**: [scripts/okf_project.py](scripts/okf_project.py) — the master `.md` states the horizon inline, since a corpus pasted into a cloud Project has no clock; the `.json` ships `staleAfter`, `stale` and `staleEvaluatedAt`. The evaluation date travels with the flag because a projection rebuilds when concepts change, not when dates pass — so a consumer with a clock must re-derive, and now it can tell that it needs to.
* **Kit**: [ontology.md](ontology.md), [docs/DECISIONS.md](docs/DECISIONS.md) — **D12** records why this stays advisory: a live legal corpus refusing on 11 Dec 2026 would fail on a date rather than a defect, and stale is not wrong (a concept can be inaccurate the day it is written and accurate a year past its horizon). Also records that a **horizon is a review cycle, not a content date** — setting it to a commencement date expires the corpus in one day and gets the warning switched off, the D4 shape — and the freshness × trust matrix whose dangerous cell is *verified + stale*.
* **Kit**: [tests/test_okf_check.py](tests/test_okf_check.py) — 11 tests including an explicit guard that V17 never appears at ERROR severity. 143 across the kit.
* **Note**: mechanism only. **No `stale_after` value is set on any concept** in any bundle — that remains open, and deliberately so.

## 2026-08-10

* **Kit**: [docs/OKF_DIVERGENCE.md](docs/OKF_DIVERGENCE.md) — rewritten against **OKF v0.2**, published 2026-07-24 and superseding the v0.1 this kit was written against. Divergences are now sorted into three classes: superseded-field debt (fix), additive extension (keep — spec §4.1 already requires consumers to tolerate them), and producer-side house rules (keep, but never report as non-conformance). The sort is the point: "migrate to v0.2" read naively deletes the Coverage Ledger, Authority Posture and relationship-marker work, all of which is conformant as-is.
* **Kit**: [docs/DECISIONS.md](docs/DECISIONS.md) — D11 records the classification and the constraint that keeps the dialect legitimate: strictness must be additive, never a redefinition. Also records why trust tiers supersede the stored `confidence` float in substance while the certainty *tags* survive on the separate axis D5 measured.
* **Kit**: [ontology.md](ontology.md) — ontology v1.0. New §Spec Field Families (actor convention, `generated`/`verified`, derived trust tiers, `status`/`stale_after`, `sources`). §Required frontmatter names `generated` in place of `timestamp`, legacy key accepted during migration per spec §13.1. Base conformance reference corrected from v0.1 §9 to v0.2 §11. Added V14, V15, V16.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — frontmatter parser rewritten to read nested block mappings and block sequences. The flat parser turned `verified:` block lists into junk keys with **no error**, breaking its own "report, never skip" contract; since `sources` and `verified` are both nested in v0.2, no new rule could have been trusted on top of it. Implements V14/V15/V16 and `trust_tier()`. Refuses shapes it cannot read rather than guessing.
* **Kit**: [tests/test_okf_check.py](tests/test_okf_check.py) — 20 tests covering nested parsing, the §5.2 bare-mapping rule, trust-tier derivation, and the false-negative side of each new rule. 129 across the kit.
* **Kit**: [README.md](README.md), [AGENTS.MD](AGENTS.MD), [CHANGELOG.md](CHANGELOG.md) — v0.1 → v0.2 throughout, `okf_version: "0.2"`, rule range V1–V16, version table corrected (had stalled at 2.3.0 while the kit shipped 2.10.1). v2.11.0.
* **Kit**: [scripts/okf_project.py](scripts/okf_project.py) — projections carry the v0.2 layer through to consumers. The master `.md` metadata line gains `Trust:`, `Status:` and `Stale after:`; the `.json` gains `trustTier`, `verified`, `generatedBy`, `status` and `staleAfter`. `Updated:` now reads `generated.at` and falls back to the legacy `timestamp`, so a projection is correct on either side of a bundle's migration — without this the field would have silently blanked the moment a corpus migrated. The module's own flat frontmatter reader was deleted in favour of the checker's parser: a second, flat reader hands back `verified` as a raw string and reports every concept unverified, which is a wrong answer rather than a missing one.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — a frontmatter value that opens with a quote but does not close it is now a CHECK_1 error. Found by migrating a real corpus: `title: "Arranged For" — Third-Party…` is not valid YAML, and the old flat parser mangled it to `Arranged For" — …` and shipped that unbalanced quote into a projection heading. Neither parser errored, so the corpus carried invalid YAML nobody could see. 3 tests, 132 across the kit.

## 2026-08-09

* **Kit**: [scripts/okf_check.py](scripts/okf_check.py), [scripts/okf_graph.py](scripts/okf_graph.py) — three false-positive classes fixed, all found by pointing the checks at a second real bundle for the first time. A leading `/` in a link is bundle-root-relative, not filesystem-absolute (134 false broken links against 20 real targets); a Coverage Ledger `Status` may carry a note such as `Captured *(closed 2026-07-03 remediation pass)*`, which exact matching read as unresolved (8 false gaps in a ledger that had been deliberately remediated); and `.ai_context/` is agent scratch, which `okf_project.py` already excluded and `okf_check.py` did not. An annotated `Not yet checked` still fails, so the note cannot smuggle a row through.
* **Kit**: [tests/test_okf_check.py](tests/test_okf_check.py) — 5 tests, one per convention plus the case that must still fail. 109 across the kit.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.10.1.

## 2026-08-09

* **Kit**: [scripts/okf_new_bundle.py](scripts/okf_new_bundle.py) — new. Scaffolds a complete bundle as its own repo: kit attached as a pinned submodule, domain-only ontology, log, index, README, inbox, both `.command` wrappers and CI. Runs the checker before exiting, so a bundle is conformant at birth rather than at first use. Replaces a hand-written recipe that told you to copy the kit's ontology and cut it down — the copy-then-drift this layer exists to prevent.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py), [scripts/okf_project.py](scripts/okf_project.py) — **bundles now inherit the kit's registries** rather than copying them. Both read `okf-kit/ontology.md` first and merge the bundle's own on top, so a bundle declares domain additions only and has no copy to lose a rule from. The reference bundle now sees all 17 rules with none restated locally.
* **Kit**: [scripts/okf_project.py](scripts/okf_project.py) — two bugs found by scaffolding a real bundle. A subtree with its own ontology.md is a separate bundle and is no longer projected as content (a 4-file bundle reported 25 concepts). And the ALL-CAPS rule now tests the stem: `"README.md".isupper()` is False because of the extension, which had quietly projected README.md as a concept and pushed the reference bundle to 105.
* **Kit**: [templates/check.command](templates/check.command), [templates/update-kit.command](templates/update-kit.command) — promoted from the reference bundle so every new bundle gets them.
* **Kit**: [tests/test_okf_project.py](tests/test_okf_project.py) — tests for both bugs. 104 across the kit.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.10.0.

## 2026-08-09

* **Kit**: [ontology.md](ontology.md) — v0.8 → v0.9. New §Authority Posture: `authoritative` / `supporting` / `provenance` / `illustrative`, **declared per area rather than per document**, so a bundle carrying adjacent material can state the distinction once instead of maintaining a caveat in every file. Added V13 (WARNING): no authoritative concept may rest on supporting or illustrative material via `depends-on`, `part-of` or `derived-from`; `provenance` exempt, `references` not load-bearing. Unknown posture is an ERROR, an undeclared path defaults to `supporting`, and no declaration at all reports SKIP rather than silence.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py), [scripts/okf_project.py](scripts/okf_project.py) — V13 implemented against the extracted graph; posture carried per concept into the JSON, and an optional `Disclaimer` from §Projection carried in the master file's header.
* **Kit**: [tests/test_okf_graph.py](tests/test_okf_graph.py) — 9 posture tests. 102 across the kit.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.9.0.

## 2026-08-09

* **Kit**: [scripts/okf_project.py](scripts/okf_project.py) — new, and the gap it closes is the largest one found: the kit shipped no projection builder at all. The implementation lived only inside one target bundle, so every other bundle generated from this kit had no way to produce a master file. Now bundle-agnostic — slug, title, schema id and tag slices are read from a `# Projection` section in the bundle's own ontology, defaulting from the directory when absent. The JSON gains `edges`, so the relationship graph ships with the knowledge instead of being a separate command; an absent graph is reported with a reason rather than as an empty list.
* **Kit**: [tests/test_okf_project.py](tests/test_okf_project.py) — 15 tests building synthetic bundles in temp directories, so generality is asserted rather than assumed. 93 across the kit.
* **Kit**: [README.md](README.md), [AGENTS.MD](AGENTS.MD) — registered the builder and told PROJECTION_AGENT to run the kit's script rather than write a per-bundle one, since that duplication is what caused the drift.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.8.0.

## 2026-08-09

* **Kit**: [ontology.md](ontology.md) — v0.7 → v0.8. §Deliverable Parity Contracts gains `Record pattern` and `Source key pattern`, the machine-readable form of the `Identity key` column that was previously prose only. CHECK_7 becomes a real two-way set diff; without a `Record pattern` it reports SKIP and never PASS, because filename matching cannot see an orphan record. The kit stays format-agnostic — the contract declares how to read a hand-authored artifact rather than the kit guessing at HTML or JSON.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — CHECK_7 rewritten as a diff naming what is missing on each side. A clean diff is now a silent pass rather than a SKIP, which had said "could not decide" about the one case where it fully did. Guardrails for a pattern that matches nothing, an invalid regex, a multi-group pattern, and a source title with no extractable identity key.
* **Kit**: [docs/DECISIONS.md](docs/DECISIONS.md) — new. Ten decisions behind the two scripts, each with the measurement that drove it, what was rejected, and how to tell if it was wrong. Cross-referenced from both script docstrings, README.md and AGENTS.MD so a reviewer meets it before changing a severity or relaxing a guard.
* **Kit**: [tests/test_okf_check.py](tests/test_okf_check.py) — 7 CHECK_7 tests including the orphan case only a real diff can catch. 80 across the kit.
* **Kit**: [README.md](README.md), [AGENTS.MD](AGENTS.MD), [CHANGELOG.md](CHANGELOG.md) — v2.7.0.

## 2026-08-09

* **Kit**: [ontology.md](ontology.md) — v0.6 → v0.7. §Tag Taxonomy gains a **Certainty band** column (`>= 0.80`, `<= 0.95`, `0.60 - 0.90`); V12 enforces every declaration, so registering a certainty tag is a table cell rather than a rule. Bands ship empty — one domain's epistemics must not be hard-coded into every bundle. Instruction added to set the band to what the corpus actually holds: measured, the previously-stated bands were breached by 51 of 104 concepts, and a band tighter than authored practice fails a pile on day one and gets switched off. V12 is WARNING and stays one until a real bundle passes clean. **V3 rewritten** — a concept carrying `confidence` shows its working, either `confidence_sources` *or* a `# Citations` section. Measured: 0 of 104 concepts carry `confidence_sources`, 104 of 104 carry `# Citations`, so the old form was wrong for judgment-based corpora. Registered V10–V12 in the rules table.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — implements the rewritten V3 and new V12; an unreadable band is an ERROR, never silence, so a typo cannot switch the check off. **Fixed CHECK_5**: links inside fenced code blocks are examples, not links. Adding a worked example to `ontology.md` immediately produced three false positives against the kit itself. `okf_graph.py` had the same exposure and is fixed with it.
* **Kit**: [AGENTS.MD](AGENTS.MD) — CONFORMANCE_AGENT now lists V9–V12 and the `okf_graph.py` command, and is told explicitly not to resolve a V12 warning by re-grading a concept to fit a band. A band half the corpus breaches is the thing that is wrong; re-grading to satisfy it hides material rather than correcting it.
* **Kit**: [tests/test_okf_check.py](tests/test_okf_check.py) — 12 more tests covering band parsing, V12 severity, and the three V3 outcomes. 70 across the kit.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — `type: Stub` exempted from V3 and V12. A stub's `confidence: 0.0` means nothing asserted yet, not asserted weakly, so neither showing working nor sitting inside a certainty band applies. Found by running v2.6.0 against the reference bundle, where a `contested` stub at 0.0 read as outside its band — a correct reading of the rule and the wrong question to ask of a placeholder. Three tests; 73 across the kit.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.6.0, then v2.6.1 for the stub exemption.

## 2026-08-09

* **Kit**: [scripts/okf_graph.py](scripts/okf_graph.py) — new. Extracts typed edges from every `# Related` section; 384 edges across 101 concepts in the reference bundle, every target resolving. Parses a bold marker from the closed ten-item taxonomy, not prose — measured, 323 of 332 bullets already carry the marker and none relies on an unmarked English verb, so the standing caution against prose parsing does not apply. Joins wrapped continuation lines before matching, worth 18 edges alone.
* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — added V10 (every edge target resolves to a concept) and V11 (no edge points into an archived or superseded concept), both ERROR. V11 is the decay guard V6 could only half-cover. The graph module is imported lazily and its absence is reported as SKIP, never as a pass.
* **Kit**: [tests/test_okf_graph.py](tests/test_okf_graph.py) — new, 18 tests. 58 across the kit.
* **Kit**: [ontology.md](ontology.md) — v0.5 → v0.6. New §Writing a relationship so it can be traversed, and the decision that **relationships are directional with no registered inverses**: `referenced-by`, `depended-on-by`, `superseded` fail the build; put the edge on the other concept. Keeps the vocabulary closed at ten, which is what makes an unregistered relationship detectable.
* **Update**: [stubs/relationship-graph-extraction.md](stubs/relationship-graph-extraction.md) — its own `# Related` bullets rewritten to use the bold marker the new section requires. They used backticks and produced no edges, which the zero-edge guard caught on the kit itself.
* **Kit**: [docs/PLAN_GRAPH_AND_CERTAINTY.md](docs/PLAN_GRAPH_AND_CERTAINTY.md) — Part A marked done; inverse-form count corrected from four to six, the first figure having been read off a sample rather than counted.
* **Kit**: [README.md](README.md), [CHANGELOG.md](CHANGELOG.md) — v2.5.0.

## 2026-08-09

* **Kit**: [scripts/okf_check.py](scripts/okf_check.py) — new. Runs CHECK_1–CHECK_9 and V1–V9 in code, exit 0/1/2, `--json` available. The kit previously shipped no executable code, so every check was agent judgment; `build_projection.py` existed only in the `privacy-act-okf` instance and never came back upstream. Verified against both this kit and that bundle.
* **Kit**: [tests/test_okf_check.py](tests/test_okf_check.py) — new. 39 tests, one failing bundle per check plus a passing baseline.
* **Kit**: [ontology.md](ontology.md) — v0.3 → v0.4. Type Registry gained `Required Sections` and `Required Fields` on all three type tables plus a universal required-frontmatter list; `Typical Body Sections` retained as advisory so positional parsers still work. Added V9 to enforce them, and the V1–V9 reserved / `V-<slug>` bundle-rule naming convention, generalised from the live V5/V6 collision between this kit and `privacy-act-okf`.
* **Kit**: [AGENTS.MD](AGENTS.MD) — CONFORMANCE_AGENT must now run `scripts/okf_check.py` first and report its output, and must report NOT RUN rather than PASS if the script is missing. Its judgment is scoped to the three checks code cannot settle.
* **Kit**: [README.md](README.md) — registered `scripts/` and `tests/`; the conformance section now leads with the command.
* **Kit**: [ontology.md](ontology.md) — v0.4 → v0.5. Wrote down the conventions `okf_check.py` already enforces, so the spec and the code agree. V4 now carries its `archive/` exemption in the rule text; it previously contradicted §Concept Hierarchy Rules 5 outright for an archived stub, and only the checker knew the resolution. New §Conventions the checker depends on covers the `**Worked example**` marker (load-bearing — `**Example**` would make the checker read an illustration as a live contract), the rule that a subtree with its own `ontology.md` is a separate bundle, and the directories that are not concept trees.
* **Kit**: [CHANGELOG.md](CHANGELOG.md) — v2.4.0, then v2.4.1 for the above plus the V3 presence fix, which had reached log.md and the commit message but not the changelog.
* **Kit**: [docs/PLAN_GRAPH_AND_CERTAINTY.md](docs/PLAN_GRAPH_AND_CERTAINTY.md) — new. Staged plan for the two stubs, written against measurements of `privacy-act-okf` rather than against the spec, because they disagree. Part A (relationships): 104/104 concepts carry a `# Related` section, 323 of 332 bullets (97.3%) parse once wrapped lines are joined, and all 323 use the bold `**rel**` marker — none relies on inferring a relationship from an English verb, so this is not prose parsing and the standing caution against it does not apply. Four bullets use unregistered inverse forms, which is the real finding. Two to three days, one decision. Part B (certainty): 51 of 104 concepts breach the band their own tag declares, so the work starts with three questions for a human, not with a check. **Plan only — nothing implemented.**
* **Update**: [stubs/certainty-vocabulary-reconciliation.md](stubs/certainty-vocabulary-reconciliation.md) — corrected. It proposed "at most one tag from a mutual-exclusion group"; the corpus disproves that. Three concepts carry `confirmed` and `interpretation` deliberately — principle confirmed, enforcement dimension interpretation — so certainty attaches to a claim, not to a document, and a mutual-exclusion rule would break working practice. Also records that the stated bands themselves are in question, not just their enforcement.
* **Update**: [stubs/relationship-graph-extraction.md](stubs/relationship-graph-extraction.md) — added the measurements and the three named classes of parse failure.
* **Restructure**: [docs/PLAN_GRAPH_AND_CERTAINTY.md](docs/PLAN_GRAPH_AND_CERTAINTY.md) — renamed from `PLAN-graph-and-certainty.md`. `docs/` follows the ALL-CAPS rule (`KIT_RESTRUCTURE.md`, `OKF_DIVERGENCE.md`), so a mixed-case name was read as a concept document and failed CHECK_1 for having no frontmatter. The checker caught it; the naming rule already covered it.
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
