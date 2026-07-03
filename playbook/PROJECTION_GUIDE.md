# Projection Guide — From OKF Bundle to Cloud LLM Project

**How to compile your structured knowledge bundle into a single file for Gemini Gems, Claude.ai Projects, and ChatGPT Projects.**

---

## The core problem this solves

Your OKF bundle is rich and navigable in an IDE: subfolders, cross-links, `index.md` navigation, typed concepts, a structured ontology. That structure is its strength for local agent work.

But cloud LLM Projects have no file system. When you upload `index.md`, all its relative links (`[VNI West](projects/vni-west.md)`) point to nothing. When you upload 40 separate concept files, keeping them in sync is a manual nightmare — which file changed? Which do I delete and re-upload?

The projection pattern solves both problems: **compile the entire bundle into one flat Markdown file** and upload that. The LLM reads it as one coherent document. Sync is one file swap.

---

## Two deployment modes from one build

```
Your OKF bundle (local, structured)
│
├── IDE / Claude Cowork / Antigravity   ← use the full folder directly
│   - Full cross-links, subfolders, ontology checks
│   - Agents read AGENTS.MD and operate on live files
│
└── Cloud LLM Project                   ← use a projection file
    - Gemini Gem, Claude.ai Project, ChatGPT Project
    - Upload ONE file: projections/<bundle>-master.md
    - The projection embeds the ontology as §0 + all concepts
```

---

## How to build a projection

In any agent session (Antigravity, Claude Cowork, Cursor):

```
"build projection"           → compiles full master projection
"build projection [tag]"     → compiles a tag-scoped slice
"update projection"          → same as build projection (rebuilds from current state)
```

The PROJECTION_AGENT will:
1. Read `log.md` to get the Log Head date (the date of the newest bundle change)
2. Walk all concept files, excluding index.md, log.md, stubs, archive, and agent instructions
3. Compile: Sync Header → §0 Ontology → all concepts (alphabetical)
4. Write to `projections/<bundle-slug>-master.md`
5. Report: file path, concept count, generated datetime

---

## Anatomy of a projection file

```
# <Bundle Title> — Knowledge Projection

| Field             | Value                              |
|---|---|
| Generated         | 2026-06-27T18:00:00Z               |
| Scope             | master (all concepts)              |
| Concepts included | 34                                 |
| Log head          | 2026-06-27                         |
| Sync status       | Current                            |

> UPLOAD INSTRUCTIONS: Upload THIS FILE ONLY …

---

## §0 Ontology
[full ontology body — type registry, tags, relationships]

---

## Battery Substitution Balancing Loop
*Type: Concept | Tags: bess, system-dynamics | Updated: 2026-06-27*

[concept body]

---

## CER-Price Death Spiral
*Type: Concept | Tags: cer, system-dynamics | Updated: 2026-06-27*

[concept body]

--- [and so on for every concept, alphabetical]
```

---

## Sync model

### When to regenerate

Open `projections/<bundle>-master.md` and look at the header table:

| Sync Status | Meaning | Action |
|---|---|---|
| `Current` | Generated date ≥ Log head date | No action needed |
| `STALE` | Log head is newer than Generated | Regenerate and re-upload |

The Log head advances every time you ingest new content into the bundle. After each ingest cycle, say `"update projection"` to bring the projection current.

### How to update a cloud Project

1. Regenerate: `"update projection"` in your agent session
2. Open your cloud Project
3. Delete the old projection file upload
4. Upload the new `projections/<bundle>-master.md`

**That is the entire operation. One file in, one file out.**

There is no need to track which individual concept files changed. The projection includes everything; replace the whole thing.

---

## Tag-scoped slices — when to use them

Use a scoped slice when:
- Your bundle is large (50+ concepts) and you want a focused Project on one topic
- You have multiple teams or use cases that each need a different subset
- You want to test a concept cluster in isolation

```
"build projection transmission"    → projections/by-tag/transmission.md
"build projection regulatory"      → projections/by-tag/regulatory.md
```

Each slice contains: Sync Header + §0 Ontology + only concepts tagged `<tag>`.

**Note:** the ontology is always included even in slices, so the cloud LLM understands the type/tag vocabulary for the concepts it receives.

---

## What NOT to upload to a cloud Project

| File | Why not |
|---|---|
| `index.md` | Navigation file — relative links break with no file system |
| `log.md` | Mutation audit log — not domain knowledge |
| `AGENTS.MD` | Agent operating instructions — not for the consuming LLM |
| Individual concept files | Fragmented — the projection already contains them |
| `ontology.md` standalone | Already embedded as §0 in every projection |

**One exception:** if you build a tag-scoped Project and want the full governance registry visible, upload `ontology.md` as a second file alongside the tag slice. But for a master projection, it is redundant.

---

## Technical debt and sync hygiene

The projection is a **derived artifact** — it is generated from the source of truth (the structured concept files) and should never be edited manually. If you find an error in a projection, fix it in the source concept file and regenerate.

Recommendations:
- **After every ingest session:** run `"update projection"` before committing. The projection in the repo is then always at most one session behind.
- **Before every commit:** confirm `log.md` reflects this session (ingest appends via LOG_AGENT;
  direct edits need `"append log"` / `"repair log"` first). See `playbook/BUNDLE_COMMIT_CHECKLIST.md`.
- **Tag the projection in git alongside the bundle version:** `git tag v2 && git push --tags`. This makes it trivial to know what the cloud Project was loaded from.
- **Never mix projections and concept files in the same cloud Project upload.** The projection is self-contained.

---

## Cross-environment topology (full picture)

```
   AUTHOR / REFRESH (local agent environments)
   ┌──────────────────────────────────────────────┐
   │ Antigravity · Cowork · Cursor                 │
   │  - ingest inbox/ → ENRICHMENT→LINK→INDEX→LOG  │
   │  - "update projection" → PROJECTION_AGENT      │
   │  - commit + push to git                        │
   └──────────────────────┬───────────────────────┘
                          │ git (source of truth)
                          ▼
                     GitHub repo
                     (per-domain bundle)
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
   LOCAL IDE USE                  CLOUD LLM PROJECTS
   (full structured folder)       (projections/ only)
   Cursor, Antigravity            Gemini Gem
   Claude Cowork                  Claude.ai Project
                                  ChatGPT Project
                                  (upload master.md; swap on update)
```

---

*This guide is a method document. The operational instructions are in `AGENTS.MD` (PROJECTION_AGENT spec). The folder structure is in `projections/README.md`.*
