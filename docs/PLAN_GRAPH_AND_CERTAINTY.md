# Plan — relationship traversal, and reconciling the two certainty systems

**Written** 9 August 2026. Covers the two gaps tracked in
[`stubs/relationship-graph-extraction.md`](../stubs/relationship-graph-extraction.md) and
[`stubs/certainty-vocabulary-reconciliation.md`](../stubs/certainty-vocabulary-reconciliation.md).

Both were deliberately left out of kit v2.4.0. This plan is written against **measurements
of a real 104-concept bundle** (`privacy-act-okf`), not against the spec, because the spec
and the corpus turn out to disagree in one of the two cases — and that disagreement is the
whole problem.

---

## What was measured, and what it changes

Two numbers decide the shape of everything below.

### Relationships are already a marked syntax, not prose

| Measure | Result |
|---|---|
| Concepts with a `# Related` section | **104 / 104** |
| Total relationship bullets | 332 |
| Parse once line-wrapping is handled | **323 (97.3%)** |
| Recognised bullets using the bold `**rel**` marker | **323 / 323 — 100%** |
| Bullets naming more than one relationship | **0** |

The ontology describes relationships as a "prose signal" with the label appearing "as natural
language". In practice **every single one** is written `**depends-on**`, `**references**`,
and so on. Nothing relies on inferring a relationship from an English verb.

That changes the risk profile completely. `ENHANCEMENTS.MD` in the bundle warns that "parsing
prose is what caused every corpus defect found this week" — correct, and it does not apply
here, because this is not prose parsing. It is parsing a bold marker drawn from a closed
ten-item vocabulary, in our own format. The remaining judgment is in the sentence around the
marker, which we do not need.

### Certainty: the corpus and the stated bands disagree half the time

| Measure | Result |
|---|---|
| Concepts with a certainty tag | **104 / 104** |
| Carrying `confirmed` + `interpretation` together | 3 |
| **Breaching the band their own tag declares** | **51 / 104 — 49%** |

`AGENTS.MD` in the bundle states the mapping: `confirmed` ≥ 0.95, `interpretation` ≤ 0.8.
Measured against the corpus:

| Tag | n | confidence range | stated band |
|---|---|---|---|
| `confirmed` | 71 | 0.8 – 1.0 | ≥ 0.95 |
| `interpretation` | 24 | 0.6 – 0.95 | ≤ 0.8 |
| `contested` | 12 | 0.65 – 0.85 | — |

**Enforcing the stated bands today would fail 51 of 104 concepts.** That is not a corpus in
need of cleanup. A rule that half the material breaks was never the rule the authors were
actually following, and shipping it as an ERROR would simply get it dropped — which is
precisely what happened to V3.

**So the certainty work does not start with a check. It starts with a decision.**

### A correction to the stub

`stubs/certainty-vocabulary-reconciliation.md` proposes, among other things, that a concept
carry "at most one tag from a mutual-exclusion group". **The evidence says no.**

Three concepts carry `confirmed` *and* `interpretation`, and the 30 July log entry for
[`app-1-3-policy-currency`] records why deliberately: *"Principle `confirmed`; enforcement
dimension `interpretation`."* One concept, two claims, two different certainties. That is
correct modelling, not a tagging error.

**Certainty attaches to a claim, not to a document.** Any rule treating the tags as mutually
exclusive would break working practice. The stub is corrected accordingly.

---

## Part A — Make relationships traversable

Lowest risk of the two, highest immediate value, and the measurements say it is close to
free. Do this first.

### A1 · Close the taxonomy honestly (half a day)

The 9 unparsed bullets are not noise. They fall into three named classes, and two of them are
telling us the taxonomy is short:

| Class | Count | Example | What it means |
|---|---|---|---|
| **Unregistered inverse forms** | 4 | `**referenced-by**` ×3, `**superseded**` ×1 | Authors need to say a relationship *backwards* and the taxonomy has no way to |
| **Bullet truncated at a section boundary** | 2 | line ends `— ` with nothing after | Wrapping/authoring artefact |
| **Genuine cross-reference, no relationship** | 3 | "…sits outside this ladder — see [x]" | Not a typed edge at all |

**Decide the inverse question before writing any parser.** Two options:

- **(a) Directional only.** `references` is stored once, A → B, and a consumer reads the edge
  in either direction. `**referenced-by**` becomes a validation error telling the author to
  put the edge on the other concept. Simplest, keeps the taxonomy at ten, and matches
  `supersedes`/`superseded_by`, which the frontmatter already handles as a reciprocal pair.
- **(b) Register the inverses.** `referenced-by`, `depended-on-by`, `part-of` ↔ `has-part`.
  Doubles the vocabulary and creates a reciprocity problem for every pair.

**Recommendation: (a).** V6 already establishes the reciprocal-pair pattern for supersession,
and four uses across 332 bullets is not evidence of a need — it is evidence of four authors
reaching for the nearest word.

Also register `supersedes` past-tense usage as an error, not a synonym; `**superseded**`
should point at the frontmatter field, which the checker already validates.

### A2 · Extract in `scripts/`, count everything (one day)

New module, `scripts/okf_graph.py`, sharing the frontmatter parser already in
`okf_check.py`.

```
extract_edges(bundle) -> [ {source, target, relationship, line} ]
```

Non-negotiable conditions, both drawn from what already exists in the kit:

1. **Join wrapped continuation lines before matching.** Measured: this alone moves recognition
   from 91.9% to 97.3%. A parser that skips wrapped bullets would silently drop 18 real edges.
2. **Count what is extracted, and fail on zero.** Same reasoning already written into
   `build_projection.py`'s empty-registry failure — an extraction yielding no edges is
   indistinguishable from a bundle with no relationships.
3. **An unregistered relationship fails the build.** It does not get dropped. The taxonomy is
   closed at ten, which is exactly what makes this decidable.
4. **A bullet with a link but no marker is a WARNING, not an error.** Three exist today and
   they are legitimate prose cross-references. Warn so the count is visible; do not force
   authors to type a marker on every sentence containing a link.

### A3 · Two new checks (half a day)

Both are the decay guards the stub was written for, and both are pure set operations once
edges exist:

- **`V10` — every edge target resolves to a concept on disk.** CHECK_5 already checks that a
  *link* resolves; this checks that a *typed edge* points at something that is a concept.
- **`V11` — no edge points at an archived or superseded concept.** This is the one that
  matters. A `supersedes` edge still cited in prose currently reads exactly like a live one,
  and V6 only guards the frontmatter half.

### A4 · Emit into the projection (half a day)

Add an `edges` array to `<bundle>-master.json`, beside `concepts`. A consumer can then show
what a concept depends on, warn when a superseded concept is cited, or walk from an obligation
to the gate that triggers it — the thing the ontology has promised since v0.1.

Do **not** put edges in the markdown projection. That file exists so a model can read the
bundle whole; edges there are noise it would have to parse back out.

**Part A total: two to three days.** Ends with the graph traversable and two decay classes
guarded.

---

## Part B — Reconcile the two certainty systems

Bigger, and the first stage is not code.

### B1 · Decide what the tags mean (a conversation, not a task)

Three questions, in order. Nothing below can be built until they are answered, and answering
them wrongly produces a rule that gets dropped.

**1. When the number and the tag disagree, which is authoritative?**
Today 49% disagree. Options: the tag wins and confidence is advisory; the number wins and the
tag is derived from it; or they measure different things and both stand — in which case say
what each measures, because "confidence" and "confirmed" reading as synonyms is the whole
problem.

**2. What does `confidence` actually count?**
The kit's V3 requires `confidence_sources` alongside it, which presumes confidence is derived
from a countable set. In `privacy-act-okf` it plainly is not — it is editorial judgment backed
by a `# Citations` block, which is why V3 was dropped there. Either confidence is a computed
ratio (and V3 is right), or it is a judgment (and V3 is wrong for this class of bundle, and
should say so).

**3. Are the stated bands aspiration or specification?**
`confirmed` ≥ 0.95 fails 40+ concepts today. Either the band moves to fit authored practice
(`confirmed` ≥ 0.8 would fit the measured corpus) or the corpus moves to fit the band. The
first is an afternoon; the second is a re-grading pass over 104 concepts.

### B2 · Declare bands in the ontology, per bundle (half a day)

Once B1 is answered, the mechanism is the **same shape as the v0.4 Type Registry change**:
declare it in a registry, let one rule enforce every declaration.

Extend §Tag Taxonomy with two optional columns:

| Tag | Meaning | Certainty band | Exclusive group |
|---|---|---|---|
| `confirmed` | Enacted text or explicit regulator statement | `>= 0.80` | — |
| `contested` | Under active consultation | `0.60 – 0.90` | — |
| `interpretation` | Reasoned inference | `<= 0.90` | — |

A bundle that does not use certainty tags leaves both columns empty and nothing changes.
The kit ships them empty — `confirmed`/`contested`/`interpretation` are **one domain's
epistemics** and must not be hard-coded into every bundle.

**Leave `Exclusive group` unused unless a bundle genuinely needs it.** Per the correction
above, `confirmed` + `interpretation` on one concept is meaningful, and the column exists for
a bundle that has a real exclusion, not to police this one.

### B3 · One rule, one check (half a day)

**`V12` — a concept's `confidence` falls within the declared band of every certainty tag it
carries.** Severity **WARNING**, not ERROR, for at least one release. A rule that would fail
half a corpus on day one gets switched off, and a switched-off rule is worse than none because
it looks present.

Promote to ERROR only once a real bundle passes it clean.

### B4 · Revisit V3 with the answer to B1.2 (half a day)

If confidence is a judgment rather than a count, V3 as written is wrong for judgment-based
bundles. Either scope it (`WARNING`, and only where a bundle declares confidence as computed),
or replace `confidence_sources` with a requirement that already fits practice — a `# Citations`
block, which `V-T3a` in `privacy-act-okf` already demands and 104 concepts already have.

That would close the V3 divergence honestly rather than by exemption.

**Part B total: two to three days, of which the first stage is a decision.**

---

## Sequencing and cost

| Stage | Effort | Blocked by |
|---|---|---|
| A1 close the taxonomy (inverse question) | 0.5 d | one decision |
| A2 extractor | 1 d | A1 |
| A3 V10, V11 | 0.5 d | A2 |
| A4 edges in the JSON projection | 0.5 d | A2 |
| B1 decide what the tags mean | — | **Walter** |
| B2 bands in §Tag Taxonomy | 0.5 d | B1 |
| B3 V12 as WARNING | 0.5 d | B2 |
| B4 revisit V3 | 0.5 d | B1.2 |

**Do Part A first**, entirely. It is nearly mechanical, the corpus is already 97% conformant,
and it delivers the decay guards that matter most in a legal bundle. Part B cannot start until
the three questions in B1 are answered, and answering them badly is worse than leaving the gap
open — which is why v2.4.0 left it open.

## Decisions needed

1. **Inverse relationships** — directional only, or register the inverses? *(recommend:
   directional only)*
2. **Number vs tag** — which is authoritative when they disagree?
3. **What `confidence` counts** — a computed ratio, or editorial judgment?
4. **The bands** — move the band to fit the corpus, or re-grade the corpus to fit the band?

Nothing in Part B should be built before 2, 3 and 4 are settled.
