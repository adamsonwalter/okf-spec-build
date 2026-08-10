---
type: Ontology
title: Bundle Ontology
description: Single source of truth for all concept types, relationship semantics, tag taxonomy, and validation rules in this OKF bundle.
memory_tier: semantic
confidence: 1.0
okf_version: "0.1"
timestamp: 2026-07-03T05:26:26Z
tags: [ontology, system, governance]
---

> This file is maintained by agents (ENRICHMENT_AGENT, ONTOLOGY_AGENT) and by humans.
> It is the authoritative registry for this bundle. All agents MUST consult it before
> creating a new `type`, registering a new relationship, or adding tags.
> To extend the ontology: add an entry in the correct section below and update `timestamp`.
> Never delete entries — deprecate them (see §DEPRECATED TYPES).

---

# Type Registry

All valid values for the `type` frontmatter field in this bundle.
Agents MUST reject or flag any concept using a `type` not listed here,
and propose an addition via the ONTOLOGY_AGENT (see §EXTENDING).

## Required frontmatter — every concept, every type

These are required of any `lowercase.md` concept document regardless of type, and are
checked by V1 and by `scripts/okf_check.py`:

`type` · `title` · `description` · `timestamp` · `tags`

Anything a *particular* type needs beyond this list is declared in the **Required Fields**
column below, and anything it must contain in its body is declared in **Required Sections**.

**Typical vs Required.** `Typical Body Sections` is advisory — guidance for an author, never
checked. `Required Sections` and `Required Fields` are binding and are enforced. A type with
both columns empty is valid with only the universal frontmatter above; that is the normal case
for the generic core types, which are deliberately permissive.

**Declare, do not legislate.** A per-type requirement belongs in these two columns, not in a
new hand-written rule in §Validation Rules. One rule (V9) enforces all of them, so registering
a new type with its own requirements costs a table row and no new rule. Writing `V-xyz | Every
Legal Provision carries a Citations section` is the mistake this column exists to prevent — it
does not scale past a handful of types, and each such rule is separately unenforced until
someone codes it.

## Core Knowledge Types

| Type | Description | Typical Body Sections | Required Sections | Required Fields |
|---|---|---|---|---|
| `Concept` | A discrete idea, entity, or domain term. | Schema, Examples, Citations | — | — |
| `Playbook` | Step-by-step procedure for a known task. | Trigger, Steps, Outcome | — | — |
| `Decision` | A recorded decision with context and rationale. | Context, Options, Chosen, Rationale | — | — |
| `API Endpoint` | An external or internal API surface. | Schema, Authentication, Examples | — | — |
| `Metric` | A measurable quantity with definition and source. | Formula, Source, Caveats | — | — |
| `Reference` | A pointer to an external source or document. | Summary, Citations | Citations | `resource` |
| `Glossary Term` | A domain vocabulary definition. | Definition, Related Terms | — | — |
| `Person` | A named individual (role-based, not PII). | Role, Expertise, Related Concepts | — | — |
| `Organisation` | A company, team, or institution. | Description, Relationships | — | — |
| `Event` | A time-bound occurrence. | Date, Participants, Outcome | — | — |
| `Dataset` | A named collection of data. | Schema, Source, Access | — | — |
| `System` | A software system, platform, or tool. | Description, API Endpoint refs | — | — |
| `Process` | A recurring business or technical workflow. | Steps, Actors, Inputs, Outputs | — | — |

## Memory & Governance Types (system-managed)

> NOTE (v2.0): `Inference`, `Loop Health Report`, `Decay Report`, and
> `Contradiction Record`, plus the `confidence`/`memory_tier` fields, belong to
> the OPTIONAL T3 cognitive layer. A default (T1/T2) bundle does not use them.
> Field and rule definitions live in `optional/ontology-ext.md`.
>
> NOTE (v0.3): `Coverage Ledger` is the one exception — it is CORE, not
> optional-layer, and applies at every effort tier (T1/T2/T3). It is a
> completeness check (was everything captured?), not a correctness or
> confidence mechanism (is it right?), so it carries none of the T3
> confidence/memory-tier machinery and costs nothing extra for a T1 bundle to
> use on a whole-document ingestion.

| Type | Description | Created By | Required Sections | Required Fields |
|---|---|---|---|---|
| `Ontology` | This file. The bundle's type and relationship registry. | Human / ONTOLOGY_AGENT | — | — |
| `Stub` | A placeholder for a known gap. Confidence 0.0. | ENRICHMENT_AGENT (gap-finder) | — | — |
| `Inference` | A relationship or claim derived by an agent from existing concepts. | CONSUMPTION_AGENT | — | `inferred_from` |
| `Agent Instruction` | An instruction file for agent behavior (ALL CAPS .md files). | Human | — | — |
| `Loop Health Report` | Periodic diagnostic snapshot of bundle health metrics. | LOG_AGENT | — | — |
| `Decay Report` | List of stale, isolated, or low-confidence concepts. | CONFORMANCE_AGENT | — | — |
| `Contradiction Record` | A logged contradiction event and its resolution. | ENRICHMENT_AGENT | — | — |
| `Coverage Ledger` | An exhaustive inventory of every named structural unit in a source document (Box/Table/Figure/callout/appendix/quote), mapped to the bundle file(s) that capture it, with a Status column (Captured / Partial / N/A / Not yet checked). Built by ENRICHMENT_AGENT's `STATE: INVENTORY` on every SOURCE-DOCUMENT MODE ingestion — the mechanical completeness gate that checks whether everything was captured, distinct from correctness checks on what *is* captured. | ENRICHMENT_AGENT (STATE: INVENTORY) | — | — |

## Project-Specific Types

> Add domain-specific types below as the bundle grows.
> Format: `| Type | Description | Typical Body Sections | Required Sections | Required Fields |`
> Use `—` where nothing is required. Declaring a requirement here is what makes V9 enforce it —
> do not write a new validation rule for a per-type requirement.

*(empty at bundle initialisation — add as needed)*

---

# Relationship Taxonomy

Cross-links between concepts carry meaning inferred from surrounding prose.
This taxonomy standardises that meaning for agents and human readers.

Agents SHOULD annotate links with a relationship label in the surrounding prose.
The label does NOT appear in the markdown link syntax — it appears as natural language.

| Relationship | Direction | Prose signal | Example |
|---|---|---|---|
| `depends-on` | A → B | "requires", "built on", "cannot run without" | System A depends on API B |
| `implements` | A → B | "implements", "is an instance of", "follows" | Playbook implements Process |
| `contradicts` | A ↔ B | "disputes", "conflicts with", "challenges" | Decision A contradicts Metric B |
| `supersedes` | A → B | "replaces", "supersedes", "updates" | Concept A supersedes Concept B |
| `references` | A → B | "see", "refer to", "documented in" | Playbook references Dataset |
| `related-to` | A ↔ B | "related", "connected", "associated" | Concept A related to Concept B |
| `part-of` | A → B | "belongs to", "is part of", "component of" | Metric is part of System |
| `derived-from` | A → B | "derived from", "based on", "calculated using" | Metric derived from Dataset |
| `authored-by` | A → B | "authored by", "written by", "maintained by" | Playbook authored by Person |
| `governs` | A → B | "governs", "constrains", "regulates" | Ontology governs all Concepts |

## Writing a relationship so it can be traversed

A `# Related` bullet is an **edge**, not a sentence. `scripts/okf_graph.py` extracts these,
so the form below is load-bearing.

**Mark the relationship in bold, from the ten above.** Write `**depends-on**`, not the word
"depends" in a sentence. Measured across a 104-concept bundle, 323 of 332 bullets already do
this and none relies on an unmarked English verb — the marker is the convention in practice
and is now the convention in writing.

```markdown
- Anchored by the [POLA Act 2024](../framework/pola-act-2024.md) — **depends-on**.
- Key milestones: [Issues Paper](a.md), [GenAI guidance](b.md) — **references**.
```

One bullet carries **one** relationship and any number of links; each link becomes an edge.

**A bullet may wrap.** The extractor joins continuation lines before matching, so a marker on
the following line is still found.

**A bullet with links and no marker is a plain cross-reference.** That is allowed and produces
no edge. It warns, so the count stays visible.

### Relationships are directional — do not write the inverse

The taxonomy is **ten directional relationships and no inverses**. `**referenced-by**`,
`**depended-on-by**` and `**superseded**` are not registered and fail the build.

To say a thing backwards, put the edge on the other concept: if B is referenced by A, the
`**references**` bullet belongs in A, pointing at B. A consumer reads an edge in either
direction, so the inverse carries no information the forward edge does not.

This matches the reciprocal pattern V6 already enforces for `superseded_by` / `supersedes` in
frontmatter, and keeps the vocabulary closed at ten — which is what makes an unregistered
relationship *detectable* rather than merely unexpected.

*(Measured: six bullets in the reference bundle reach for an inverse — five `referenced-by`
and one `superseded`. Six authors reaching for the nearest word, not evidence of a missing
capability.)*

---

# Tag Taxonomy

All valid tags for the `tags` frontmatter field.
Tags are lowercase, hyphenated. Agents MUST use registered tags.
Unregistered tags trigger a Type Orphan gap flag (T3 only; see `optional/LLM_WIKI.MD` §GAP-FINDING).

## System Tags (reserved)

### Certainty bands — declared, not assumed

A bundle may use tags to express how settled a claim is (`confirmed`, `contested`,
`interpretation`, or whatever its domain calls them). Where it does, the tag may declare the
`confidence` range it implies, in the **Certainty band** column. V12 then enforces every
declaration, so a bundle registering a new certainty tag writes a table cell, not a rule.

Syntax: `>= 0.80`, `<= 0.95`, or `0.60 - 0.90`. An empty cell means the tag says nothing
about confidence and is never checked.

**Bands are a domain's epistemics, not the kit's.** The kit ships them empty. Do not
hard-code one bundle's vocabulary here.

**Set the band to what the corpus actually holds.** A band tighter than authored practice
does not raise quality — it fails a pile of concepts on day one, gets switched off, and then
looks present while enforcing nothing. That is how V3 was lost. Measure first, declare
second, and tighten only when the corpus has moved.

**V12 is a WARNING, and should stay one until a real bundle passes it clean.** Certainty is a
judgment; a band is a sanity check on that judgment, not an authority over it.

| Tag | Meaning | Certainty band |
|---|---|---|
| `system` | Bundle infrastructure: ontology, instructions, health reports | |
| `governance` | Policies, rules, constraints | |
| `stub` | Incomplete / placeholder concept | |
| `review-required` | Needs human or agent verification | |
| `archived` | Superseded or deprecated | |
| `inference` | Agent-derived, not directly sourced | |
| `disputed` | Contains an unresolved contradiction | |
| `coverage` | A Coverage Ledger or other bundle-completeness audit artifact | |

## Domain Tags

> Add project-specific tags below as the bundle grows.
> Format: `| tag-name | meaning | certainty band |`
> Leave the band empty unless the tag genuinely implies a confidence range.

*(empty at bundle initialisation — add as needed)*

---

# Concept Hierarchy Rules

OKF does not enforce a taxonomy, but this bundle follows these hierarchy conventions
to keep the directory structure navigable:

1. **Subdirectory = semantic group.** Group related concepts under a subdirectory
   when three or more concepts share a tag or parent type.

2. **No more than three levels deep.** `root/domain/subdomain/concept.md`.
   Deeper nesting degrades traversal. Flatten if you hit four levels.

3. **Stub concepts live in `stubs/`.** All `type: Stub` files go here until filled.
   When a stub is filled (content added, confidence > 0.50), ENRICHMENT_AGENT moves
   the file to its correct semantic subdirectory.

4. **Reports live in `reports/`.** All `type: Loop Health Report` and `type: Decay Report`
   files go here. Excluded from the main index.md sections; listed under `## Reports`.

5. **Archived concepts live in `archive/`.** All superseded concepts are moved here
   after supersession. They retain their frontmatter and body. They are excluded from
   active index.md sections but included in `## Archive` for auditability.

---

# Validation Rules

CONFORMANCE_AGENT checks these rules in addition to OKF v0.1 base conformance (§9):

| Rule | Check | Severity |
|---|---|---|
| V1 | Every concept's `type` is registered in this Ontology | ERROR |
| V2 | Every concept's `tags` are registered in this Ontology | WARNING |
| V3 | A concept carrying `confidence` shows its working — either `confidence_sources`, or a `# Citations` section | WARNING |
| V4 | Every `type: Stub` concept is in the `stubs/` subdirectory, **except** an archived stub, which lives in `archive/` per §Concept Hierarchy Rules 5 | WARNING |
| V5 | Every `type: Inference` has `inferred_from` listing at least one source | ERROR |
| V6 | No concept has `superseded_by` without a reciprocal `supersedes` in the target | ERROR |
| V7 | Every contradiction comment `<!-- CONFLICT -->` has a corresponding LOG entry | WARNING |
| V8 | This `ontology.md` file has `memory_tier: semantic` and `confidence: 1.0` | ERROR |
| V9 | Every concept carries the universal required frontmatter, plus its type's `Required Fields` and `Required Sections` from §Type Registry | ERROR |
| V10 | Every relationship edge target resolves to a concept in this bundle | ERROR |
| V11 | No relationship edge points into an archived or superseded concept | ERROR |
| V12 | A concept's `confidence` falls inside the declared band of every tag it carries | WARNING |
| V13 | No `authoritative` concept rests on `supporting` or `illustrative` material via `depends-on`, `part-of` or `derived-from` | WARNING |

## Conventions the checker depends on

`scripts/okf_check.py` reads this file. The conventions below are **load-bearing**: change
the wording and the checker's behaviour changes with it. They are declared here rather than
left as prose an agent infers, because that inference is precisely what code cannot do.

**`**Worked example**` marks an illustration.** In §Deliverable Parity Contracts and
§Source Coverage Contracts, a table following a line that begins `**Worked example**` is
never read as a live contract. The marker runs until the next heading.

Write it exactly. `**Example**`, `**Illustration**` or a plain sentence will cause the
checker to treat the illustration as a registered contract and fail the build against files
that were never meant to exist.

**A subtree with its own `ontology.md` is a separate bundle.** It is governed by that
registry, not this one, and the checker walks it as its own bundle rather than judging its
concepts against the parent. `ontology-mapper/pattern-library/` is the working example — its
`type: Pattern` concepts are valid there and unregistered here, and both statements are
correct. Check one by pointing at it: `python3 scripts/okf_check.py <dir>`.

**Not concept trees.** `inbox/` holds raw source documents awaiting ingestion,
`deliverables/` holds hand-authored artifacts, and `templates/` holds seeds for reserved
files. None carries concept frontmatter and none is checked. `archive/` and `stubs/` do hold
concepts and are checked.

## Rule numbering — kit rules and bundle rules must not collide

`V1`–`V9` are **reserved by this kit**. A bundle built from the kit inherits them and must not
renumber, redefine, or drop them.

A bundle adding its own rule MUST name it `V-<slug>` — `V-coverage-parity`,
`V-scenario-parity` — never a bare number. A bare number in a domain bundle either shadows a
kit rule or collides with the next one the kit adds.

**This is not hypothetical.** In `privacy-act-okf`, `V5` means scenario/deliverable parity and
`V6` means source coverage parity. In this kit `V5` means every `Inference` lists what it was
inferred from, and `V6` means no `superseded_by` without a reciprocal `supersedes`. Both are
ERROR in both places, so "V6 failed" means two unrelated things depending on which repo you are
standing in, and promoting either rule upstream would overwrite the other. That same bundle
also carries `V-T3a`/`V-T3b`, which are correctly named — so the convention was understood and
then not applied.

**Dropping a kit rule is a divergence, not a preference.** `privacy-act-okf` has no `V3`, and
104 concepts carrying `confidence` with zero `confidence_sources` — which is exactly what V3
exists to catch. Its own enhancements file records someone later puzzling over why V3 does not
exist. It does; it is here. Record a deliberate exclusion in §DEPRECATED TYPES or a bundle
note, so the next reader finds a decision instead of a hole.

---

# Authority Posture

Declares what each part of a bundle is **for**, so a reader — and a consuming application —
can tell an authoritative statement from supporting context.

**The point is that posture is declared per area, not per document.** New material inherits
the posture of where it lands, so an author adding a reference does not have to classify it,
and a bundle does not accumulate an unmaintainable set of per-file caveats.

| Posture | Meaning |
|---|---|
| `authoritative` | This bundle is the authority for these facts. Downstream bundles must not contradict them. |
| `supporting` | Reliable context that helps a reader apply the authoritative material. **Deliberately not a complete treatment**, and not to be cited as authority in its own right. |
| `provenance` | Source documents, audits and claim registers that the material above rests on. |
| `illustrative` | Worked examples and applied fact patterns. |

| Scope | Posture | Note |
|---|---|---|
| *(none at bundle initialisation — declare the first time a bundle carries material outside its own authority)* | — | — |

**Default is `supporting`** for any path matching no row. Understating authority is safe;
overstating it is not.

**V13** enforces the one thing that must not happen: an `authoritative` concept must not rest
on `supporting` or `illustrative` material through `depends-on`, `part-of` or `derived-from`.
Authority resting on context is the failure this section exists to catch — it is invisible in
prose and obvious in the graph. `provenance` is exempt, because resting on a source document
is what provenance *is*.

**V13 is a WARNING.** A posture boundary is a modelling judgment; the check surfaces where
authority and context have blurred, it does not adjudicate. See docs/DECISIONS.md D4.

**Posture travels into the projection**, per concept, so an application can render the right
caveat without the bundle repeating a disclaimer in every file.

---

# Deliverable Parity Contracts

> Most derived output never needs this section: `projections/` files are **regenerated in full**
> every time PROJECTION_AGENT runs, so they cannot silently drift. This section exists for a
> narrower, riskier case — a **hand-authored, self-contained interactive artifact** (an HTML/JS
> decision tool, a dashboard, a slide-deck generator, an embedded lookup table, etc.) that carries
> its **own denormalized snapshot** of one or more concept subdirectories, because it needs custom
> rendering PROJECTION_AGENT's flat-markdown output cannot produce. That snapshot is hand-edited,
> not regenerated — so the moment a concept is added, retired, or renamed and the deliverable is
> not touched in the same pass, it silently goes stale. Register a contract here **the first time**
> such a deliverable is built, and CONFORMANCE_AGENT will catch drift automatically from then on
> instead of relying on someone noticing.

**Format** — one row per deliverable that embeds a source-concept snapshot:

| Field | Meaning |
|---|---|
| `Contract ID` | Short slug identifying the contract. |
| `Deliverable file` | Path to the artifact, relative to bundle root (typically under `deliverables/`). |
| `Source scope` | The concept subdirectory, or a `type`/`tag` filter, being mirrored. |
| `Identity key` | Prose, for a human: how ONE record in the deliverable maps 1:1 to ONE source file. The two pattern columns below are the machine-readable form of the same statement. |
| `Record pattern` | A regex with **one capture group**, applied to the deliverable's text, yielding that deliverable's identity keys. This is what lets the checker diff a hand-authored artifact whose format the kit cannot know — the contract declares how to read it. Leave empty and the check falls back to searching for source filenames, which cannot detect an extra record and reports SKIP rather than PASS. |
| `Source key pattern` | A regex with **one capture group**, applied to each source file's `title`, yielding that file's identity key. Leave empty to use the filename stem. |
| `Severity` | `ERROR` (the deliverable ships broken or misleading to an end user/client) or `WARNING` (cosmetic drift only). Default to `ERROR` for anything client-facing. |

**Why two regexes and not a format reader.** A `deliverables/` artifact is hand-authored and
may be HTML, an embedded JSON blob, a slide deck — the kit has no business knowing. Declaring
how to read it keeps the kit format-agnostic and makes CHECK_7 a real set diff that names
what is missing on *each* side, including a record in the deliverable with no source file.
Same shape as everything else here: declare it in the registry, let one check enforce every
declaration.

**A contract with no `Record pattern` reports SKIP, never PASS.** Filename matching can only
prove that every source appears somewhere in the deliverable; it cannot see an orphan record,
and a check that cannot fully decide must not read as if it did.

| Contract ID | Deliverable file | Source scope | Identity key | Record pattern | Source key pattern | Severity |
|---|---|---|---|---|---|---|
| *(none at bundle initialisation — register the first time a hand-authored deliverable snapshots concept data; see worked example below)* | — | — | — | — | — | — |

**Worked example** (illustrative only — this is not a live contract in this seed ontology; shown
so a domain builder can copy the pattern exactly):

| Contract ID | Deliverable file | Source scope | Identity key | Record pattern | Source key pattern | Severity |
|---|---|---|---|---|---|---|
| `scenario-decision-map` | `deliverables/app-1-7-trigger-test-decision-map.html` | `scenarios/scenario-*.md` (one row per file) | Scenario letter — the concept's `title: "Scenario X — …"` matched against the deliverable's embedded `id` field | `"id"\s*:\s*"([A-Z])"` | `Scenario ([A-Z])` | ERROR |

This is the exact fix applied retroactively to the `privacy-act-okf` bundle after its
`scenarios/` directory grew to nine concepts (A–I) while its interactive decision-map deliverable
had silently stalled at seven (A–G) for several days — an *additive* new Scenario concept did not
read, on a first pass, like it triggered "update the deliverable", because the old instruction was
conditional ("if the new material changes scenarios…") rather than unconditional on any create/
retire event. See CHANGELOG.md [2.2.0] and AGENTS.MD §ENRICHMENT_AGENT / §CONFORMANCE_AGENT for
how this is now enforced unconditionally, at write time and at audit time, for every bundle built
from this kit — not just the one where the gap was first found.

---

# Source Coverage Contracts

> **Not the same problem as Deliverable Parity Contracts, above.** That section catches
> *concept → hand-authored deliverable* drift (a snapshot embedded in an HTML/JS artifact
> going stale after the source concepts change). This section catches a different failure:
> *source document → bundle* drift, where a named unit in the original source (a Box, Table,
> Figure, recurring callout, appendix, or cited case) was simply never transcribed into any
> concept file in the first place. There is no deliverable involved — the miss is in
> ENRICHMENT_AGENT's own INGEST/MAP pass, not in a downstream artifact. A bundle can be
> perfectly internally-conformant (every CHECK_1–8 passes) while still failing this, because
> none of those checks ever look back at the source document.
>
> **Enforced at ingestion time, not just audited afterwards.** AGENTS.MD §ENRICHMENT_AGENT's
> `STATE: INVENTORY` and `GATE_5-COVERAGE` make building this ledger a mandatory, blocking
> step of any SOURCE-DOCUMENT MODE ingestion — the pipeline cannot hand off to
> LINK_AGENT/LOG_AGENT while any ledger row is unresolved. CHECK_9 (AGENTS.MD
> §CONFORMANCE_AGENT) is the safety net for a bundle predating this mechanism, or a session
> that skipped STATE: INVENTORY — it is not the primary defence.

**Format** — one row per source document being tracked for bundle completeness:

| Field | Meaning |
|---|---|
| `Contract ID` | Short slug identifying the contract. |
| `Coverage ledger file` | Path to the `type: Coverage Ledger` concept enumerating every named unit in the source. |
| `Source document` | The source PDF/text being tracked (with version/date). |
| `Identity key` | How ONE row in the ledger maps to ONE structural unit in the source (a Box/Table/Figure number, a page-anchored callout label, an appendix letter). |
| `Severity` | `ERROR` if an uncaptured unit would misrepresent the source's scope to a reader relying on the bundle as complete (e.g. a director-facing checklist item, a safety procedure, a compliance clause); `WARNING` if cosmetic (e.g. a front-matter foreword). |

| Contract ID | Coverage ledger file | Source document | Identity key | Severity |
|---|---|---|---|---|
| *(none at bundle initialisation — register the first time a whole source document is ingested; see worked example below)* | — | — | — | — |

**Worked example** (illustrative only — this is not a live contract in this seed ontology; shown
so a domain builder can copy the pattern exactly):

| Contract ID | Coverage ledger file | Source document | Identity key | Severity |
|---|---|---|---|---|
| `directors-guide-coverage` | `errata/source-coverage-ledger.md` | *A Director's Guide to AI Governance* (AICD/HTI, v2, June 2026) | Box N / Table N / Figure N / page-anchored callout label / Appendix letter | ERROR |

This is the exact fix applied retroactively to the `directors-guide-ai-governance` bundle after
its 2026-07-03 canonical re-ingestion — despite a full sequential read of a 56-page source PDF —
still omitted four recurring "Questions for directors to ask" / "Governance red flags" boxes
entirely, plus three further named units (a "Ways boards can harness AI" box, an illustrative
example box, and a closing outlook section) that only surfaced once an exhaustive enumeration was
built after the fact. Root cause: a single self-review pass is correlated with its own blind
spots — it notices what looks substantively interesting and silently deprioritises what looks
repetitive or formulaic, even when the latter is real, required content. A second, independent
review caught the initial gap; building the ledger to close it then surfaced the rest
mechanically, without anyone re-reading the source a third time. See CHANGELOG.md [2.3.0] and
AGENTS.MD §ENRICHMENT_AGENT (`STATE: INVENTORY`, `GATE_5-COVERAGE`) / §CONFORMANCE_AGENT
(`CHECK_9`) for how this is now enforced unconditionally, at ingestion time and at audit time,
for every bundle built from this kit — not just the one where the gap was first found.

---

# ONTOLOGY_AGENT — Extension Protocol

When ENRICHMENT_AGENT encounters an unregistered `type` or `tag`, it does NOT silently
accept it. It triggers ONTOLOGY_AGENT:

```
AGENT: ONTOLOGY_AGENT
TRIGGER: Unregistered type or tag detected during ENRICHMENT or CONFORMANCE

ACTIONS:
  1. Propose the new type or tag entry in the correct section of ontology.md.
  2. Include: name, description, typical use, example concept.
  3. Write the proposed addition as a <!-- PROPOSED: --> comment at the bottom
     of the appropriate section in ontology.md.
  4. Set `review_required: true` in ontology.md frontmatter.
  5. LOG_AGENT records: **Ontology Proposal**: [type/tag name] — awaiting approval.
  6. HALT. Do not write the concept using the unregistered type until approved.

APPROVAL:
  A human (or agent with explicit authority) removes the <!-- PROPOSED: --> comment
  and promotes the entry to the active table. Removes `review_required: true`.
  LOG_AGENT records: **Ontology Extension**: [type/tag name] — approved and registered.

REJECTION:
  Human removes the <!-- PROPOSED: --> comment without promoting it.
  ENRICHMENT_AGENT maps the rejected concept to the nearest registered type.
```

---

# Deprecated Types

Types that were once valid but are no longer in use. Agents encountering these
types in existing concept files should flag for migration, not auto-migrate.

| Deprecated Type | Replaced By | Migration Note |
|---|---|---|
| *(none at initialisation)* | — | — |

---

# Ontology Version History

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-06-19 | Initial ontology for bundle bootstrap kit |
| 0.2 | 2026-07-03 | Added **§Deliverable Parity Contracts** — an opt-in registry for hand-authored interactive deliverables that embed a denormalized snapshot of a concept subdirectory. Generalises a bundle-specific fix (`privacy-act-okf` scenario/decision-map drift) into a reusable kit pattern. Empty template + one illustrative worked example; no live contract in this seed ontology. Paired with AGENTS.MD changes enforcing it at write time (ENRICHMENT_AGENT) and audit time (CONFORMANCE_AGENT CHECK_7). No new types/tags. |
| 0.3 | 2026-07-03 | Added type `Coverage Ledger` (Memory & Governance Types) and tag `coverage` (System Tags), plus new **§Source Coverage Contracts** — a *different* completeness mechanism from §Deliverable Parity Contracts: that section catches concept→deliverable drift; this one catches source-document→bundle omission, which involves no deliverable at all. Generalises a bundle-specific fix (`directors-guide-ai-governance` re-ingestion silently omitting four recurring content boxes despite a full sequential read) into a reusable kit pattern. Empty template + one illustrative worked example; no live contract in this seed ontology. Paired with AGENTS.MD changes enforcing it at ingestion time (ENRICHMENT_AGENT `STATE: INVENTORY` + `GATE_5-COVERAGE`, mandatory in the new SOURCE-DOCUMENT MODE) and audit time (CONFORMANCE_AGENT CHECK_9). See CHANGELOG.md [2.3.0]. |
| 0.4 | 2026-08-09 | Type Registry now **declares validity**, not just narrates it: added `Required Sections` and `Required Fields` columns to all three type tables, plus a universal required-frontmatter list. `Typical Body Sections` is retained and remains advisory, so any positional parser reading the first three columns is unaffected. Added **V9**, which enforces every type's declared requirements — registering a type with its own requirements is now a table row rather than a new hand-written rule, which is what stopped V-T3a-style per-type rules from scaling. Added the **rule-numbering convention**: V1–V9 are reserved by the kit, bundle rules must be `V-<slug>`. Generalised from a live collision — `privacy-act-okf` uses V5/V6 for parity checks while the kit uses them for inference sourcing and supersession reciprocity, both ERROR in both places. Paired with `scripts/okf_check.py`, which executes V1–V9 and CHECK_1–CHECK_9 in code. |
| 0.5 | 2026-08-09 | Wrote down the conventions the checker already enforces, so the spec and the code agree. V4 now carries its `archive/` exemption in the rule text — it previously contradicted §Concept Hierarchy Rules 5 outright for an archived stub, and only `okf_check.py` knew the resolution. Added §Conventions the checker depends on: the `**Worked example**` marker that keeps an illustration out of the live contract registries, the rule that a subtree with its own `ontology.md` is a separate bundle governed by its own registry, and the list of directories that are not concept trees. Each was implemented in code in v2.4.0 and documented nowhere an author would look. |
| 0.6 | 2026-08-09 | Relationships become traversable. Added §Writing a relationship so it can be traversed: a `# Related` bullet is an edge, the relationship is marked in bold from the closed ten, one bullet carries one relationship and any number of links, wrapped bullets are joined, and a bullet with links but no marker is an allowed cross-reference that produces no edge. **Relationships are directional and inverses are not registered** — `referenced-by`, `depended-on-by`, `superseded` fail the build; put the edge on the other concept instead. Keeps the vocabulary closed at ten, which is what makes an unregistered relationship detectable. Added V10 (every edge target resolves to a concept) and V11 (no edge points into an archived or superseded concept), both ERROR — V11 is the decay guard, since a superseded concept still cited in prose reads exactly like a live one and V6 only guards the frontmatter half. |
| 0.7 | 2026-08-09 | Certainty becomes checkable without imposing a vocabulary. §Tag Taxonomy gains a **Certainty band** column; V12 enforces every declaration, so registering a certainty tag is a table cell rather than a rule. Bands ship empty — they are a domain's epistemics, not the kit's — with the instruction to set them to what the corpus actually holds, because a band tighter than authored practice fails a pile of concepts on day one and gets switched off. V12 is WARNING and stays one until a real bundle passes clean. **V3 rewritten**: a concept carrying `confidence` must show its working — either `confidence_sources` *or* a `# Citations` section. The old form presumed confidence was computed from a countable set; measured against the reference bundle, 0 of 104 concepts carry `confidence_sources` and 104 of 104 carry `# Citations`, so the rule was wrong for judgment-based corpora and was silently dropped rather than argued with. Registered V10 and V11 from v0.6 in the rules table. |
| 0.8 | 2026-08-09 | CHECK_7 becomes a real set diff. §Deliverable Parity Contracts gains **`Record pattern`** (a one-group regex read against the deliverable's text) and **`Source key pattern`** (a one-group regex read against each source file's `title`, defaulting to the filename stem). The kit stays format-agnostic — a hand-authored artifact may be HTML, embedded JSON or a deck, and the contract declares how to read it rather than the kit guessing. The diff names what is missing on *each* side, so an orphan record in the deliverable is now detectable; filename matching never could see one. A contract with no `Record pattern` reports **SKIP, never PASS**. |
| 0.9 | 2026-08-09 | Added §Authority Posture — `authoritative` / `supporting` / `provenance` / `illustrative`, declared **per area rather than per document** so new material inherits its posture from where it lands. A bundle can now say what it is the authority for and what it merely carries as context, without maintaining a per-file caveat. Added **V13** (WARNING): no authoritative concept may rest on supporting or illustrative material via `depends-on`, `part-of` or `derived-from` — authority resting on context is invisible in prose and obvious in the graph. `provenance` is exempt, since resting on a source document is what provenance is. Posture travels into the projection per concept, and the §Projection section gains an optional `Disclaimer` carried in the projection header, so a consuming application receives the caveat with the knowledge instead of being trusted to add it. |
