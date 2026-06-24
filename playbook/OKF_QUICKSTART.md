# OKF Quickstart — new domain in one afternoon

Companion to RAPID_OKF_PLAYBOOK.md. Print this; run it per domain.

## A. Domain intake — 10 questions (answer these first)
1. Domain name + one-line purpose of the bundle.
2. Who/what consumes it? (you / clients / field crews / a cheap model)
3. Effort tier? (T1 personal / T2 advisory / T3 compliance) — see playbook §1.
4. What are the core entity TYPES? (6–15, e.g. Mandate, Dimension, Procedure, Risk, Vendor, Decision)
5. What TAGS will you filter/subset by? (the cuts you'll want for other LLMs)
6. Topic INVENTORY: list the 10–30 subjects the bundle must cover.
7. Sources: what documents/notes/transcripts exist, and which are authoritative?
8. Any liability/safety-critical numbers or rules? (if yes → T3 for those topics)
9. Known CONFLICTS or contested points to watch?
10. Update cadence + who adds knowledge over time?

Output of intake → register types/tags in `ontology.md`; save topic inventory as `TODO.md`.

## B. Setup checklist
- [ ] `git clone kit <domain>`; confirm AGENTS.MD/LLM_WIKI.MD/FEEDBACK_LOOP.MD present
- [ ] Add `inbox/ projections/` if missing
- [ ] Register domain types + tags in `ontology.md` (from intake Q4/Q5)
- [ ] Save topic inventory to `TODO.md` (from Q6)
- [ ] Drop sources into `inbox/`
- [ ] Run: "Read AGENTS.MD, LLM_WIKI.MD, ontology.md; ingest inbox/"
- [ ] Tier pass: T1 none · T2 provenance+light check · T3 figures+conflict sweeps+regression
- [ ] `git add -A && git commit -m "v1 <domain>" && git tag v1`
- [ ] Build first projection(s) → `projections/`; upload to your cloud tool(s)

## C. Per-update checklist (batch)
- [ ] Drop new material in `inbox/`
- [ ] Run "ingest inbox/"
- [ ] Review any `<!-- CONFLICT -->` flags
- [ ] (T3) extend regression set per new conflict/critical value
- [ ] Re-project changed subsets; re-upload to cloud tools
- [ ] `git commit`

## D. Projection one-liner (filter by tag → single file)
"Concatenate every concept whose tags include <TAG> into projections/<TAG>.md, each with its
title + source reference, newest first." Then upload that one file to the LLM's project/knowledge.

## E. Anti-patterns (what made it slow before)
- Hand-authoring concepts instead of batch-ingesting → let the pipeline write them.
- Over-verifying T1/T2 work to T3 standard → match effort to consequence.
- Editing the kit per domain → keep the kit frozen; vary only ontology + content.
- Pushing the live repo into every LLM → push small projections instead.
- One giant bundle for everything → one bundle PER domain; subset across with tags.

© 2026 Walter Adamson | BHP 20 years, Head IT Audit - IT Strategy - Corporate Planning - International Bus Development | 100+ AI workflow solutions delivered | linkedin.com/in/adamson | walter@outcomesnow.com
