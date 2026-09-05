# STATE_OF_PLAY.md — where the OKF work stands

**Written** 11 August 2026, after the 10 August migration pass. Written to be read **cold**,
a few days later, without the conversation that produced it.

`CHANGELOG.md` and each repo's `log.md` record *what* changed. This records **what it means**
and **what is still open** — the reasoning, and which decisions are still yours to make.

---

## The one-paragraph version

Google published **OKF v0.2** on 24 July 2026, and it **supersedes** the v0.1 this kit was
written against. It retires two fields we were using and — more importantly — it answers, in
the format itself, the question this kit had invented `confidence` to answer. The kit and both
bundles now track v0.2. Nothing was lost: the kit's own inventions (Coverage Ledgers, Authority
Posture, relationship markers, Parity Contracts) turn out to be **already conformant** as
extensions and were left alone. The corpus now states honestly what has been independently
verified — **18 of 104 concepts**, which is the migration working, not failing. Nothing else is
required. Everything remaining is a judgment call, listed at the bottom.

---

## The three repos, and what each is now for

| Repo | State | What it is for |
|---|---|---|
| **okf-spec-build** (the kit) | v2.12.0, ontology v1.0, tracks OKF v0.2 | The **machinery**. Checks, projections, agent instructions, the registry. Holds no knowledge. |
| **privacy-act-okf** (the bundle) | Migrated, conformant, 0 errors | The **knowledge**. 104 projected concepts. Pins the kit at `59a943b`. |
| **google-okf-generator** | `dcc09ce` | The **OKF v0.2 format engine**: validator, trust/staleness derivation, job model. Now in live use against a real corpus — see the open question below. |

On `google-okf-generator`: the ontology layer added on 6–9 August was removed and archived as
tag `archive/ontology-attempt`. Two genuine bug fixes from that period were kept. It is a
clean, literal v0.2 implementation — its spec citations were verified accurate section by
section — and on 11 August it was also used to build a real corpus, which is what raises the
question below.

---

## Open question — should the generator supersede the kit?

Raised 11 August after someone applied `google-okf-generator` to a real corpus and hit two
engine bugs (both since fixed: `dcc09ce`). The docs had said it was a reference, not a builder.
It is now demonstrably a builder, so the two-builders risk `ARCHITECTURE.md` exists to prevent
is live.

**Measured answer today: it cannot supersede the kit.** The generator implements the *format*
completely and the *production system* not at all. Retiring the kit right now would break, in
`privacy-act-okf`:

| What breaks | Scale | Kit component with no generator equivalent |
|---|---|---|
| Projections your live apps consume | 104 concepts, `.md` + `.json` | `okf_project.py` |
| Typed relationship graph | 388 edges | `okf_graph.py`, the ten markers |
| Ingestion completeness | 3 Coverage Ledgers | `STATE: INVENTORY`, `GATE_5`, CHECK_9 |
| Authority scope | 12 declared rows | Authority Posture, V13 |
| Bundle CI and `check.command` | both call `okf-kit/scripts/*` | — |
| Hand-authored artifact drift | — | Parity Contracts, CHECK_7 |
| Bundle scaffolding, agent pipeline | — | `okf_new_bundle.py`, `AGENTS.MD` |

Grep confirms the asymmetry: `projection` 0 files vs 23, `coverage` 0 vs 14, `authority
posture` 0 vs 12, `parity contract` 0 vs 12, `inventory` 0 vs 11.

**So "supersede" is a port, not a switch.** Three honest options:

1. **Keep both, boundary written down** — generator owns format conformance, kit owns
   production. Cheapest, and what the two currently are. Requires the boundary to be stated
   where a reader meets it, not just here.
2. **Port the kit's production layer onto the generator's engine**, then retire the kit's
   `okf_check.py`. Real work — the seven rows above — but it ends with one system.
3. **Port the generator's v0.2 engine into the kit** and retire the generator. Smaller: the
   kit already has the production layer, and its own v0.2 support now overlaps the generator's.

**Chosen: option 3** (11 August). Port the generator's v0.2 engine into the kit, then retire
the generator as a builder.

The deciding asset is `ontology.md` — **671 lines, v1.0**, live in the kit: 21 registered
types, the 10-relationship taxonomy, 8 system tags, **V1–V17**, plus Authority Posture,
Deliverable Parity Contracts, Source Coverage Contracts and the ONTOLOGY_AGENT extension
protocol. Porting the engine *into* the kit moves code onto that existing registry.

**Do not read this as "the generator had no ontology."** It had a substantial one, now archived
at tag `archive/ontology-attempt`, and it is a *different kind of artefact* — see the section
below. Whether parts of it should come back is open, and is not settled by the direction of the
port.

What the port actually involves (nothing is started):

| From the generator | Into the kit | Note |
|---|---|---|
| `derive.py` — trust tiers, staleness, status | already exists as `trust_tier()` / `is_stale()` | **overlaps; reconcile, do not duplicate** |
| `validate.py` §11 rule codes (`C1`, `C2`, `F_*`, `S_*`) | alongside CHECK_1–9 / V1–V17 | two rule vocabularies must become one |
| `yaml_lite.py` | kit's `split_frontmatter` | generator's is the more complete parser |
| Attested Computation (§10) | absent from the kit | the only wholly new capability |
| `job.py` / `okf.yaml`, engine-job-consumer | absent | decide whether the kit wants a job model at all |

**Do the rule-vocabulary reconciliation first and on its own.** Two sets of codes for the same
conformance criteria is how a check ends up enforced twice with different severities, or
believed to be enforced and not running — the failure D13 already caught once here.

Until the port lands, the boundary stands: the generator is the format reference, the kit is
the builder. What must not happen is both being edited as builders — that is precisely the
drift the architecture was written to prevent.

---

## Reopened — was the archived ontology the better one?

Raised 11 August. Worth taking seriously, because the two "ontologies" are not competing
versions of one thing and the earlier rollback did not compare them on the merits.

| | Kit `ontology.md` | Archived `archive/ontology-attempt` |
|---|---|---|
| What it is | a **governance registry**, 671 lines of prose | a **typed-graph mechanism**, 775 lines of code + 235 coverage + a 107-line schema |
| Relationships | 10 markers in `# Related` prose, regex-extracted | instance-level `edges: [{relation, to}]` in frontmatter, schema-checked |
| Constraints | direction only | `from`/`to` classes, `cardinality`, `inverse` |
| Reverse traversal | none — D2 rejects inverses; put the edge on the other concept | generated `derived_edges` index; build rejects a stale one |
| World assumption | open — an unmarked bullet is a WARNING | **closed** (`closed: true`) — absence of an edge is a *fact* |
| Instance resolution | none; classes are document genres | `identity`, `title_key`, `properties` — an instance can be *resolved*, not just categorised |
| Completeness of answers | none | **competency questions** with traversal paths, enforced by the build |

**Two things the archived layer does that the kit cannot do at all.**

*Instance resolution.* Its own closing note says the analytics classes are document genres, and
that "a domain-entity ontology — provisions of an instrument, contract clauses, obligations —
should instead give each class an `identity`, a `title_key`, and `properties`." That is
`privacy-act-okf` exactly. The kit classifies by genre (`Legal Provision`, `Reference`), which
is the mode that note calls *merely categorised*.

*Competency questions.* `coverage.py` declares the questions a bundle is warranted to answer,
each with the traversal path that answers it, and the build checks the structure exists — no
model, no answer evaluation. It also carries `out_of_scope` entries **with a stated reason**.
That is a mechanised form of the operative constraint recorded in D4: *a reader must be able to
explain why they are not seeing something.* Nothing in the kit does this. Its worked examples
are privacy-domain — `is-app-entity`, `not-small-business-operator`, `s-6d`, penalty units — so
it was aimed at this corpus from the start.

**What the rollback argument actually covered.** It was that the marker taxonomy *described
existing practice* (323 of 332 bullets already used a bold marker before the rule was written)
while typed edges *legislated new structure*. That argument still stands — **for the
relationship layer**. It never addressed the coverage layer, which has no counterpart here.

**So the piece most worth reconsidering is competency-question coverage, not the closed typed
edge graph.** Test it the way this kit tests everything (D3, D4): measure the corpus first. The
question is whether there are answers `privacy-act-okf` is expected to give that its 388
prose-marker edges cannot support — if yes, the coverage layer earns its way back; if no, the
rollback was right and should be left alone.

---

## The fact that reframed everything

**OKF v0.2 is real, published, and supersedes v0.1.** `GoogleCloudPlatform/knowledge-catalog`
PR #227, merged 24 July 2026. Its §13 says so in terms.

That mattered in three ways:

1. **Two of our fields were retired.** `timestamp` → `generated: { by, at }`, and the body
   `# Citations` list → the `sources` frontmatter family (§13.1). Not style preferences — a
   corpus written against a revision that no longer exists.
2. **The section numbers moved.** Conformance is now **§11**, not §9. Every reference in the
   kit was pointing at the wrong place.
3. **The spec now answers the trust question itself**, and answers it better than we did — see
   below.

---

## Why trust tiers replaced the `confidence` float

v0.2 §5.1 declines to store a credibility score, by name and with reasoning:

> it does not store a credibility score: a score is subjective, unportable across consumers,
> and goes stale. Credibility is *inferred* from the signals, not stored.

Instead, §5.3 **derives** a tier from `verified`: `unverified` → `machine-confirmed` (verified
only by non-`human:` actors) → `human-reviewed` (any `human:` actor).

**Why that is better and not merely different.** A tier names *who* confirmed a concept and
*when*. It is auditable, it cannot drift from what actually happened, and it regenerates itself
from the facts. `confidence: 0.9` is a number somebody chose, and nothing updates it when the
underlying authority moves. For a corpus whose whole value is that a sceptical counsel cannot
fault it, "verified by X on date Y" is materially stronger evidence than a decimal.

**What survived.** The certainty *tags* (`confirmed`, `contested`, `interpretation`). They
answer a genuinely different question — how settled a **claim** is, versus who checked the
**document** — and D5 measured concepts legitimately carrying more than one. Only the stored
float is superseded in substance.

---

## Question 1 — do the kit and the spec serve different purposes?

**Yes, and the split is clean. OKF is the wire format; the kit is the factory.**

**The spec answers a reader's questions** about a concept someone handed them: where did this
come from, how well is it verified, is it still current, was this number computed the
sanctioned way. Everything in v0.2 is per-concept and self-describing, because the consumer may
have no relationship with the producer.

**The kit answers a maintainer's questions** about a corpus being continuously grown: did we
capture everything in that 56-page PDF, is this bundle the authority for this claim or merely
carrying context, has the hand-built HTML tool drifted from the concepts, did anyone commit
without logging. None of those are per-concept, and none survives being handed to a stranger —
they are properties of the **process**, not the artifact.

That is why neither absorbs the other, and why running one corpus through two builders would be
a mistake.

---

## Question 2 — how to stay on-spec while keeping the dialect

The existing principle was already right: **"we write a stricter OKF than we read."** v0.2 adds
one constraint to it:

> **Strictness must be additive, never a redefinition.**

Sort every divergence into three classes. **Only one is a real conflict.** Full register in
[`OKF_DIVERGENCE.md`](OKF_DIVERGENCE.md); reasoning in [`DECISIONS.md`](DECISIONS.md) D11.

| Class | What it is | Action | Status |
|---|---|---|---|
| **A — debt** | Retired fields, moved section refs | Fix | **Done** |
| **B — additive extension** | Coverage Ledgers, Authority Posture, relationship markers, Parity Contracts | Keep | **Already conformant** — §4.1 requires consumers to tolerate unknown keys and unknown `type` values |
| **C — house rules** | Five required frontmatter fields, closed type vocabulary | Keep | Legitimate, but **never report as non-conformance** |

**Class C is the line.** `okf_check.py` may report a bundle as *outside this kit's dialect*. It
must never report a **spec-conformant** bundle as non-conformant. That is the single thing that
would actually put the kit off-spec.

**The decision rule in practice:**

| Corpus | Posture |
|---|---|
| Handed to a third party, or consumed by an app you don't control | Strict v0.2 core; extensions optional and clearly separable |
| Grown internally, liability-grade, completeness matters | v0.2 core **plus** the Class B extensions — still conformant |
| Either | Never reject on Class C; those govern **writing** only |

The point worth remembering in a few days: **you never had to choose between the kit and the
spec.** Class A was the only real conflict, and it is paid off.

---

## Question 3 — can the ontology be contributed upstream?

**The type-registry half cannot, and should not be proposed.** v0.2 §1 lists *"Defining a fixed
taxonomy of concept types"* as its **first non-goal**, and §4.1 states types are not registered
centrally and consumers MUST tolerate unknown ones. A mandatory closed vocabulary is the one
thing OKF has ruled out at both revisions. It stays permanently ours — which is fine, it is a
producer rule and it works.

**The governance half is genuinely additive, and needs no permission to use.** Three pieces sit
entirely outside the non-goals:

- **Coverage Ledgers + the `INVENTORY` gate.** OKF has no notion of **completeness**. Every
  §11 criterion is satisfiable by a bundle that transcribed 60% of its source. The
  `directors-guide` failure — four recurring boxes missed despite a full sequential read — is a
  failure mode the spec cannot currently express.
- **Authority Posture.** v0.2 has trust tiers (*how well verified*) but nothing on authority
  **scope** (*is this bundle the authority, or carrying someone else's*). Different axis, and
  it only appears once there is more than one bundle. **This is the strongest upstream
  candidate** — a real gap rather than an addition.
- **The ten relationship markers.** §6.1 explicitly says links are untyped and the relationship
  "is conveyed by the surrounding prose."

**Why the relationship markers are not the thing we deleted from `google-okf-generator`.** That
layer imposed a closed-world frontmatter graph and made the *absence* of an edge a fact. The
kit's version reads a bold marker out of prose authors were already writing — **323 of 332
bullets used it before the rule existed** — stays a WARNING when unmarked, and asserts nothing
about what is not there. One described existing practice; the other legislated new structure.
That difference is the whole reason one added value and the other did not, and it is the
argument to make if this is ever proposed.

**Would it materially help OKF's own use cases? Be honest: it depends on the corpus.** For
catalog cases (BigQuery tables, GA4) completeness and authority barely register — the source
*is* the schema. For document-derived, liability-grade corpora they are the difference between
one you can defend and one you cannot. That is a strong argument for an **extension** and a
weak one for a core change.

**Recommended shape, if pursued:** *"OKF Knowledge Governance Extension — conformant with v0.2
§4.1; adds completeness and authority-scope conventions for document-derived corpora."*

**Recommended sequencing:** do **not** open with a spec PR. The repo has no tags, no releases,
and v0.2 landed as one squashed PR from a single Google author with no visible
external-contribution process. Open an issue describing the completeness gap, gauge whether
anyone engages, and publish the extension note yourself in the meantime — it needs nobody's
permission.

---

## What is open — ranked, and whose call each is

### 1. Review horizons (`stale_after`) — **yours, highest value**

The mechanism shipped; **no horizon is set on any concept**. This is the single highest-value
remaining field: it turns "check for stale concepts" from an agent prompt into a date
comparison, and it converts the 86-concept verification backlog from a flat list into a
prioritised queue.

Staleness is **advisory and cannot gate** — V17 is a WARNING by construction ([`DECISIONS.md`](DECISIONS.md)
D12). Your live apps cannot be taken offline by a date.

Proposed classes, to correct rather than accept:

| Material | Horizon | Why |
|---|---|---|
| Statutory text — APP wording, s 13G/13H penalties | 12–18 months | The Act does not move; review is a formality |
| OAIC guidance interpretation | ~6 months | Guidance is live; the enforcement sweep is running |
| Pending / unlegislated — Tranche 2, proposed reforms | ~3 months | Where the corpus goes wrong fastest |
| Advisory framing, scenarios | inherit from what they depend on | A scenario is only as fresh as the provision under it |

Test any candidate before committing to it:

```bash
python3 okf-kit/scripts/okf_check.py . --today 2026-12-11
```

### 2. Promote the 18 verified concepts to `human-reviewed`? — **yours, one question**

They are recorded as `machine-confirmed` because both auditors (the 29 Jul claim audit, the
3 Jul hard-error register) were logged as `process:` actors. **If you personally cross-graded
either audit**, those become `human-reviewed` — a one-line change per concept and a genuine
strengthening. Understating was the safe default; only you know whether it understates.

### 3. Work down the verification backlog — **yours, ongoing**

86 of 104 concepts derive as `unverified`. Not a regression: it is the corpus stating what has
actually been independently checked, where a `confidence` float previously implied a judgment
nothing regenerated. Horizons (item 1) are what make this a queue instead of a list.

### 4. The bundle boundary — **open, mechanical**

`privacy-act-okf`'s bundle root **is** its repo root, so concepts, machinery (`okf-kit/`),
working state (`inbox/`) and exports (`projections/`) share one tree. **33 `.md` files** carry
no frontmatter. Under a literal §11.1 walk that bundle does not conform; it passes only because
our checker knows a private exclusion set a third party does not. Two fixes, neither done:
publish the exclusion set in `ontology.md` (cheap), or move concepts under `bundle/` (correct,
and what `google-okf-generator` does). Recorded in [`OKF_DIVERGENCE.md`](OKF_DIVERGENCE.md).

### 5. The extension note — **yours, optional**

Per Question 3. Needs no permission and no one's agreement.

---

## Four traps

1. **Do not set `stale_after` to 10 Dec 2026.** A commencement date is a fact *in* the content,
   not a review horizon. Made a horizon, the entire corpus expires on one day, every answer in
   every app warns simultaneously, and the warning becomes noise you switch off. That is D4's
   recorded lesson verbatim — *"that is how V3 was lost."*
2. **Never promote V17 to ERROR.** It would take a live legal corpus offline on a **date**
   rather than on a **defect** — and stale is not wrong. A concept can be inaccurate the day it
   is written and accurate a year past its horizon. There is a test asserting this.
3. **Never call a Class C finding "non-conformant."** Outside this kit's dialect, yes.
   Non-conformant with OKF, no.
4. **Do not "migrate the Class B extensions to the spec."** They are conformant as they stand.
   The naive reading of "get on-spec" deletes the Coverage Ledger and Authority Posture work for
   no reason. This is why D11 sorts before it migrates.

---

## If you read nothing else

The kit and both bundles are on v0.2, conformant, tested (143 kit tests), pushed. **Nothing is
required of you.** The corpus is more honest than it was: it now says what has actually been
checked rather than implying it with a number.

The one thing genuinely worth doing next is **setting review horizons** — it is what makes the
verification backlog workable, and it cannot break anything because staleness only ever warns.
