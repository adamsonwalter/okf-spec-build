# projections/

This folder contains **flat-file exports** of the OKF knowledge bundle, compiled by PROJECTION_AGENT for upload to cloud LLM environments.

---

## Why this folder exists

The structured bundle (subfolders, `index.md`, cross-links) is designed for local IDE use — Cursor, Antigravity, Claude Cowork. It relies on a file system to traverse.

Cloud LLM Projects (Gemini Gems, Claude.ai Projects, ChatGPT Projects) have no file system. They see a flat list of uploaded files. Relative links in `index.md` break. Uploading 40 separate concept files is noisy and hard to keep in sync.

The solution: **compile the whole bundle into one file**. That is what every file in this folder is.

---

## File naming

| File | Contents | When to upload |
|---|---|---|
| `<bundle-slug>-master.md` | Full bundle: ontology §0 + all active concepts | Default — use for most Projects |
| `by-tag/<tag>.md` | Scoped slice: ontology §0 + concepts tagged `<tag>` | Use when you want a focused Project on one topic |

---

## Sync model — ONE FILE IN, ONE FILE OUT

The source of truth is always the structured concept files in the parent bundle.

**To sync a cloud Project after bundle updates:**

1. Check the **Sync Status** field in the header of the projection file.
   - `Current` → no action needed.
   - `STALE` → the Log head date is newer than the Generated date → regenerate.
2. To regenerate: say `"build projection"` or `"update projection"` in your agent session.
3. Open the resulting file in this folder.
4. In your cloud Project: **delete the old upload, upload the new file**. One swap.

That is the entire sync operation. No diffing. No selecting individual files. One file replaces one file.

---

## What NEVER goes into a cloud Project

| File | Reason |
|---|---|
| `index.md` | Navigation file — relative links break outside the repo |
| `log.md` | Mutation history — not domain knowledge |
| `AGENTS.MD` / `LLM_WIKI.MD` etc. | Agent instruction files — not domain knowledge |
| Individual concept `.md` files | Fragmented — the projection already contains them all |
| `ontology.md` (standalone) | Already embedded as §0 in the projection |

**Exception:** if you build a tag-scoped Project and want the governance rules alongside it, you may upload `ontology.md` as a second file. But the master projection already embeds it.

---

## Contents of this folder

*(Populated by PROJECTION_AGENT — files here are derived artifacts, not source of truth)*
