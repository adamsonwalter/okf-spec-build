---
type: Reference
title: OKF Dialect — How This Kit Diverges From Vanilla OKF v0.1
description: Authoritative note on where this kit writes a stricter OKF than the Google spec requires, so consumers know what to expect and what does not round-trip.
tags: [governance, conformance, divergence]
okf_version: "0.1"
timestamp: 2026-06-24
---

## Version history
- 2026-06-24 — v1.0 — Initial divergence note. Separates spec floor from kit dialect; flags the read/write asymmetry; reclassifies the runtime cognitive layer as optional.

---

# Spec floor vs. this kit's dialect

Vanilla **Google OKF v0.1** requires exactly one thing: a `type` field in each
concept file's YAML frontmatter. Everything else — `title`, `description`,
`resource`, `tags`, `timestamp` — is optional, the body is free-form Markdown,
and **no ontology file is required**. A "valid OKF bundle" can be a folder of
Markdown files where each one declares a `type`.

This kit deliberately writes a **stricter dialect** on top of that floor. The
table below states every place we require or assume more than the spec, and
whether a vanilla bundle can round-trip through our tooling.

| Area | Vanilla OKF v0.1 | This kit's dialect | Round-trips? |
|---|---|---|---|
| Required fields | `type` only | `type`, `title`, `description`, `tags`, `timestamp`; `resource` where a route exists | A vanilla file missing these still **reads**, but our build script may reject or warn on **write** |
| `type` vocabulary | Any string | Closed set, defined in `ontology.md` | Unknown types are flagged, not accepted |
| Ontology file | Not required | **Required.** `ontology.md` is the authoritative type/tag registry and the input contract for `build-okf.py` | A bundle with no ontology is valid OKF but is **not** a valid bundle for this kit |
| `resource` | Free URI | Internal route convention (e.g. `/jcs/estimating-ledger`) | Cosmetic; reads fine elsewhere |
| Generation | Out of scope | `scripts/build-okf.py` from `catalog/pages.json` | Hand-written files are fine to read; regeneration overwrites from the catalog |
| Hub typing | Out of scope | `Client` type for hub-and-spoke aggregation | Extra type; ignored by vanilla readers |

## The one rule to remember

**We write a stricter OKF than we read.**

- *Reading:* anything that is valid OKF v0.1 (a `type` and a Markdown body) we
  can consume.
- *Writing:* our build script emits the stricter dialect above, driven by
  `ontology.md` + `catalog/pages.json`. Do not expect a plain vanilla bundle to
  pass back through `build-okf.py` unchanged — it is generated *from* the
  catalog, not reconstructed from loose files.

## On the ontology specifically

An ontology is **our convention, not an OKF requirement.** We keep one always,
on purpose: the moment `type` is a closed vocabulary, the ontology is what makes
that constraint real, auditable, and machine-checkable — and `build-okf.py`
already depends on it. So in this kit the ontology is mandatory **for our
dialect**, while remaining an addition above the spec floor. If you ever hand a
bundle to a third party expecting plain OKF, the ontology is bonus context they
can ignore, not something they must honour.

## What is NOT part of the spec (and never was)

The following are this kit's inventions, not OKF: `confidence`, `memory_tier`,
supersession/`archive`, contradiction records, the feedback-decay loop, and the
multi-agent runtime. See `docs/KIT_RESTRUCTURE.md` — these now live in an
optional layer that only liability-grade (T3) domains pull in.
