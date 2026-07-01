# CHANGELOG — OKF Kinetic Ontology Mapper (customised module)

Format: [Semantic Versioning](https://semver.org) — MAJOR.MINOR.PATCH

---

## [1.0.0] — 2026-06-24

### Added
- Customised, OKF-coupled fork of the general `kinetic-ontology-mapper` (v1.1), placed as
  an opt-in in-repo module under `ontology-mapper/`.
- `RELATIONSHIP-CROSSWALK.md` — the single coupling contract mapping the mapper's gate-logic
  verbs onto the parent kit's ten-relationship taxonomy; declares `crosswalk_version: 1`
  against parent `okf_version: 0.1`.
- **Seam B**: `pattern-library/` as a conformant OKF sub-bundle (own `ontology.md`
  registering `Pattern`/`Action Type`/`Gate`, `index.md`, `log.md`, and four seed Pattern
  concept files with OKF-relationship links). Compounding now rides the kit's
  ENRICHMENT→LINK→INDEX→LOG pipeline instead of a flat log.

### Notes
- Intentionally duplicates the general mapper's engine. The general mapper remains the
  domain-agnostic tool; this one is specialised for use inside an OKF estate.
- Module is decoupled: removing `ontology-mapper/` leaves the core kit unaffected.
