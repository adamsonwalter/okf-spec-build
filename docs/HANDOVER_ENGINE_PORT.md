# HANDOVER_ENGINE_PORT.md — for the next coder (human or AI)

**Written** 11 August 2026. You are picking up a decided but **unstarted** piece of work:
folding the OKF v0.2 engine from `google-okf-generator` into this kit, and deciding which
parts of an archived ontology layer come back with it.

Read in this order, then come back here:

1. [`STATE_OF_PLAY.md`](STATE_OF_PLAY.md) — where everything stands and why
2. [`DECISIONS.md`](DECISIONS.md) — **D1, D2, D3, D4, D11, D12, D13**; do not change a check
   before reading the one that shaped it
3. [`OKF_DIVERGENCE.md`](OKF_DIVERGENCE.md) — how this kit relates to the published spec
4. [`../ontology.md`](../ontology.md) — the registry every rule reads

**Nothing below is started. Nothing below is authorised beyond what it says.** Where a step
needs a judgment that is the owner's, it says so.

---

## 0. The governing idea — read this before touching anything

The question that produced this document: *the sources are of different kinds — legislation and
standards on one hand, company knowledge and operating procedures on the other. Can one system
serve both, or does deterministic checking make universality impossible?*

**It is a false dilemma, and this kit already resolved it.** The resolution is D1:

> A per-type, per-tag or per-contract requirement is a **table cell in `ontology.md`**, never a
> new hand-written rule. One rule plus a registry column scales to any number of types at zero
> marginal cost.

That is **universal mechanism, per-bundle vocabulary**. Determinism does not require a universal
taxonomy; it requires a *declaration*, and the declaration belongs to the bundle. The evidence is
in the code, not just the doctrine:

```python
# scripts/okf_check.py — V1
if known_types and concept_type not in known_types:
```

Register nothing and the rule never fires. `load_registries()` reads **that bundle's**
`ontology.md`, and a subtree carrying its own `ontology.md` is treated as a separate bundle
governed by its own registry (D10). The checker never knows your domain. It only ever checks
what a bundle has declared about itself.

This is also the spec's own design: §4.1 says type values are **not** registered centrally and
consumers MUST tolerate unknown ones; §11 makes consumption permissive. A *producer* may still
be as strict as it likes — which is this kit's "we write a stricter OKF than we read", now
constrained by D11's rule that strictness must be **additive, never a redefinition**.

**Consequence for the port: every capability you add must be opt-in per bundle and inert when
undeclared.** A legislation bundle can be strict; an SOP bundle can declare nothing and pay
nothing. If a change makes an undeclared bundle fail, the change is wrong.

---

## 1. Instance vs document — the distinction that actually matters

An earlier framing ("document genres vs analytics classes") came from the archived layer's
analytics example and does not map onto real sources. Discard it. The distinction that decides
whether a class needs machinery is:

**Does a reader need to resolve a specific instance, or find a relevant document?**

| Reader's question | Kind | What the class needs |
|---|---|---|
| "What does s 42 amend?" / "Does APP 1.7 bite here?" | **instance** | `identity`, `title_key`, typed edges |
| "What is our escalation procedure?" | **document** | genre + tags is enough |

**Both kinds live inside one corpus.** `privacy-act-okf` holds provisions (instances: APP 1.7,
s 6D) *and* advisory framing (documents). A company-knowledge bundle holds SOPs (documents)
*and* systems, roles, processes (instances).

So this is a property of a **class within a bundle** — not of a bundle, and emphatically not of
a system. Do not split the system along source type. There is no legislation build and no SOP
build; there is one build reading different declarations.

---

## 2. The archived ontology layer — what to take, what to fix

At tag `archive/ontology-attempt` in `google-okf-generator`: `src/okf/ontology.py` (775 lines),
`src/okf/coverage.py` (235), and a 107-line example schema. Reverted 10 August, and the
revert's stated reason — that the marker taxonomy *described existing practice* (323 of 332
bullets already carried a bold marker) while typed edges *legislated new structure* — is sound
**for the relationship layer**. It never addressed the rest.

Two capabilities have no counterpart in this kit:

- **Instance resolution.** Classes with `identity`, `title_key`, `properties`. The archived
  file's own closing note says a domain-entity ontology — "provisions of an instrument,
  contract clauses, obligations" — needs these, and that classifying by genre leaves an
  instance *merely categorised*. That is `privacy-act-okf` exactly.
- **Competency-question coverage** (`coverage.py`). Declares the questions a bundle is
  warranted to answer, each with the traversal path that answers it, and the build checks the
  structure exists. Its `out_of_scope` entries carry a **stated reason** — a mechanised form of
  the owner's constraint recorded in D4: *a reader must be able to explain why they are not
  seeing something.* Its worked examples (`is-app-entity`, `not-small-business-operator`,
  `s-6d`, penalty units) were aimed at this corpus from the start.

### The one design error to correct on the way in

The archived layer set **`closed: true` by default**. That imposes a contract on a bundle that
never asked for one, and it is the same failure shape as D4: a rule stricter than authored
practice fails a pile of concepts on day one, gets switched off, and then looks present while
enforcing nothing. *That is how V3 was lost.*

**Invert the default.** Open unless a bundle opts in, per bundle and per class:

- legislation / standards → declare `identity`, opt into `closed: true`. Closure earns its keep
  here: "no provision links this obligation to that entity type" is a real answer.
- company knowledge / SOPs → declare nothing extra; nothing fires; cost is zero.

That is D1 applied to the ontology layer instead of only to types and tags.

---

## 3. The hard limit — state it, do not try to beat it

**Deterministic checking verifies structure. It never verifies meaning.** The archived coverage
module says so itself:

> It is deterministic — no model is involved, and it does not evaluate an answer. It checks that
> **the structure needed to answer exists**.

This is exactly why universality survives. Every check asserts only a structural claim the
bundle made about itself: V1 registration, V9 presence, V10 resolution, CHECK_9 an unresolved
ledger row. **None of them reads the law.** The moment a check tries to judge whether content is
*correct*, it needs domain knowledge and stops being universal.

If you find yourself adding a rule that requires knowing what a concept *means*, stop. That
belongs to a reviewer, or to a competency question that checks the path exists — not to a
checker.

---

## 4. The port, in order

Work packages. **Do them one at a time, each with its own commit and its own verification.**
Package A is a prerequisite for everything else.

### A. Reconcile the two rule vocabularies — first, and alone

The generator uses `C1`, `C2`, `C3`, `F_*`, `S_*` against spec §11. This kit uses
`CHECK_1`–`CHECK_9` and `V1`–`V17`. They overlap on the same criteria — parseable frontmatter,
non-empty `type`, reserved-file structure — with **different codes and potentially different
severities**.

- Produce a mapping table of every generator code to its kit equivalent, marking each
  `identical` / `narrower` / `wider` / `no equivalent`.
- Where both exist, keep **one**. Record which and why in `DECISIONS.md`.
- Where severities disagree, the spec wins for conformance criteria (§11 is permissive) and the
  kit's house rule wins for producer strictness — per D11 Class C, and it must never be
  reported as non-conformance.

**Why first:** two vocabularies for one criterion is how a check ends up enforced twice at
different severities, or believed to run and not running. D13 caught exactly that failure here
once already.

**Done when:** the mapping table is committed, no criterion has two live codes, and the full
suite passes.

### B. Fold in the parser

`src/okf/yaml_lite.py` (generator) is more complete than this kit's `split_frontmatter` — it
handles block scalars (`|`, `>`, with chomping), flow mappings, block lists of mappings, and
round-trips multi-line values as block scalars. This kit's was extended on 10–11 August for
nested `verified`/`sources` and rejects half-quoted values.

Take the generator's, port this kit's additions onto it, keep **one** parser. Both repos have
tests; keep both sets.

**Done when:** one parser, both test suites green, and `okf_project.py` output for
`privacy-act-okf` is byte-identical apart from its build stamp.

### C. Reconcile the derivations

`derive.py` (generator) and `trust_tier()` / `is_stale()` (kit) implement the same §5.3 and §5.5
logic. **Overlap — reconcile, do not duplicate.** Keep the kit's signatures; the projections and
V17 already depend on them.

**Done when:** one definition of each, and `okf_check.py --today` behaviour is unchanged.

### D. Decide on the job model — owner's call, do not assume

`job.py` / `okf.yaml` / the engine-job-consumer split has no counterpart here; this kit uses a
pinned-submodule model instead (`OPERATING.md`). These are two answers to the same question.
**Do not port it silently.** Put the choice to the owner with the trade-offs.

### E. Attested Computation (§10) — the only wholly new capability

Absent from this kit. `privacy-act-okf` has no Attested Computations today, but it does carry
computed figures (penalty by turnover, the ~$167M threshold) that are candidates.

Port it only if the owner wants it. If ported, note D12: §10.5 mandates refusal for a **failing
attestation** — that is the one thing in the spec that legitimately refuses, and it is distinct
from staleness, which must stay advisory.

### F. Ontology layer — measure before building

Per D3 and D4, decide by measuring the corpus, not by re-reading files. The question:

> Are there answers `privacy-act-okf` is expected to give that its 388 prose-marker edges cannot
> support?

Write the candidate competency questions first, check whether existing edges already answer
them, and only then decide. If yes, bring back **coverage first** (it is additive and inert when
undeclared) and instance resolution second. The closed typed-edge graph is the least urgent and
the most invasive; it stays reverted unless the measurement demands it.

### G. Retire the generator as a builder

Only after A–C land and the owner confirms. Update `STATE_OF_PLAY.md`, and leave the repo as a
spec-conformance reference with its harness intact — it is the independent check on this kit's
reading of the spec, which is worth keeping even when it is no longer a builder.

---

## 5. Rules you must not break

1. **Never report a spec-conformant bundle as non-conformant.** House rules may require more
   than §11; they may not reject what §11 permits. D11, Class C.
2. **Never promote V17 to ERROR.** Staleness warns; it never gates. A live corpus must not go
   offline because a date passed. D12, and there is a test asserting it.
3. **Never default a new capability to strict.** Inert when undeclared. §0 and §2 above.
4. **Never add a check that needs to know what a concept means.** §3 above.
5. **A horizon is a review cycle, not a content date.** Do not set `stale_after` to the
   10 Dec 2026 commencement; it expires the corpus in one day. D12, D4.
6. **Log before commit.** Append to `log.md` in the same commit — `playbook/BUNDLE_COMMIT_CHECKLIST.md`.
7. **Do not commit projection artefacts to this kit.** It holds no knowledge and registers no
   artefacts; `.gitignore` covers `projections/*-master.*`. A stray local run got committed once
   and defeated a CI fix.

---

## 6. How to verify anything you change

```bash
cd okf-spec-build
python3 -m unittest discover -s tests     # 145 tests, must pass
python3 scripts/okf_check.py .            # must exit 0
```

```bash
cd privacy-act-okf
python3 okf-kit/scripts/okf_check.py .    # 0 errors, 11 warnings, 132 files
python3 okf-kit/scripts/okf_project.py .  # projections must rebuild identically but for the stamp
```

```bash
cd google-okf-generator
PYTHONPATH=src python3 tests/harness.py   # 139 cases, CLEAN PASS
```

**Both guards, every time.** This kit's harness discipline is false-positive *and*
false-negative: prove the new check fires on the bad case, and prove it stays silent on the good
one. A check that cannot fail is the same defect as a check that never ran — D13.

CI is green on both repos as of 11 August. It had **never** passed before that day; if it goes
red, read D13 before assuming the bundle is at fault.

---

## 7. State of the three repos, 11 August 2026

| Repo | HEAD | Role |
|---|---|---|
| `okf-spec-build` | v2.12.0, ontology v1.0 | the kit — machinery and registry; **the builder** |
| `privacy-act-okf` | conformant, 0 errors, 104 projected concepts | the knowledge; pins the kit |
| `google-okf-generator` | `dcc09ce`, harness 139/139 | OKF v0.2 format engine; **source of the port** |

Open items owned by the owner, not by you: review horizons (`stale_after`, none set anywhere),
whether the 18 machine-confirmed concepts are actually human-reviewed, the undefined bundle
boundary, and packages D, E and F above.
