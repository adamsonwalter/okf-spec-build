# optional/ — T3 Cognitive Layer (opt-in)

These files are **not** part of a default bundle. The operating-repo evidence
(see `../docs/KIT_RESTRUCTURE.md`) showed the runtime cognitive layer left almost
no trace in real use, so it is demoted to opt-in here.

Pull these in **only** for liability-grade (T3) domains — anything where a wrong
claim costs money, safety, or legal exposure (the Optus-class case).

| File | What it adds |
|---|---|
| `LLM_WIKI.MD` | Memory tiers, confidence scoring, supersession, gap-finding. |
| `FEEDBACK_LOOP.MD` | Continuous synthesis loop, contradiction resolution, decay model. |
| `ontology-ext.md` | Definitions for the opt-in fields (`confidence`, `memory_tier`, etc.) and the conformance rules (V3, V5–V8) those fields trigger. |

## To enable for a T3 bundle

1. Copy these three files into the bundle root (alongside `AGENTS.MD`).
2. Tell the agent to also read `LLM_WIKI.MD`, `FEEDBACK_LOOP.MD`, and
   `ontology-ext.md`.
3. The enrichment/link/consumption/conformance agents in `AGENTS.MD` then
   activate their optional behaviours.

A core (T1/T2) bundle ignores all of the above and runs on the six standard
fields only.
