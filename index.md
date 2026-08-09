---
okf_version: "0.1"
---

# OKF Bundle Root

This is the root index of an OKF knowledge bundle managed by the OKF Bundle Bootstrap Kit.
Concept files are created and maintained by agents following AGENTS.MD, LLM_WIKI.MD, and FEEDBACK_LOOP.MD.
All types and relationships are governed by [ontology.md](ontology.md).

## Governance

* [ontology.md](ontology.md) — Single source of truth: type registry, relationship taxonomy, tag vocabulary

## Concepts

*(populated by INDEX_AGENT as concepts are created)*

## Stubs

* [Trigger C Activation — External Scheduler](stubs/trigger-c-scheduler.md) — Known gap: the time-based decay trigger needs an external scheduler to fire.
* [Relationship Graph Extraction](stubs/relationship-graph-extraction.md) — Known gap: the ten-relationship taxonomy is declared but nothing extracts it, so a bundle is a list, not a graph, and `supersedes` / `derived-from` decay undetected.
* [Certainty Vocabulary Reconciliation](stubs/certainty-vocabulary-reconciliation.md) — Known gap: a numeric `confidence` and a certainty tag can disagree, and no rule relates them.

## Reports

*(populated by LOG_AGENT: loop health and decay reports)*

## Archive

*(populated by INDEX_AGENT as concepts are superseded)*
