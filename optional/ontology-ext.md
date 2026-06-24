---
type: Ontology
title: Optional Cognitive-Layer Field Extensions (T3 only)
description: Definitions for the opt-in frontmatter fields and conformance rules used only by liability-grade (T3) bundles that load LLM_WIKI.MD and FEEDBACK_LOOP.MD.
memory_tier: semantic
confidence: 1.0
okf_version: "0.1"
tags: [ontology, system, governance, optional]
timestamp: 2026-06-24
---

> This file is part of the OPTIONAL cognitive layer. It is NOT copied into a
> default (T1/T2) bundle. Load it only when a domain is liability-grade (T3) and
> you have also pulled in `optional/LLM_WIKI.MD` and `optional/FEEDBACK_LOOP.MD`.
> Core bundles do not recognise these fields and must not be validated against
> the rules below.

# Optional frontmatter fields

| Field | Type | Meaning | Required by |
|---|---|---|---|
| `confidence` | float 0.0–1.0 | Agent's confidence in the concept's claims. | LLM_WIKI memory model |
| `confidence_sources` | list | Evidence supporting the confidence value. | paired with `confidence` |
| `memory_tier` | enum (`semantic`/`episodic`/`working`/`archival`) | Memory tier per LLM_WIKI. | LLM_WIKI |
| `supersedes` / `superseded_by` | filename refs | Supersession links for versioned knowledge. | supersession protocol |
| `inferred_from` | list | Source concepts an `Inference` was derived from. | CONSUMPTION_AGENT |
| `review_required` | bool | Flags pending ontology extension review. | ONTOLOGY_AGENT |

# Conformance rules gated to this layer

These move OUT of core `ontology.md` and apply ONLY when this extension is loaded:

| Rule | Check | Severity |
|---|---|---|
| V3 | No concept has `confidence` without `confidence_sources` | WARNING |
| V5 | Every `type: Inference` has `inferred_from` with ≥1 source | ERROR |
| V6 | No `superseded_by` without a reciprocal `supersedes` in the target | ERROR |
| V7 | Every `<!-- CONFLICT -->` comment has a corresponding LOG entry | WARNING |
| V8 | This file and core `ontology.md` carry `memory_tier: semantic`, `confidence: 1.0` | ERROR |

Core bundles keep only V1 (type registered), V2 (tags registered), and V4
(stubs in `stubs/`). Everything above is opt-in.
