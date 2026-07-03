# Rapid OKF Playbook — Stand up a knowledge bundle per domain in hours, not a week

**Purpose:** make OKF setup repeatable and cheap across many domains (accounting M&A, civil HDD,
HVAC AI control, grid OT comms, your own interest groups…), so each new domain is a *clone + intake*,
not a rebuild — and so the bundle is usable across cloud LLMs and local git environments, with simple
batch updates.

---

## 0. The one idea that fixes the "it took a week" problem

The Optus job was long because of **source verification** (PDF sweeps, reading figures, classifying
cross-manual conflicts) — NOT because of OKF mechanics. The bundle assembly itself is one agent pass.

So separate two layers and never re-do the first:

| Layer | What it is | How often built |
|---|---|---|
| **Invariant kit** | `AGENTS.MD`, `LLM_WIKI.MD`, `FEEDBACK_LOOP.MD`, ontology seed, pipeline | Built ONCE. Copied unchanged per domain. |
| **Domain content** | ontology types/tags, concepts, ingestion tasks | Per domain, but mostly automated. |

And right-size the effort. Optus was liability-critical (field NCRs) so it earned figure
reconciliation + conflict sweeps + a regression harness. Most of your domains do **not** need that.
Pick a tier (below) and skip what you don't need. **Over-verifying is the real time sink.**

---

## 1. Effort tiers — choose before you start

| Tier | Use for | Verification you DO | Verification you SKIP |
|---|---|---|---|
| **T1 Personal / insight** | your interest groups, your own knowledge, drafts | type+tag, source note, timestamp | figure reading, conflict sweeps, regression |
| **T2 Client advisory** | accounting M&A, engineering advisory, most client work | + provenance per claim, light cross-source check, confidence field | figure pixel-reading, formal regression set |
| **T3 Compliance / liability** | civil HDD, HVAC control safety, grid OT, anything causing fines/injury | + figure reconciliation, conflict sweeps, regression harness (the full Optus method) | nothing |

Rule of thumb: a claim that, if wrong, costs money/safety/legal → T3. A claim that's "my thinking" → T1.

---

## 2. The reusable template repo (build once)

Keep ONE pristine template repo — your "kit". Per domain you `git clone` it into a new repo.
**Do not author domain content into the kit itself** (note: this `okf-spec-build` currently holds
the Optus `optus-ug/` content — for cleanliness move that to its own repo and keep the kit clean).

Template contents (already exist here):
```
kit/
├── AGENTS.MD            # 6-agent orchestrator (ingest/link/index/log/consume/conform)
├── LLM_WIKI.MD          # memory tiers, confidence, supersession
├── FEEDBACK_LOOP.MD     # batch synthesis loop
├── ontology.md          # SEED only (system types) — domain types added at intake
├── index.md  log.md
├── inbox/               # ADD THIS — drop raw inputs here for batch ingest
├── projections/         # ADD THIS — exported subsets for cloud LLMs
├── templates/           # Seeds — copy log-domain-init.md → log.md on first clone
├── playbook/            # Includes BUNDLE_COMMIT_CHECKLIST.md (log before every commit)
├── tasks/               # ADD THIS — pipeline (copy the generic ones; specialise per domain)
├── deliverables/        # OPTIONAL, per-domain — hand-authored client artifacts (HTML tools,
│                         #   dashboards). If one embeds a concept-data snapshot, register a
│                         #   Deliverable Parity Contract in ontology.md the same session (see §6b).
└── stubs/ reports/ archive/
```

Add three folders to the template once: `inbox/`, `projections/`, `tasks/` (generic pipeline).
`deliverables/` is created per-domain only when a bespoke artifact is actually built — see Step 6b.

---

## 3. Per-domain setup — the 6-step rapid path (target: a few hours)

**Step 1 — Clone.** `git clone kit <domain>` → new repo. (2 min)

**Step 1b — Domain log.** Copy `templates/log-domain-init.md` → `log.md`; set today's date and
the domain name. A domain bundle tracks its own mutations — not the kit's release history. (1 min)

**Step 2 — Domain intake (the only "thinking" part).** Answer a 10-question intake (see
`OKF_QUICKSTART.md`) to produce: (a) 6–15 domain **types**, (b) domain **tags**, (c) a **topic
inventory** (the list of subjects the bundle must cover), (d) the **effort tier**. Register types/tags
in `ontology.md`. (~30–60 min)

**Step 3 — Gather sources into `inbox/`.** PDFs, your notes, transcripts, prior deliverables, web
pages. No processing yet — just collect. (variable, mostly your existing material)

**Step 4 — Batch ingest.** In a local agent env (Cowork/Cursor/Antigravity) say:
*"Read AGENTS.MD, LLM_WIKI.MD, ontology.md, then ingest everything in inbox/."* The ENRICHMENT→LINK
→INDEX→LOG pipeline writes concept files in one pass. (minutes of agent time per batch)

**Step 5 — Tier-gated quality pass.**
- T1: skip. - T2: run a provenance + light cross-source check.
- T3: run the figure-extraction, depth/distance + other conflict sweeps, and build the regression set
  (reuse the Optus `tasks/03,05,06,10`).

**Step 6 — Build the projection.** Say: *"build projection"*. PROJECTION_AGENT compiles
`projections/<bundle-slug>-master.md` — the single flat file that goes into a Gemini Gem,
Claude.ai Project, or ChatGPT Project. Check the Sync Status field in its header; regenerate
whenever the Log head advances past the Generated date.

**Step 6b — Building a bespoke interactive deliverable (only if you build one).** Some domains
earn a hand-authored client-facing artifact beyond the flat projection — an interactive HTML
decision tool, a scored dashboard, a slide generator — living under `deliverables/`, not
`projections/`. The moment you build one that embeds its own snapshot of concept data (a table of
scenarios, gates, definitions, whatever), **register a Deliverable Parity Contract in ontology.md
in the same session** (§Deliverable Parity Contracts). This is the one artifact type
PROJECTION_AGENT cannot regenerate for you — it's hand-edited, so it drifts silently the moment a
source concept is added or retired and nobody remembers to touch the HTML too. Registering the
contract at build time, not after drift is first noticed, is what lets ENRICHMENT_AGENT and
CONFORMANCE_AGENT catch it automatically from then on. (This step exists because it was skipped
once — see CHANGELOG.md [2.2.0].)

**Step 7 — Commit + tag a release.** Confirm `log.md` reflects this session (ingest pipeline
appends automatically; for direct edits run `"append log"` first). Then:
`git add -A && git commit && git tag v1`. See `playbook/BUNDLE_COMMIT_CHECKLIST.md`. Done.

After the first domain, steps 1–2 take under an hour; steps 4–6 are automated.

---

## 4. Source-type ingestion adapters (so Step 4 is repeatable)

| Source | How to ingest | Tier note |
|---|---|---|
| Clean text PDFs | `pdftotext -layout`; concepts from headings/clauses | figures need T3 render+read |
| Scanned PDFs | OCR first (`ocrmypdf`) then as above | flag low-confidence |
| Your notes / MD | ingest directly; type by topic | T1 default |
| Transcripts (calls, meetings) | chunk by topic; extract decisions/claims as concepts | great for capturing tacit insight |
| Spreadsheets/CSV | one concept per entity or a `Dataset` concept | keep numbers as literals |
| Web pages | fetch → summarise → `Reference` concept with URL | re-fetch on refresh |

---

## 5. Reuse — draw subsets for any LLM (the "projection" pattern)

Git repo = single source of truth. Every other tool consumes an **export**, never the live repo.

**Make a projection** = filter concepts by tag/type, concatenate (or zip) into one artifact:
- *Full bundle* → zip the repo.
- *Subset* (e.g. only `tag: hdd-depths`) → concat those concept bodies into one `projections/<name>.md`.

**Load into each environment:**

| Environment | How it consumes a projection |
|---|---|
| Claude.ai | Create a **Project**; upload the projection .md/zip as Project knowledge |
| ChatGPT | **Project** or custom GPT; upload projection as knowledge files |
| Gemini | **Gem** + Google Drive folder; point it at the projection |
| Grok | Paste projection into context / workspace files |
| Cowork / Cursor / Antigravity | Open the repo directly (local + git); no export needed |

Keep projections small and task-scoped — that's also what lets a **cheap model** serve reliably
(deterministic retrieval + the bundle's guardrails).

---

## 6. Update model — simple batch, no real-time integration

You generate insight continuously. Capture it cheaply:

1. **Drop** new material (a note, a transcript, a corrected value) into `inbox/`.
2. **Run** "ingest inbox/" in a local agent env. The pipeline merges additively, raises confidence
   on confirmation, flags contradictions with `<!-- CONFLICT -->` (never silent overwrite),
   supersedes+archives changed concepts, updates `index.md`/`log.md`.
3. **Re-project** any subsets that changed; re-upload to the cloud tools that use them.
4. **Commit.** Verify `log.md` has today's batch; if not, `"repair log"` first. `git commit` —
   the log + git history are your audit trail (`playbook/BUNDLE_COMMIT_CHECKLIST.md`).

For source REISSUES (a vendor updates a manual), use the **refresh playbook** pattern from the Optus
build: detect version from the document, re-extract changed parts only, re-run sweeps, diff values,
supersede, regenerate projections, extend the regression set. (T3 only.)

Cadence: weekly or whenever a batch accumulates. No daemons, no webhooks.

---

## 7. Cross-environment topology

```
        author / refresh (local agent envs)               consume (cloud LLMs)
   ┌───────────────────────────────────────┐      ┌───────────────────────────────┐
   │ Cowork  ·  Cursor  ·  Antigravity      │      │ Claude.ai Project            │
   │  - ingest inbox/                       │      │ Gemini Gem                   │
   │  - "build projection" (PROJECTION_AGENT)│      │ ChatGPT Project              │
   │  - run sweeps (T3)                     │      │                              │
   │  - commit to git                       │      │ Upload: projections/          │
   └───────────────────────────────────────┘      │   <bundle>-master.md ONLY    │
                        │   git push / pull                │   (one file = one upload)     │
                        └─────────────────────────────└─────────────────────────────┘
                               GitHub repo (per-domain bundle, tagged releases)
```

Principle: **author once locally, project outward.** Cloud tools never hold the master; they hold a compiled snapshot. When the bundle updates, rebuild the projection and swap the file in the cloud Project.

---

## 8. What to standardise ONCE (so domains stay cheap)

- The **kit** (invariant files) — frozen, versioned.
- The **intake questionnaire** — same 10 questions every domain.
- The **ingestion adapters** — same per source type.
- The **projection script** — filter-by-tag → one file.
- The **tier policy** — written down, so you don't over-verify T1 work.

Build these five once; every new domain reuses them. That is the difference between "a week per
domain" and "an afternoon per domain."

---

## 9. Your domains — suggested starting tiers

| Domain | Tier | Why |
|---|---|---|
| Accounting practice M&A | T2 | advisory; provenance matters, not figure-level safety |
| Mid-market customer engineering | T2 | advisory + some spec values |
| Civil HDD drilling | **T3** | depths/clearances → liability, like Optus |
| Civil construction | T3 | safety/spec/compliance |
| Industrial HVAC AI control | T3 | control-safety, setpoints, interlocks |
| Commercial HVAC O&M | T2/T3 | procedures + some safety-critical values |
| Grid-scale OT comms | **T3** | safety + regulatory + protocol exactness |
| Your interest groups | T1 | your knowledge, low ceremony |

---

*This is a method document, not the kit itself. The kit (AGENTS.MD etc.) already implements the
pipeline; this guide tells you how to deploy it across domains rapidly and reuse it everywhere.*

© 2026 Walter Adamson | BHP 20 years, Head IT Audit - IT Strategy - Corporate Planning - International Bus Development | 100+ AI workflow solutions delivered | linkedin.com/in/adamson | walter@outcomesnow.com
