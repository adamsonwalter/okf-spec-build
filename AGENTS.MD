# AGENTS.MD — OKF Bundle Orchestrator
# Open Knowledge Format v0.1 | GoogleCloudPlatform/knowledge-catalog
# Place this file at the root of any project where agents should maintain an OKF knowledge bundle.

---

## CORE vs OPTIONAL (read first)

This kit is split into a lean always-on **core** (this file + `ontology.md`,
`index.md`, `log.md` — the six standard OKF fields) and an opt-in **T3 cognitive
layer** in `optional/` (`LLM_WIKI.MD`, `FEEDBACK_LOOP.MD`, `ontology-ext.md`).

- **Default (T1/T2) bundles:** run on core only. Agents create concept files with
  `type`, `title`, `description`, `resource`, `tags`, `timestamp`. Conformance
  checks V1, V2, V4 only. Do NOT emit `confidence`, `memory_tier`, supersession,
  or contradiction records.
- **T3 (liability-grade) bundles only:** also load the three files from
  `optional/`. The enrichment/link/consumption/conformance agents then activate
  their memory-tier, confidence, supersession, and decay behaviours, and V3/V5–V8
  apply (see `optional/ontology-ext.md`).

If the `optional/` files are not present in the bundle root, treat every
optional-layer instruction below (confidence scoring, memory tiers, supersession,
contradiction/decay handling) as inert.

See `docs/OKF_DIVERGENCE.md` for how this dialect relates to vanilla OKF v0.1.

---

## CONFORMANCE REFERENCE

OKF v0.1 hard rules (§9). A bundle is conformant when:
1. Every non-reserved `.md` file has a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field. THIS IS THE ONLY REQUIRED FIELD.
3. `index.md` files follow §6 format: sections + bullet lists, no frontmatter — EXCEPT the
   bundle-root `index.md`, which MAY carry a single fenced `okf_version` frontmatter block
   (§11). That is the only place frontmatter is permitted in any `index.md`.
4. `log.md` files follow §7 format: ISO 8601 date headings, newest-first, bold action verbs.

Reserved filenames (must never be used as concept documents): `index.md`, `log.md`

---

## ORCHESTRATOR

```
AGENT: OKF_ORCHESTRATOR
ROLE: Route incoming work to the correct specialist agent. Never write files directly.

TRIGGER: Any of the following inputs:
  - Raw text, research notes, documents, or structured data to be ingested
  - A request to update, query, or traverse the knowledge bundle
  - A request to validate or audit the bundle for conformance

ROUTING TABLE:
  Input is a whole/large source document (PDF, report, multi-page transcript,
  or an explicit re-ingestion of a previously-ingested source) — i.e. it has,
  or plausibly has, its own named structural units (headings, numbered/
  lettered boxes, tables, figures, appendices, case studies) that a partial
  read could miss                                       →  dispatch ENRICHMENT_AGENT
                                                            in SOURCE-DOCUMENT MODE
                                                            (STATE: INVENTORY and
                                                            GATE_5-COVERAGE are
                                                            mandatory — see AGENT 1)
  Input is a short note, single fact, correction, or                        →  dispatch ENRICHMENT_AGENT
  fragment with no internal structure worth inventorying                     in NOTE MODE (STATE:
                                                                               INVENTORY skipped)
  Input is a query or read request                      →  dispatch CONSUMPTION_AGENT
  Input is "validate" or "audit"                        →  dispatch CONFORMANCE_AGENT
  Input is "rebuild index" or "reindex"                 →  dispatch INDEX_AGENT (standalone)
  Input is "rebuild log" or "repair log"                →  dispatch LOG_AGENT (standalone)
  Input is "commit", "push", "save", "append log", or any request to finalize changes after a
  direct edit to bundle infrastructure (AGENTS.MD, README.md, CHANGELOG.md,
  ontology.md, playbook/, docs/, optional/, projections/, ontology-mapper/,
  .gitignore, or any non-ingest file write)             →  dispatch LOG_AGENT first
                                                          (standalone — build manifest
                                                          from the files changed in
                                                          this session), THEN git
  Input is "build projection", "export", or "update projection"
                                                        →  dispatch PROJECTION_AGENT
  Input describes a new hand-authored interactive deliverable that embeds a
  snapshot of concept data, or says "register deliverable parity"           →  dispatch ONTOLOGY_AGENT
                                                                                (add a Deliverable
                                                                                Parity Contract row —
                                                                                see ontology.md
                                                                                §Deliverable Parity
                                                                                Contracts)

SEQUENCING RULE:
  ENRICHMENT_AGENT always runs in this fixed order:
    1. ENRICHMENT_AGENT  (parse, classify, write concept files)
    2. LINK_AGENT        (inject cross-links after all concept files exist)
    3. INDEX_AGENT       (rebuild affected index.md files)
    4. LOG_AGENT         (append mutation record to log.md)

  Agents 2–4 receive the MUTATION_MANIFEST output from step 1.
  Do not run INDEX_AGENT or LOG_AGENT before ENRICHMENT_AGENT completes.

  KIT_MAINTENANCE path (direct edits — no ENRICHMENT, no new concepts):
    1. Apply the infrastructure edits
    2. INDEX_AGENT (only if concept files or directory listings changed)
    3. LOG_AGENT (mandatory — append before git commit)
    4. git commit / push (human or agent — only after step 3)

  LOG_AGENT is NOT optional on the kit-maintenance path. Commits that change bundle
  files but leave log.md untouched since the last ## date block are a protocol violation.
  Never replace log.md body with a placeholder comment — historical entries are append-only.
```

---

## AGENT 1 — ENRICHMENT_AGENT

```
AGENT: ENRICHMENT_AGENT
ROLE: Parse input, extract concepts, write or update concept .md files.
OUTPUT: MUTATION_MANIFEST (list of files created/updated, with paths)

─── STATE: INGEST ───────────────────────────────────────────────────────────────
ACTION:
  Determine INGEST_MODE before doing anything else:
    SOURCE-DOCUMENT MODE — the input is a whole document with its own internal
      structure (a PDF, report, multi-page transcript, or an explicit re-ingestion
      of a previously-ingested source).
    NOTE MODE — the input is a short note, single fact, correction, or fragment
      with no internal structure worth inventorying.
  When in doubt, prefer SOURCE-DOCUMENT MODE — the cost of an unnecessary inventory
  pass is small; the cost of silently skipping one on a real document is a
  completeness gap that no later CHECK will catch on its own (see GATE_5-COVERAGE).

  Parse the incoming input.
  Extract discrete concepts and named entities.
  For each concept, determine: name, type, description, relationships.

GATE_1: Were one or more discrete concepts successfully extracted?
  YES → SOURCE-DOCUMENT MODE: proceed to INVENTORY.
        NOTE MODE: proceed directly to MAP.
  NO  → HALT. Respond: "No extractable concepts found. Provide structured input."

─── STATE: INVENTORY (SOURCE-DOCUMENT MODE ONLY — skipped entirely in NOTE MODE) ─
ACTION:
  This state exists because a single read-through, no matter how thorough, is
  liable to notice what looks substantively interesting and silently deprioritise
  what looks repetitive or formulaic — even when the latter is real, required
  content (e.g. a recurring "Questions to ask" box that appears identically several
  times in the source). Reading comprehension and completeness are different
  skills; this state is a mechanical substitute for the second one.

  Before writing or updating a single concept file, walk the ENTIRE source and
  enumerate every named structural unit it contains — every heading, numbered or
  lettered box/callout, table, figure, appendix, case study, boxed quote, and any
  other visually or structurally distinct unit the source itself labels or sets
  apart. Enumerate by walking the document's own structure (its table of contents,
  numbering, headings) — NOT by recalling what stood out while reading. Do not
  filter this list by perceived importance; that judgement is applied later, in
  MUTATE_CREATE/MUTATE_UPDATE, not here.

  Load the existing `type: Coverage Ledger` concept for this source if one exists
  (re-ingestion), or create one (first ingestion) — conventionally at
  `errata/<source-slug>-coverage-ledger.md` or `coverage/<source-slug>.md`. Write or
  confirm one row per enumerated unit with a Status of Captured / Partial / N/A /
  "Not yet checked" (new units default to "Not yet checked").

  Register a Source Coverage Contract for this source in ontology.md §Source
  Coverage Contracts if one is not already registered (first ingestion only).

GATE_1-INVENTORY: Was the enumeration built by mechanically walking the source's
  own structure (contents/numbering/headings), not by recalling what stood out?
  YES → proceed to MAP. The inventory (not unaided re-reading judgement) now
        drives which concepts MUTATE_CREATE/MUTATE_UPDATE must produce.
  NO  → HALT. Redo the inventory pass structurally — list every Box N, Table N,
        Figure N, page-anchored recurring callout, and appendix letter the source
        itself labels, before extracting or writing a single concept.

─── STATE: MAP ──────────────────────────────────────────────────────────────────
ACTION:
  Scan the bundle directory tree for all existing .md files.
  Build BUNDLE_MANIFEST: a flat list of all .md file paths (excluding index.md and log.md).
  Load the nearest index.md as a human-readable directory hint (optional, not authoritative).
  For each extracted concept, check if a matching .md file exists in BUNDLE_MANIFEST.

GATE_2: Can the bundle directory be scanned?
  YES → for each concept:
          exists in BUNDLE_MANIFEST  →  route to MUTATE_UPDATE
          absent from BUNDLE_MANIFEST →  route to MUTATE_CREATE
  NO  → HALT. Report filesystem access error.

─── STATE: MUTATE_CREATE ────────────────────────────────────────────────────────
ACTION:
  For each novel concept, generate a new .md file.

  FILE PATH RULE:
    Place the file in the most semantically appropriate subdirectory.
    Use kebab-case filenames: `customer-orders.md`, `ingestion-playbook.md`.
    Create subdirectories as needed.

  REQUIRED FRONTMATTER (minimum for OKF conformance):
    ---
    type: <descriptive type string>   # REQUIRED. e.g. "Concept", "Playbook", "API Endpoint"
    ---

  RECOMMENDED FRONTMATTER (include all when inferable):
    ---
    type: <type>
    title: <human-readable display name>
    description: <single sentence summary>
    resource: <URI if concept maps to a real asset, omit otherwise>
    tags: [<tag1>, <tag2>]
    timestamp: <ISO 8601 datetime of now>
    ---

  BODY RULE:
    Use structural markdown: headings, lists, tables, fenced code blocks.
    Include a `# Schema` section if the concept has columns or fields.
    Include a `# Examples` section if usage examples are available.
    Leave a `# Citations` section placeholder if sources exist.
    Do NOT yet inject cross-links — that is LINK_AGENT's job.

GATE_3: Does every new file have a parseable YAML frontmatter block with a non-empty `type` field?
  YES → add file path to MUTATION_MANIFEST under "created". Proceed.
  NO  → HALT. Inject missing `type` field. Re-evaluate GATE_3.

GATE_3-PARITY: Does this new file's path fall inside the `Source scope` of any registered
  Deliverable Parity Contract in ontology.md (§Deliverable Parity Contracts)?
  NO  → not applicable, proceed.
  YES → this ENRICHMENT pass is NOT complete until a matching record is added to the named
        `Deliverable file`, using the contract's `Identity key`, IN THE SAME BATCH — do not defer
        this to a later session or to PROJECTION_AGENT (which never touches `deliverables/`).
        Add the deliverable file path to MUTATION_MANIFEST under "deliverable_synced". If the
        deliverable cannot be safely edited in this pass (e.g. its structure is unfamiliar),
        HALT and report the specific contract that is now unsatisfied — do not silently proceed
        leaving the deliverable stale.

─── STATE: MUTATE_UPDATE ────────────────────────────────────────────────────────
ACTION:
  Load the existing .md file.
  Identify sections to add, revise, or extend.
  NEVER overwrite: existing frontmatter fields not in the incoming data, existing body sections
  not contradicted by new data, or existing cross-links.
  Merge new content additively.

  CONFLICT RULE:
    If incoming data contradicts existing content:
      Compare timestamps. Favor the entry with the more recent `timestamp`.
      If timestamps are equal or absent, flag the conflict inline with:
        <!-- CONFLICT: [old value] vs [new value] — resolve manually -->
      Do not silently discard either version.

  UPDATE the `timestamp` frontmatter field to the current ISO 8601 datetime.

GATE_4: Is the updated file parseable with a valid `type` field intact?
  YES → add file path to MUTATION_MANIFEST under "updated". Proceed.
  NO  → HALT. Restore from pre-mutation state. Report error.

GATE_4-PARITY: Same check as GATE_3-PARITY, in reverse — if this update MOVES a file out of a
  contracted `Source scope` (archived to `archive/`, retitled, deleted), the matching record in
  the `Deliverable file` must be removed or annotated stale in the SAME batch.

GATE_5-COVERAGE (SOURCE-DOCUMENT MODE ONLY — not applicable in NOTE MODE): Once all
  MUTATE_CREATE/MUTATE_UPDATE work for this batch is done, does every row in this
  source's Coverage Ledger (built in STATE: INVENTORY) show Status "Captured",
  "Partial", or "N/A" — none left as "Not yet checked"?
  YES → this ENRICHMENT pass may hand MUTATION_MANIFEST to LINK_AGENT.
  NO  → HALT. Do NOT proceed to LINK_AGENT/INDEX_AGENT/LOG_AGENT. List the
        unresolved rows by name and return to MUTATE_CREATE/MUTATE_UPDATE for
        those specific units. "I read the whole source" is not evidence of
        completeness — an unresolved row is. An ingestion in SOURCE-DOCUMENT MODE
        is not finished while GATE_5-COVERAGE fails, no matter how much of the
        source was read or how many concepts were written.
```

---

## AGENT 2 — LINK_AGENT

```
AGENT: LINK_AGENT
ROLE: Inject bidirectional cross-links between related concept files.
INPUT: MUTATION_MANIFEST from ENRICHMENT_AGENT
PRECONDITION: All files in MUTATION_MANIFEST must already exist on disk before this agent runs.

─── STATE: RESOLVE ──────────────────────────────────────────────────────────────
ACTION:
  Rebuild BUNDLE_MANIFEST by scanning the directory tree (post-ENRICHMENT_AGENT).
  For each file in MUTATION_MANIFEST, identify semantically related concepts
  by scanning body content and frontmatter tags of other bundle files.

─── STATE: LINK ─────────────────────────────────────────────────────────────────
ACTION:
  For each identified relationship between concept A and concept B:

  LINK FORMAT — use bundle-relative paths (preferred):
    [Title of B](/path/to/b.md)
  LINK FORMAT — use relative paths only when both files are in same directory:
    [Title of B](./b.md)

  Inject the link into concept A's body at the appropriate contextual location
  (e.g., within a "Related" section, or inline in a sentence that references B).
  Then inject the reciprocal link into concept B pointing back to A.

GATE_5: For every injected link, does the target file path exist in BUNDLE_MANIFEST?
  YES → proceed to LOG_AGENT.
  NO  → HALT. Remove the orphaned link. Do NOT add links to files that do not
        exist on disk. Log the pruned edge in MUTATION_MANIFEST under "pruned_links".

  NOTE: Validate links against BUNDLE_MANIFEST (actual files on disk),
        NOT against index.md. index.md may be stale or absent.
```

---

## AGENT 3 — INDEX_AGENT

```
AGENT: INDEX_AGENT
ROLE: Generate or update index.md files to reflect current bundle contents.
INPUT: MUTATION_MANIFEST from ENRICHMENT_AGENT

CRITICAL INVARIANT: index.md files MUST NOT contain YAML frontmatter.
  Exception: the bundle-root index.md MAY contain a single frontmatter key:
    okf_version: "0.1"
  This is the only permitted frontmatter in any index.md.

─── STATE: SCOPE ────────────────────────────────────────────────────────────────
ACTION:
  For each directory that contains a file in MUTATION_MANIFEST:
    Identify all .md files in that directory (excluding index.md and log.md).
    Group them by their `type` frontmatter field to form index sections.

─── STATE: WRITE_INDEX ──────────────────────────────────────────────────────────
ACTION:
  Write (or overwrite) index.md in each affected directory using this exact format:

  ═══ BUNDLE ROOT index.md FORMAT ═══════════════════════════════════════════════
  ---
  okf_version: "0.1"
  ---

  # <Directory or Bundle Name>

  <Optional one-line description of what this directory contains.>

  ## <Type Group or Section Name>

  * [<title>](<relative-path>.md) — <description from frontmatter>
  * [<title>](<relative-path>.md) — <description from frontmatter>

  ## Subdirectories

  * [<subdir-name>](<subdir>/) — <brief description>
  ═══════════════════════════════════════════════════════════════════════════════

  ═══ SUBDIRECTORY index.md FORMAT ═══════════════════════════════════════════════
  # <Subdirectory Name>

  ## <Type Group>

  * [<title>](<filename>.md) — <description>
  ═══════════════════════════════════════════════════════════════════════════════

  RULES:
  - Title comes from `title` frontmatter field; fall back to filename if absent.
  - Description comes from `description` frontmatter field; omit dash if absent.
  - Sort entries alphabetically within each section.
  - Subdirectory entries link to the subdirectory path with trailing slash.
  - Do NOT include log.md or index.md as entries.

GATE_6: Does every produced index.md have NO frontmatter block (except okf_version at root)?
  YES → proceed to LOG_AGENT.
  NO  → HALT. Strip the frontmatter block. Re-evaluate GATE_6.
```

---

## AGENT 4 — LOG_AGENT

```
AGENT: LOG_AGENT
ROLE: Append a dated mutation record to log.md at the bundle root.
INPUT: MUTATION_MANIFEST from ENRICHMENT_AGENT + pruned_links from LINK_AGENT;
       OR a KIT_MANIFEST (explicit list of infrastructure paths changed this session,
       built from git diff or the agent's own edit list) on the kit-maintenance path

─── STATE: WRITE_LOG ────────────────────────────────────────────────────────────
ACTION:
  Open (or create) log.md at the bundle root.
  Prepend a new date block at the TOP of the file (newest entries first).

  ═══ log.md FORMAT ══════════════════════════════════════════════════════════════
  # Bundle Update Log

  ## YYYY-MM-DD

  * **Creation**: [<title>](<bundle-relative-path>.md) — <one-line reason>
  * **Update**: [<title>](<bundle-relative-path>.md) — <what changed>
  * **Kit**: [<path>](<bundle-relative-path>) — <what changed> (infrastructure: AGENTS.MD,
    README, CHANGELOG, playbook/, docs/, optional/, projections/, .gitignore, etc.)
  * **Restructure**: [<path>](<new-path>) — <move/rename reason> (use when a file changes
    directory, e.g. root → optional/)
  * **Link**: [<concept A>] ↔ [<concept B>] — relationship injected
  * **Pruned**: [<concept A>] → [<dead-target>] — target did not exist
  * **Deprecation**: [<title>](<path>.md) — <reason> (use when a concept is retired)
  * **Gap**: [<stub or path>](<path>) — <known missing piece recorded>
  * **Initialization**: <one-line bundle bootstrap event> (first install only)

  ═══════════════════════════════════════════════════════════════════════════════

  RULES:
  - Date heading MUST use ISO 8601 YYYY-MM-DD format.
  - Use today's date (UTC).
  - If a date block for today already exists, append new entries under it.
  - Do NOT create a new date block for the same date.
  - Bold action word is required (see list above).
  - Each entry links to the affected file using a bundle-relative path where applicable.
  - Omit categories with zero entries (do not write "* **Pruned**: none").
  - NEVER delete or replace prior date blocks. NEVER substitute the file body with a
    placeholder such as "populated by LOG_AGENT". Append only.
  - On kit-maintenance commits: one **Kit** or **Restructure** line per infrastructure
    file or directory touched, summarising the change in one sentence.

GATE_7: Is log.md valid — date heading in ISO 8601, entries newest-first, no frontmatter?
  YES → HALT with SUCCESS. Report summary to orchestrator.
  NO  → HALT. Repair the malformed block. Re-evaluate GATE_7.
```

---

## AGENT 5 — CONSUMPTION_AGENT

```
AGENT: CONSUMPTION_AGENT
ROLE: Read and traverse the bundle to answer queries. Read-only. Never writes files.

─── STATE: ORIENT ───────────────────────────────────────────────────────────────
ACTION:
  Load bundle-root index.md for progressive disclosure (directory overview).
  If index.md is absent, scan the directory tree directly to build a working map.

─── STATE: RETRIEVE ─────────────────────────────────────────────────────────────
ACTION:
  Parse the query to identify target concepts, types, or relationships.
  Locate relevant .md files via index.md links or direct directory scan.
  Follow cross-links to retrieve related concepts (graph traversal).
  Tolerate broken links — a link whose target is absent is not an error; skip it.

─── STATE: RESPOND ──────────────────────────────────────────────────────────────
ACTION:
  Synthesize findings from concept bodies.
  Cite sources using the concept's `resource` frontmatter URI when present.
  Surface the `timestamp` of each concept used to indicate data freshness.
  Never modify files.
```

---

## AGENT 6 — CONFORMANCE_AGENT

```
AGENT: CONFORMANCE_AGENT
ROLE: Audit the bundle for OKF v0.1 compliance. Produces a report; does not auto-repair.

─── STATE: RUN THE CHECKER FIRST (mandatory) ────────────────────────────────────
ACTION:
  Run the checker before reading anything yourself:

      python3 scripts/okf_check.py .

  Exit 0 = no ERROR-severity failures. Exit 1 = at least one. Exit 2 = the bundle
  could not be read. `--json` gives machine-readable findings.

  Every check below is mechanically decidable — frontmatter parses, dates sort,
  links resolve, keys diff, a Status column has no "Not yet checked" — so the
  script decides them, not you. Report its output as the result.

  The script also runs V1-V12, which cover more than CHECK_1..CHECK_9:
    V9   every concept meets its type's declared Required Fields / Sections
    V10  every relationship edge target resolves to a concept
    V11  no relationship edge points into an archived or superseded concept
    V12  a concept's confidence sits inside the band its tags declare (WARNING)

  For the relationship graph on its own — edge counts by type, or JSON for an
  application to traverse:

      python3 scripts/okf_graph.py . --json

  To rebuild projections (STATE I7), run the kit's builder rather than writing a
  per-bundle script — that duplication is why bundles drifted from the kit:

      python3 <kit>/scripts/okf_project.py .

  For how the kit and its bundles fit together — what to pull, when, and what
  breaks if you do not — see docs/OPERATING.md.

  Before changing a severity, relaxing a guard or adding a rule, read
  docs/DECISIONS.md — several of these were settled against measured evidence and
  should not be re-litigated from first principles.

  DO NOT hand-audit these and report PASS. A check an agent performed and a check
  an agent skipped look identical afterwards, which is the whole reason the script
  exists. If the script is missing or errors, say so and report the audit as NOT
  RUN — never as passing.

  Your judgment is still required for what code cannot settle, and only that:
    - whether a `contested` claim names the *right* open question (V-T3b-style rules)
    - whether a Coverage Ledger still matches the source document — the script reads
      the Status column only, and cannot re-derive the ledger (see CHECK_9)
    - whether a CHECK_7 SKIP hides a real record-level mismatch inside a
      hand-authored deliverable whose format the kit does not specify
    - whether a V12 warning means the concept is mis-graded or the band is
      wrong. Do not "fix" a warning by moving a concept's confidence to fit a
      band; a band that half the corpus breaches is the thing that is wrong,
      and re-grading to satisfy it hides material rather than correcting it

─── STATE: SCAN ─────────────────────────────────────────────────────────────────
ACTION:
  Walk every .md file in the bundle tree.
  Classify each file: concept document | index.md | log.md | unknown.

─── STATE: AUDIT ────────────────────────────────────────────────────────────────
CHECK_1  Every non-reserved .md has parseable YAML frontmatter.
CHECK_2  Every frontmatter block has a non-empty `type` field.
CHECK_3  No index.md contains a frontmatter block (except okf_version at root).
CHECK_4  log.md date headings are ISO 8601 YYYY-MM-DD, newest-first.
CHECK_5  All internal markdown links resolve to files that exist on disk.
CHECK_6  No .md file is named index.md or log.md and used as a concept document.
CHECK_7  For EVERY row in ontology.md §Deliverable Parity Contracts: the files matching
         `Source scope` and the records in `Deliverable file` (keyed on `Identity key`) are in
         1:1 correspondence. Do not just compare counts — diff the actual keys and NAME any
         source file with no matching record, and any deliverable record with no matching
         source file. Skip CHECK_7 entirely (not a fail) if the contracts table has no rows.
CHECK_8  log.md body is NOT placeholder-only (no sole line like "populated by LOG_AGENT"
         with zero ## YYYY-MM-DD date blocks). FAIL if placeholder-only and any concept file,
         kit infrastructure file, or CHANGELOG.md version entry post-dates initialization —
         the log was not maintained. Repair: run LOG_AGENT standalone ("repair log").
CHECK_9  For EVERY row in ontology.md §Source Coverage Contracts: open the named
         `Coverage ledger file` (a `type: Coverage Ledger` concept) and NAME any row whose
         Status is not `Captured` or `Not applicable` — these are live gaps between the
         source document and the bundle. This is a DIFFERENT failure mode from CHECK_7: a
         CHECK_7 fail means a hand-authored deliverable drifted from concepts that already
         exist in the bundle; a CHECK_9 fail means a unit of the *original source document*
         was never turned into a concept in the first place, so there is nothing yet for a
         deliverable to drift from. Skip CHECK_9 entirely (not a fail) if the contracts table
         has no rows. CONFORMANCE_AGENT checks the ledger's Status column only — it does NOT
         re-derive the ledger from the source document itself; that re-verification is
         ENRICHMENT_AGENT's responsibility (STATE: INVENTORY) when a source is first, or re-,
         ingested. A CHECK_9 fail should not normally occur if STATE: INVENTORY /
         GATE_5-COVERAGE were followed — it exists as a safety net for bundles predating this
         mechanism, or a session that skipped SOURCE-DOCUMENT MODE.

─── STATE: REPORT ───────────────────────────────────────────────────────────────
ACTION:
  Output a conformance report:

  OKF v0.1 CONFORMANCE REPORT — <bundle name> — <date>
  ─────────────────────────────────────────────────────
  PASS  CHECK_1  All concept files have parseable frontmatter.
  FAIL  CHECK_3  /subdirectory/index.md contains frontmatter block (line 1–3).
  WARN  CHECK_5  /concepts/foo.md links to /concepts/bar.md which does not exist.
  FAIL  CHECK_7  Contract `scenario-decision-map`: scenarios/scenario-h-*.md and
                 scenarios/scenario-i-*.md have no matching record in
                 deliverables/app-1-7-trigger-test-decision-map.html (missing ids: H, I).
  FAIL  CHECK_8  log.md is placeholder-only — no ## date blocks despite kit mutations.
  FAIL  CHECK_9  Contract `<slug>-coverage`: coverage/<slug>.md has 3 rows still "Not yet
                 checked" (Box 4, Box 8, "Over the horizon") — source units never captured.
  ...
  ─────────────────────────────────────────────────────
  STATUS: NON-CONFORMANT — 1 failure, 1 warning
  Run ENRICHMENT_AGENT or INDEX_AGENT to repair flagged files. A CHECK_7 failure is repaired by
  hand-editing the named `Deliverable file` to add/remove the named record(s) — PROJECTION_AGENT
  cannot fix this; it never writes to `deliverables/`. A CHECK_8 failure is repaired by
  LOG_AGENT ("repair log") backfilling from git history or CHANGELOG.md, then appending going
  forward. A CHECK_9 failure is repaired by re-dispatching ENRICHMENT_AGENT in SOURCE-DOCUMENT
  MODE against the still-unresolved rows named in the report — MUTATE_CREATE/MUTATE_UPDATE for
  those specific units, then re-run GATE_5-COVERAGE.
```

---

## AGENT 7 — PROJECTION_AGENT

```
AGENT: PROJECTION_AGENT
ROLE: Compile the structured bundle into flat Markdown projection files for upload to cloud LLM
      environments (Gemini Gems, Claude.ai Projects, ChatGPT Projects, etc.).
      Read-only over all concept files. Writes only to projections/.

TRIGGER PHRASES (any of):
  "build projection"          → full master projection (all concepts)
  "build projection [tag]"    → tag-scoped slice (concepts matching one tag)
  "update projection"         → rebuild existing projection from current bundle state
  "export"                    → synonym for build projection

PRECONDITION: At least one concept file must exist. Run after ENRICHMENT_AGENT completes
  its full cycle (ENRICHMENT → LINK → INDEX → LOG) so the projection reflects committed state.

─── STATE: SCAN ─────────────────────────────────────────────────────────────────
ACTION:
  1. Open log.md — read the date of the newest ## YYYY-MM-DD heading (LOG_HEAD).
  2. Walk every .md file in the bundle tree.

  EXCLUDE from projection (these files must NEVER appear in any projection):
    - All index.md files (navigation — relative links break outside the repo)
    - log.md (mutation history — not domain knowledge)
    - All ALL_CAPS .md files: AGENTS.MD and any *_WIKI.MD, *_LOOP.MD etc. (agent instructions)
    - Files in stubs/ (type: Stub — incomplete placeholders)
    - Files in archive/ (superseded — not current knowledge)
    - Files in projections/ (derived artifacts — never re-project a projection)

  INCLUDE in projection:
    - ontology.md (always first, regardless of any tag filter)
    - All remaining concept .md files

  For a TAG-SCOPED slice: apply tag filter AFTER the above exclusions.
    Keep a concept if its `tags` frontmatter list includes the requested tag.
    Always include ontology.md regardless of tag filter.

─── STATE: COMPILE ──────────────────────────────────────────────────────────────
ACTION:
  Assemble the projection in this exact order:

  ┌─ 1. SYNC HEADER (plain Markdown, NO YAML frontmatter) ─────────────────────┐
  │                                                                               │
  │  # <Bundle Title> — Knowledge Projection                                     │
  │                                                                               │
  │  | Field            | Value                                                 | │
  │  |---|---|                                                                   │
  │  | Generated        | <ISO 8601 datetime>                                   | │
  │  | Scope            | master (all concepts) OR tag: <tag>                  | │
  │  | Concepts included| <count of concept files, excluding ontology>          | │
  │  | Log head         | <LOG_HEAD date>                                       | │
  │  | Sync status      | Current if Generated >= Log head; STALE if not       | │
  │                                                                               │
  │  > **UPLOAD INSTRUCTIONS**: Upload THIS FILE ONLY to your cloud LLM Project  │
  │  > (Gemini Gem, Claude.ai Project, ChatGPT Project). Do NOT upload index.md, │
  │  > log.md, or individual concept files alongside it — this file already      │
  │  > contains the ontology and all concepts.                                   │
  │  > To update: regenerate this file and replace the existing upload.          │
  │  > ONE FILE IN = ONE FILE OUT.                                               │
  └────────────────────────────────────────────────────────────────────────────┘

  ┌─ 2. §0 ONTOLOGY ────────────────────────────────────────────────────────────┐
  │  Heading: ## §0 Ontology                                                     │
  │  Body: full content of ontology.md with its YAML frontmatter STRIPPED.      │
  │  Purpose: the consuming LLM learns the type/tag vocabulary before reading    │
  │  any concept, so it can correctly interpret type and tags fields.            │
  └────────────────────────────────────────────────────────────────────────────┘

  ┌─ 3. CONCEPT SECTIONS (one per included concept file) ──────────────────────┐
  │  Sort: alphabetically by title (from `title` frontmatter, fallback filename)│
  │                                                                               │
  │  For each concept:                                                            │
  │    ## <title>                                                                 │
  │    *Type: <type> | Tags: <tags joined by ", "> | Updated: <timestamp>*       │
  │    <blank line>                                                               │
  │    <full body of concept file — YAML frontmatter block STRIPPED>             │
  │    <horizontal rule --- between concepts>                                     │
  └────────────────────────────────────────────────────────────────────────────┘

FRONTMATTER STRIP RULE:
  Remove the opening --- line, all lines up to and including the closing --- line.
  Retain everything after the closing ---. Do not alter body content.

─── STATE: WRITE ────────────────────────────────────────────────────────────────
ACTION:
  Determine output path:
    Master projection →  projections/<bundle-slug>-master.md
    Tag slice         →  projections/by-tag/<tag>.md
  Where <bundle-slug> = kebab-case version of the bundle root title.

  Create projections/ and projections/by-tag/ directories if absent.
  OVERWRITE any existing file at the output path without prompting.
  Projection files are derived artifacts; the structured concept files are the source of truth.

GATE_8: Does the output file exist at the correct path and contain the sync header?
  YES → HALT with SUCCESS. Report: file path, concept count, generated datetime, log head.
  NO  → HALT with ERROR. Report what prevented completion.
```

---

## BUNDLE INVARIANTS

These rules apply at all times and override any agent instruction:

1. **`type` is sacred.** Never write or update a concept .md without a `type` field.
2. **`index.md` has no frontmatter** (except `okf_version: "0.1"` at bundle root only).
3. **`log.md` has no frontmatter.** Ever.
4. **Link targets must exist on disk** before a link is injected. Never pre-link to planned files.
5. **Conflict annotation, never silent overwrite.** Use `<!-- CONFLICT -->` comments.
6. **LINK_AGENT runs after all concept files are written** in the current batch.
7. **INDEX_AGENT runs after LINK_AGENT** so index entries reflect final file state.
8. **LOG_AGENT runs last** in the enrichment cycle. The log is a record of what happened, not a plan.
9. **LOG_AGENT runs before every commit** — including kit-maintenance edits that bypass
   ENRICHMENT_AGENT. Never commit bundle file changes without appending to log.md first.
   Never wipe log.md to a placeholder.
10. **A deliverable with a registered Parity Contract is updated in the SAME batch** as the concept
   mutation that would otherwise break parity — never deferred to "later" or assumed covered by
   PROJECTION_AGENT (it only writes `projections/`, never `deliverables/`). This is unconditional:
   it applies to every create/retire event inside the contract's `Source scope`, not just changes
   that "seem significant enough" to warrant it.
11. **A SOURCE-DOCUMENT MODE ingestion is not complete while its Coverage Ledger has any row
   not marked Captured/Partial/N/A.** Completeness is verified against a mechanically-built
   enumeration (STATE: INVENTORY), never asserted on the strength of having read the whole
   source. NOTE MODE ingestions (a short note, single fact, or correction) are exempt — this
   invariant only binds once STATE: INVENTORY has run. See GATE_5-COVERAGE.

---

## BUNDLE COMMIT CHECKLIST

> **Renamed scope:** This checklist applies to **every OKF bundle** — domain repos generated
> from this kit, not only the okf-spec-build repo. Printable copy:
> `playbook/BUNDLE_COMMIT_CHECKLIST.md`.

Any agent or human mutating bundle files MUST follow one of these paths before `git commit` or
`git push`:

### Path A — Ingest session (ENRICHMENT pipeline)

```
ingest → ENRICHMENT → LINK → INDEX → LOG → commit
```

LOG_AGENT is step 4 of every ingest. Do not commit until `log.md` shows today's batch.
If ingest completed but log did not update, run LOG_AGENT standalone (`repair log`) before commit.

### Path B — Direct edits (bypass ENRICHMENT)

Ontology edits, hand-edited concepts, playbooks, deliverables, parity contracts, infrastructure:

1. List every file changed this session (or run `git diff --name-only`).
2. Dispatch **LOG_AGENT** — append **Kit** / **Update** / **Restructure** / **Creation** lines
   under today's `## YYYY-MM-DD` block in `log.md`.
3. If concept files or directories changed, run **INDEX_AGENT** on affected dirs.
4. `git add -A && git commit` — log.md MUST be in the commit.
5. `git push` (if requested).

Orchestrator routes **"commit"**, **"push"**, **"save"** → LOG_AGENT first (Path B).

### Path C — New domain repo cloned from this kit

Replace `log.md` with `templates/log-domain-init.md` (domain name + date filled in).
Do not inherit the kit repo's release history in a domain bundle's log.

Skipping LOG_AGENT before commit is what caused log.md to go empty after kit v2.0.0 while
CHANGELOG.md continued to be updated. CHANGELOG tracks kit *releases*; log.md tracks every
*mutation* in this bundle.

---

## MINIMAL BUNDLE STRUCTURE (reference)

```
<bundle-root>/
├── AGENTS.MD               ← this file (agent instructions — never indexed)
├── index.md                ← no frontmatter; navigation index (never uploaded to cloud Projects)
├── log.md                  ← no frontmatter; ISO 8601 date blocks, newest-first (never uploaded)
├── ontology.md             ← type/tag registry; embedded §0 in every projection
├── <concept>.md            ← frontmatter with type; markdown body
├── <subdirectory>/
│   ├── index.md            ← no frontmatter; subdirectory listing (never uploaded)
│   └── <concept>.md
└── projections/            ← DERIVED ARTIFACTS — flat exports for cloud LLM Projects
    ├── <bundle-slug>-master.md   ← full bundle: ontology §0 + all concepts (ONE FILE TO UPLOAD)
    └── by-tag/
        └── <tag>.md        ← scoped slice: ontology §0 + concepts matching one tag
```

**Two deployment modes from one build:**

| Mode | Where | What to use | What NOT to upload |
|---|---|---|---|
| IDE / Claude Cowork | Local repo, Cursor, Antigravity | The full structured folder | — |
| Cloud LLM Project | Gemini Gem, Claude.ai, ChatGPT | `projections/<bundle>-master.md` only | index.md, log.md, individual concept files, AGENTS.MD |

---

## QUICK-START FOR NEW BUNDLE

When cloning this kit into a new domain repo (or starting from scratch):

0. Replace `log.md` with `templates/log-domain-init.md` — fill in today's date and the
   domain name. Do not keep the kit's own release history in a domain bundle.
1. OKF_ORCHESTRATOR receives input.
1b. IF the input is a whole source document (not a short note): ENRICHMENT_AGENT
    runs STATE: INVENTORY first — a mechanical, structure-driven enumeration of
    every named unit in the source (Box/Table/Figure/callout/appendix/case),
    written into a `type: Coverage Ledger` concept — BEFORE extracting a single
    concept. This is what GATE_5-COVERAGE checks against before the batch can
    complete; see §Source Coverage Contracts in ontology.md.
2. ENRICHMENT_AGENT extracts concepts → writes concept .md files.
3. LINK_AGENT scans all newly written files → injects links.
4. INDEX_AGENT generates root index.md (with `okf_version: "0.1"`) and any subdirectory index.md files.
5. LOG_AGENT creates log.md with a `## YYYY-MM-DD` block recording all creations.
6. PROJECTION_AGENT compiles `projections/<bundle-slug>-master.md` — the single file to upload
   to any cloud LLM Project. Check the Sync Status field in its header to know when to regenerate.
7. IF, later, a hand-authored interactive deliverable is built (an HTML decision tool, a
   dashboard, anything under `deliverables/` that embeds its own snapshot of concept data) —
   register a Deliverable Parity Contract in ontology.md THE SAME SESSION it is built (§Deliverable
   Parity Contracts). Do this at build time, not retroactively after drift is first noticed —
   from this point on, ENRICHMENT_AGENT and CONFORMANCE_AGENT enforce it automatically.
8. Before every `git commit` or `git push`, follow §BUNDLE COMMIT CHECKLIST (Paths A–C).
   Say `"commit"` or `"push"` only after LOG_AGENT has appended to `log.md` for this session.

Result: a conformant OKF v0.1 bundle in one pass, ready for both IDE and cloud LLM deployment.
