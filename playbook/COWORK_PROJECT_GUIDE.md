# Cowork Project Guide — running a generated OKF folder inside a client Cowork Project

**How to deploy a standalone OKF bundle (e.g. `<domain>-okf`) as the knowledge base for a
per-client Claude Cowork Project, while keeping client work persistent and the shared standard
clean.** Companion to `PROJECTION_GUIDE.md` (which covers claude.ai/Gemini/ChatGPT Projects).

---

## The problem this solves

A generated OKF folder is standalone and self-maintaining (its `AGENTS.MD` governs both how to
*apply* the knowledge and how to *extend* it via ingestion). But when you use it inside a Cowork
**Project**, three things go wrong without extra scaffolding:

1. The Project creates its **own folder**; the OKF folder is **attached** alongside it. Nothing
   tells Claude which folder is the knowledge and which is the workspace.
2. **Attaching a folder does not make Claude read it.** With no instruction to consult the OKF,
   Claude answers from general training knowledge — the single most common failure.
3. Client-specific work risks being written **into the shared OKF**, polluting the standard that
   every client Project attaches.

---

## The model: 3 roles, 2 write-targets

An OKF folder plays three roles — canonical source, extractable knowledge (projections), and an
applied-analysis engine. Keep two write-targets separate:

| Content | Goes to | Why |
|---|---|---|
| Domain-general knowledge (new law, new pattern) | the **OKF folder** | true for every client; the OKF compounds |
| Client-specific work (this client's analysis, report) | the **Project folder** | belongs to the client; must never pollute the standard |

---

## Two instruction layers (non-overlapping)

- **OKF folder `AGENTS.MD`** — the *substance*: how to apply the bundle and how to extend it.
  Self-contained; this is why the folder works standalone with no Project.
- **Cowork Project instructions** — a *thin loader/router* (~20 lines): names the attached OKF
  folder, forces Claude to read its `AGENTS.MD` + `ontology.md` + `index.md` first, sets the
  read-only rule, and says where client outputs are saved. **No domain logic** — it defers to
  the OKF `AGENTS.MD`.

They interact by **bootstrap-and-defer**: the Project layer points; the OKF `AGENTS.MD` governs.

---

## Deployment modes

| Mode | Setup | Read/write |
|---|---|---|
| **A. Standalone folder** | Connect the OKF folder, chat (no Project) | Read + write the folder freely (apply + ingest) |
| **B. Client Cowork Project** | Create Project, attach the standard OKF folder | OKF **read-only**; client work → Project folder |
| **C. claude.ai Project** | Upload `projections/<slug>-master.md` + paste system instructions | Read-only projection; no ingestion |

In Cowork you attach the **structured folder** and Claude reads live files — do **not** use the
projection there. The projection is only for filesystem-less cloud Projects (Mode C).

---

## The fix for "Claude ignored the folder"

Put these three lines at the top of the Project instructions:

1. **Bootstrap read** — "Before answering anything, read `<okf-folder>/AGENTS.MD`, `ontology.md`
   and `index.md`. Answer only from that bundle."
2. **Cite-or-decline** — "Every substantive claim must cite the concept file it came from. If you
   cannot cite a bundle file, say the bundle doesn't cover it — do not answer from general
   knowledge without flagging it."
3. **Name the folder** — reference the attached folder by its actual name so Claude knows where
   to look.

---

## Paste-in Project-instructions template (generic)

Fill `<OKF-FOLDER>` (the attached folder name, e.g. `privacy-act-okf`) and `<CLIENT NAME>`.
Paste into the Cowork Project's instructions field.

```
CLIENT: <CLIENT NAME>

Two folders are available to you:
- `<OKF-FOLDER>/` — the SHARED STANDARD knowledge base (canonical OKF + ontology).
- This Project folder — <CLIENT NAME>'s workspace, where all client work is saved.

BOOT (do first, every session, before answering):
1. Read `<OKF-FOLDER>/AGENTS.MD`, `<OKF-FOLDER>/ontology.md`, `<OKF-FOLDER>/index.md`.
2. Operate under `<OKF-FOLDER>/AGENTS.MD` for ALL domain reasoning.
3. If `client-context.md` exists in this Project folder, read it — it is this client's profile.

ANSWER ONLY FROM THE OKF — cite or decline:
- Answer domain questions ONLY from concept files in `<OKF-FOLDER>/`, citing the file used.
- If you cannot cite a bundle file, say so and offer to research it — never answer from
  general knowledge without flagging it as un-sourced. Grade provenance as the bundle does.

READ-ONLY OKF:
- `<OKF-FOLDER>/` is READ-ONLY here. Never write client content into it or run its ingestion
  workflow during client work. New domain-general knowledge → note it for a separate
  maintenance session on `<OKF-FOLDER>/`, do not ingest it here.

CLIENT WORK — persistent, structured, in THIS Project folder:
- `client-context.md` (profile; create/update as facts emerge)
- `analyses/`  `inventory/`  `reports/`  (named `YYYY-MM-DD-<subject>`)
- Never write client-specific content into `<OKF-FOLDER>/`.

RULE: domain-general knowledge → the OKF (maintenance only); client-specific → this Project
folder. When unsure, treat it as client-specific and save it here.
```

---

## Maintaining the standard

Update the OKF once, in **Mode A** (a dedicated maintenance session where the OKF folder is the
working folder): drop new material into `inbox/`, run the ingestion workflow, commit + tag in
git. Every client Project then picks up the new version. Never mutate the standard mid-client-chat.

---

*Method document. The OKF folder's `AGENTS.MD` is the operational authority for applying and
extending the bundle; this guide only covers the Cowork Project wrapper around it.*

© 2026 Walter Adamson | linkedin.com/in/adamson | walter@outcomesnow.com
