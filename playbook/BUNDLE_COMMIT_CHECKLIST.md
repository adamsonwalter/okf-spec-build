# Bundle Commit Checklist — never commit without `log.md`

**Ships with every OKF bundle generated from okf-spec-build.** Operational authority:
`AGENTS.MD` (§BUNDLE COMMIT CHECKLIST, LOG_AGENT, invariant #9). This page is the printable
summary agents and humans follow before every `git commit` or `git push`.

---

## Why this exists

`log.md` is the bundle's mutation audit trail. `CHANGELOG.md` (kit repo only) tracks *releases*;
`log.md` tracks *every change*. LOG_AGENT used to run only after ENRICHMENT_AGENT, so direct
edits and `git commit` without ingest left `log.md` empty while the rest of the bundle evolved.
CONFORMANCE_AGENT **CHECK_8** now fails placeholder-only logs.

---

## Path A — Ingest session (concepts added/updated)

The enrichment pipeline **must** complete before commit:

```
ingest → ENRICHMENT → LINK → INDEX → LOG → (optional) update projection → commit
```

1. Run ingest (`"ingest inbox/"` or equivalent).
2. Confirm `log.md` has a new entry under today's `## YYYY-MM-DD` for this batch.
3. Run `"update projection"` if you use cloud LLM Projects.
4. `git add -A && git commit` — **`log.md` must be in the commit.**

If ingest finished but `log.md` did not change, say **"repair log"** before committing.

---

## Path B — Direct edits (no ingest)

Any change to bundle files **without** going through ENRICHMENT — including:

- `ontology.md`, `AGENTS.MD`, playbooks, `README.md`
- Hand-editing a concept file
- Moving/renaming files, adding `deliverables/`, registering parity contracts
- Projection scaffold, `.gitignore`, infrastructure

**LOG_AGENT runs first, commit second:**

1. List files changed (`git diff --name-only` or your session list).
2. Say **"append log"** or **"repair log"** — LOG_AGENT adds **Kit**, **Update**,
   **Restructure**, or **Creation** lines under today's date block.
3. Run **INDEX_AGENT** if concept files or directories changed.
4. `git add -A && git commit` — **`log.md` must be in the commit.**
5. `git push` (if requested).

Orchestrator also routes **"commit"**, **"push"**, and **"save"** → LOG_AGENT before git.

---

## Path C — First clone into a new domain repo

When you `git clone` the kit into a new domain bundle:

1. Copy `templates/log-domain-init.md` → `log.md` (replace date + domain name).
   **Do not** keep the kit's own release history in a domain bundle's log.
2. Complete domain intake (`OKF_QUICKSTART.md` §A).
3. First ingest → Path A from then on.

---

## Never do this

- `git commit` with bundle file changes but no `log.md` update since the last `##` date block.
- Replace `log.md` body with a placeholder (`"populated by LOG_AGENT"`).
- Delete prior `log.md` date blocks.
- Assume PROJECTION_AGENT or `git` history substitutes for `log.md`.

---

## One-liner for agents

> Before `git commit` or `git push`: verify `log.md` reflects every file changed this session.
> If not, run LOG_AGENT (`repair log` / `append log`) first. Fail CHECK_8 if unsure.

---

© 2026 Walter Adamson | okf-spec-build kit
