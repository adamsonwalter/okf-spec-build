# DECISIONS.md — why the checks are shaped the way they are

Design decisions behind `scripts/okf_check.py` and `scripts/okf_graph.py`, recorded so a
reviewer does not have to reverse-engineer the reasoning or re-litigate a settled trade-off.

Each entry states the decision, the evidence, what was rejected, and how to tell if it was
wrong. Where a decision was driven by measurement, the numbers are from `privacy-act-okf`
(104 concepts) as at 9 August 2026.

**The governing principle, stated once.** A check that did not run and a check that passed
must never look the same afterwards. Every decision below follows from that, and any change
that blurs the two is a regression regardless of how much noise it removes.

---

## D1 · Declare in the registry; let one rule enforce every declaration

**Decision.** A per-type, per-tag or per-contract requirement is a **table cell in
`ontology.md`**, never a new hand-written rule.

- Required frontmatter/sections per type → columns in §Type Registry, enforced by **V9**
- Confidence range per certainty tag → column in §Tag Taxonomy, enforced by **V12**
- How to read a deliverable's records → columns in §Deliverable Parity Contracts, used by
  **CHECK_7**

**Why.** `privacy-act-okf` had hand-written `V-T3a` ("every Legal Provision carries a
Citations section and a confidence field"). That does not scale past a handful of types, and
each such rule is separately unenforced until somebody codes it — which nobody did. One rule
plus a registry column scales to any number of types at zero marginal cost.

**Rejected.** Hard-coding domain vocabulary into the kit. `confirmed`/`contested`/
`interpretation` are one domain's epistemics. The kit ships every band **empty**.

**Wrong if.** Registering a new type or tag starts requiring code changes again.

---

## D2 · Relationships are directional; inverses are unregistered

**Decision.** The taxonomy is ten directional relationships. `referenced-by`,
`depended-on-by` and `superseded` **fail the build**. To say something backwards, put the
edge on the other concept.

**Evidence.** Six bullets in the reference bundle reached for an inverse — five
`referenced-by`, one `superseded`. Of the three examined, two already had the forward edge on
the target concept, so the inverse was pure duplication.

**Why.** A closed vocabulary is what makes an unregistered relationship *detectable* rather
than merely unexpected. Registering inverses doubles the vocabulary and creates a reciprocity
problem for every pair — V6 already shows what that costs for `supersedes`/`superseded_by`.
A consumer reads an edge in either direction, so the inverse carries no information.

**Rejected.** Silently normalising `referenced-by` into a reverse `references` edge. It would
work, and it would teach authors that unregistered vocabulary is fine, which is how a closed
taxonomy stops being closed.

---

## D3 · Parse the marker, not the prose

**Decision.** `okf_graph.py` extracts an edge from a **bold marker** (`**depends-on**`) drawn
from the closed taxonomy. It never infers a relationship from an English verb.

**Evidence.** 104/104 concepts carry a `# Related` section; 323 of 332 bullets carry a bold
marker; **zero** rely on an unmarked verb. The convention already existed — it was written
down, not imposed.

**Why this is not the prose-parsing that `ENHANCEMENTS.MD` warns against.** That warning is
about inferring meaning from natural language. This reads a delimited token from a ten-item
closed set, in the kit's own format, and fails on anything outside it.

**Watch for.** Wrapped continuation lines. Joining them before matching is worth **18 edges**
in the reference bundle — a parser that treated a wrapped bullet as unparseable would drop
them silently. That is why `logical_bullets()` exists and why it is not an optimisation.

---

## D4 · Set bands to what the corpus holds, and never re-grade to fit a band

**Decision.** Certainty bands are measured from authored practice. **V12 is a WARNING** and
stays one until a real bundle passes clean. `AGENTS.MD` explicitly forbids resolving a V12
warning by moving a concept's confidence.

**Evidence.** The previously-stated mapping (`confirmed` ≥ 0.95, `interpretation` ≤ 0.8) was
breached by **51 of 104 concepts**. Measured practice: `confirmed` 0.80–1.00, `contested`
0.65–0.85, `interpretation` 0.60–0.95.

**Why.** A rule half the corpus breaks was never the rule its authors were following. Shipped
as an ERROR it gets switched off, and a switched-off rule is worse than none because it looks
present. This is exactly how V3 was lost.

**The operative constraint, from the bundle owner.** A reader must be able to explain why they
are **not** seeing something. Bulk re-grading makes that unanswerable — a concept changes
category, an expert asks "what about X", and the answer is buried in a mass edit. So every
change here is additive: bands moved, nothing was re-graded, nothing disappeared.

**Wrong if.** A band ever gets tightened without measuring the corpus first.

---

## D5 · Certainty attaches to a claim, not to a document

**Decision.** No mutual-exclusion rule on certainty tags. A concept may carry more than one.

**Evidence.** Three concepts carry `confirmed` **and** `interpretation`, deliberately. The
30 July log entry for `app-1-3-policy-currency` records the reasoning: *"Principle
`confirmed`; enforcement dimension `interpretation`."*

**Rejected.** An earlier draft of `stubs/certainty-vocabulary-reconciliation.md` proposed
"at most one tag from a mutual-exclusion group". Measuring the corpus killed it. The stub
carries the correction; do not reinstate it without new evidence.

---

## D6 · A `Stub` is a placeholder, not a claim

**Decision.** `type: Stub` is exempt from **V3** (show your working) and **V12** (band).

**Why.** A stub's `confidence: 0.0` means *nothing asserted yet*, not *asserted weakly*.
Neither rule has anything to check. A `contested` stub at 0.0 was reported as outside its
0.60–0.90 band — a correct reading of the rule and the wrong question to ask of a placeholder.
The same exemption cleared 10 of 11 remaining V3 warnings, all archived stubs.

**Note.** The exemption turns on **what the file is**, not on its number. A non-stub concept
at confidence 0.0 is still checked.

---

## D7 · V3 asks for working, not for a count

**Decision.** A concept carrying `confidence` must show its working — **either**
`confidence_sources` **or** a `# Citations` section.

**Evidence.** `confidence_sources`: **0 of 104**. `# Citations`: **104 of 104**.

**Why.** The original form presumed confidence is computed from a countable set. In a legal
corpus it is editorial judgment backed by citations. The rule was wrong for that whole class
of bundle, and rather than being argued with it was silently dropped — the bundle's own
enhancements file later records someone puzzling over why V3 did not exist. It did; it was
upstream.

**Presence, not truth.** `confidence_sources: 0` is a declared zero and must not read as a
missing field. That bug flagged every properly-formed stub, including the kit's own.

---

## D8 · CHECK_7 diffs on declared patterns; without one it reports SKIP, never PASS

**Decision.** A Deliverable Parity Contract may declare a `Record pattern` (one-group regex,
read against the deliverable) and a `Source key pattern` (one-group regex, read against each
source file's `title`). With them, CHECK_7 is a **real set diff in both directions**. Without
a `Record pattern` it falls back to filename matching and reports **SKIP**.

**Why the fallback cannot be a pass.** Filename matching proves every source appears
*somewhere* in the deliverable. It cannot see an **orphan** — a record in the deliverable with
no source concept — so it cannot decide parity, and must not read as though it had.

**Why two regexes rather than a format reader.** A `deliverables/` artifact is hand-authored
and may be HTML, embedded JSON, or a deck. The kit has no business knowing. Declaring how to
read it keeps the kit format-agnostic — the same shape as D1.

**Guardrails, each learned from a real failure.** A pattern matching nothing is *reported*,
not diffed, because it would otherwise make every source file look missing. An invalid regex
is an ERROR. A multi-group pattern is an ERROR. A source title that the key pattern cannot
match is an ERROR naming that file — a source with no identity key is undiffable, and silently
dropping it would shrink the comparison set.

---

## D9 · Guards trigger on principle, not on thresholds

**Decision.** The zero-edge guard fires when **zero edges were extracted while linked
`# Related` bullets exist**. Zero edges with no linked bullets is a SKIP.

**Why no threshold.** "Fail if fewer than N edges" fails a freshly cloned seed bundle, which
gets the check switched off. The principled trigger asks whether there was anything to extract
*from*, which is decidable and needs no magic number.

**Same reasoning elsewhere.** An empty registry section fails the build in
`build_projection.py` — "an empty registry is indistinguishable from a permissive one".

---

## D10 · Things the checker must not treat as concepts

**Decision, and the rule behind each:**

| Excluded | Why |
|---|---|
| `inbox/` | Raw source documents awaiting ingestion |
| `deliverables/` | Hand-authored artifacts |
| `templates/` | Seeds for reserved files, deliberately frontmatter-free |
| `projections/` | Regenerated from the concepts; checking them double-reports every finding |
| ALL-CAPS `.md` | Agent instructions, per the naming rule in `README.md` |
| a subtree with its own `ontology.md` | A separate bundle, governed by its own registry |

`archive/` and `stubs/` **are** concept trees and remain checked.

**Note on code fences.** Links inside a ``` fence are examples, not links. Adding a worked
example to `ontology.md` immediately produced three false positives against the kit itself.
A checker that cries wolf teaches authors to ignore it.

---

## Open, deliberately

- **Penalty-table parity.** Removed from `privacy-act-okf`'s deliverable contract: its eight
  records live *inside* one or two concept files, so a file-per-record diff has nothing to
  map. Needs a row-inside-a-file mechanism. Recorded in that bundle's `ENHANCEMENTS.MD`
  rather than left inside a contract that cannot check it.
- **Three scenarios with no edge to the trigger-test gate.** They never mention it in their
  text. Adding the edge anyway would be asserting a relationship the concept does not make;
  the question is recorded for a domain expert, not resolved in code.
- The two `stubs/` gaps, unchanged in status.
