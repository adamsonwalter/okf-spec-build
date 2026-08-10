#!/usr/bin/env python3
"""Tests for scripts/okf_check.py.

Each check gets a bundle that fails it, plus a baseline that passes. Run:

    python3 -m unittest discover -s tests
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "okf_check.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import okf_check as K  # noqa: E402


ONTOLOGY = """\
---
type: Ontology
title: Bundle Ontology
description: Registry.
memory_tier: semantic
confidence: 1.0
timestamp: 2026-08-09T00:00:00Z
tags: [ontology, system, governance]
---

# Type Registry

| Type | Description | Typical Body Sections | Required Sections | Required Fields |
|---|---|---|---|---|
| `Concept` | A discrete idea. | Schema | — | — |
| `Reference` | A pointer to a source. | Summary | Citations | `resource` |
| `Ontology` | This file. | — | — | — |
| `Stub` | A placeholder. | — | — | — |
| `Coverage Ledger` | An inventory. | — | — | — |

# Tag Taxonomy

| Tag | Meaning |
|---|---|
| `system` | Infrastructure |
| `governance` | Rules |
| `ontology` | Registry |
| `coverage` | Completeness audit |

# Validation Rules

| Rule | Check | Severity |
|---|---|---|
| V1 | Every concept's `type` is registered | ERROR |

# Deliverable Parity Contracts

| Contract ID | Deliverable file | Source scope | Identity key | Record pattern | Source key pattern | Severity |
|---|---|---|---|---|---|---|
| *(none at bundle initialisation)* | — | — | — | — | — | — |

**Worked example** (illustrative only — not a live contract):

| Contract ID | Deliverable file | Source scope | Identity key | Record pattern | Source key pattern | Severity |
|---|---|---|---|---|---|---|
| `made-up` | `deliverables/nope.html` | `scenarios/scenario-*.md` (one per file) | letter | — | — | ERROR |

# Source Coverage Contracts

| Contract ID | Coverage ledger file | Source | Severity |
|---|---|---|---|
| *(none at bundle initialisation)* | — | — | — |
"""

LOG = "# Bundle Update Log\n\n## 2026-08-09\n\n* **Kit**: something changed.\n"

CONCEPT = """\
---
type: Concept
title: A Thing
description: A thing that exists.
timestamp: 2026-08-09T00:00:00Z
tags: [system]
---

# A Thing

Body.
"""


class BundleFixture(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.write("ontology.md", ONTOLOGY)
        self.write("log.md", LOG)
        self.write("a-thing.md", CONCEPT)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def run_checks(self):
        return K.run_checks(K.Bundle(self.root))[0]

    def codes(self, severity=None):
        return [f.check for f in self.run_checks()
                if severity is None or f.severity == severity]

    def assertFails(self, check):
        findings = self.run_checks()
        errs = [f.check for f in findings if f.severity == K.ERROR]
        self.assertIn(check, errs, f"expected {check} in errors; got {errs}")

    def assertWarns(self, check):
        self.assertIn(check, self.codes(K.WARNING))


class TestBaseline(BundleFixture):
    def test_clean_bundle_has_no_errors(self):
        errors = [str(f) for f in self.run_checks() if f.severity == K.ERROR]
        self.assertEqual(errors, [])

    def test_worked_example_table_is_not_a_live_contract(self):
        # The example names deliverables/nope.html, which does not exist. If the
        # marker were ignored, this would be a CHECK_7 error.
        self.assertNotIn("CHECK_7", [f.check for f in self.run_checks()
                                     if f.severity == K.ERROR])

    def test_placeholder_contract_rows_report_skip_not_pass(self):
        skips = [f.check for f in self.run_checks() if f.severity == K.SKIP]
        self.assertIn("CHECK_7", skips)
        self.assertIn("CHECK_9", skips)


class TestFrontmatter(BundleFixture):
    def test_missing_frontmatter(self):
        self.write("broken.md", "# No frontmatter\n\nText.\n")
        self.assertFails("CHECK_1")

    def test_unclosed_frontmatter(self):
        self.write("broken.md", "---\ntype: Concept\ntitle: x\n")
        self.assertFails("CHECK_1")

    def test_empty_type(self):
        self.write("broken.md", CONCEPT.replace("type: Concept", "type: "))
        self.assertFails("CHECK_2")

    def test_unregistered_type(self):
        self.write("broken.md", CONCEPT.replace("type: Concept", "type: Pattern"))
        self.assertFails("V1")

    def test_all_caps_files_are_not_concepts(self):
        self.write("AGENTS.MD", "# Instructions\n\nNo frontmatter here.\n")
        self.assertEqual([f for f in self.run_checks() if f.severity == K.ERROR], [])


class TestRegistryDrivenRequirements(BundleFixture):
    """V9 — the registry declares validity; one rule enforces every type."""

    def test_missing_universal_field(self):
        self.write("broken.md", CONCEPT.replace("description: A thing that exists.\n", ""))
        self.assertFails("V9")

    def test_missing_type_specific_field(self):
        self.write("ref.md", """\
---
type: Reference
title: A Source
description: Points somewhere.
timestamp: 2026-08-09T00:00:00Z
tags: [system]
---

# A Source

## Citations

- something
""")
        # Reference requires `resource` per the Type Registry.
        self.assertFails("V9")

    def test_missing_type_specific_section(self):
        self.write("ref.md", """\
---
type: Reference
title: A Source
description: Points somewhere.
resource: https://example.org
timestamp: 2026-08-09T00:00:00Z
tags: [system]
---

# A Source

No citations section here.
""")
        self.assertFails("V9")

    def test_satisfied_requirements_pass(self):
        self.write("ref.md", """\
---
type: Reference
title: A Source
description: Points somewhere.
resource: https://example.org
timestamp: 2026-08-09T00:00:00Z
tags: [system]
---

# A Source

## Citations

- something
""")
        self.assertEqual([f for f in self.run_checks() if f.severity == K.ERROR], [])

    def test_new_type_needs_no_new_rule(self):
        """Registering a type with requirements is a table row, not a rule."""
        self.write("ontology.md", ONTOLOGY.replace(
            "| `Stub` | A placeholder. | — | — | — |",
            "| `Stub` | A placeholder. | — | — | — |\n"
            "| `Gate` | A decidable test. | — | Pass Criterion | `resource` |"))
        self.write("g.md", """\
---
type: Gate
title: A Gate
description: A test.
timestamp: 2026-08-09T00:00:00Z
tags: [system]
---

# A Gate

Nothing required present.
""")
        findings = [f for f in self.run_checks() if f.severity == K.ERROR]
        messages = " ".join(f.message for f in findings)
        self.assertIn("resource", messages)
        self.assertIn("Pass Criterion", messages)


class TestReservedFiles(BundleFixture):
    def test_index_with_frontmatter(self):
        self.write("sub/index.md", "---\ntype: Concept\n---\n\n# Index\n")
        self.assertFails("CHECK_3")

    def test_root_index_may_carry_okf_version(self):
        self.write("index.md", '---\nokf_version: "0.1"\n---\n\n# Index\n')
        self.assertEqual([f for f in self.run_checks() if f.severity == K.ERROR], [])

    def test_log_out_of_order(self):
        self.write("log.md", "# Log\n\n## 2026-01-01\n\n* a\n\n## 2026-08-09\n\n* b\n")
        self.assertFails("CHECK_4")

    def test_log_placeholder_only(self):
        self.write("log.md", "# Bundle Update Log\n\npopulated by LOG_AGENT\n")
        self.assertFails("CHECK_8")

    def test_missing_log(self):
        os.remove(os.path.join(self.root, "log.md"))
        self.assertFails("CHECK_8")


class TestLinksTagsAndStubs(BundleFixture):
    def test_broken_internal_link_warns(self):
        self.write("a-thing.md", CONCEPT + "\nSee [other](./missing.md).\n")
        self.assertWarns("CHECK_5")

    def test_link_inside_a_code_fence_is_an_example_not_a_link(self):
        self.write("a-thing.md", CONCEPT +
                   "\n```markdown\n- See [Example](../nowhere/example.md) — **references**.\n```\n")
        self.assertNotIn("CHECK_5", self.codes(K.WARNING))

    def test_external_link_ignored(self):
        self.write("a-thing.md", CONCEPT + "\nSee [site](https://example.org).\n")
        self.assertNotIn("CHECK_5", self.codes(K.WARNING))

    def test_unregistered_tag_warns(self):
        self.write("a-thing.md", CONCEPT.replace("tags: [system]", "tags: [invented]"))
        self.assertWarns("V2")

    def test_stub_outside_stubs_warns(self):
        self.write("loose.md", CONCEPT.replace("type: Concept", "type: Stub"))
        self.assertWarns("V4")

    def test_archived_stub_is_the_declared_exception(self):
        self.write("archive/old.md", CONCEPT.replace("type: Concept", "type: Stub"))
        self.assertNotIn("V4", self.codes(K.WARNING))

    def test_declared_zero_sources_is_not_a_missing_field(self):
        # 'confidence_sources: 0' is correct for a Stub at confidence 0.0.
        # Treating 0 as absent would flag every properly-formed stub.
        self.write("a-thing.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nconfidence: 0.0\nconfidence_sources: 0"))
        flagged = [f.path for f in self.run_checks() if f.check == "V3"]
        self.assertNotIn("a-thing.md", flagged)

    def test_confidence_without_sources_warns(self):
        self.write("a-thing.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nconfidence: 0.8"))
        self.assertWarns("V3")


class TestConventionsFoundInRealCorpora(BundleFixture):
    """Three false-positive classes found by running on a second real bundle."""

    def test_root_relative_link_resolves_from_the_bundle_root(self):
        # A leading "/" means the bundle root, not the filesystem root. One
        # corpus used this throughout: 134 false broken links, 20 real targets.
        self.write("case-studies/one.md", CONCEPT)
        self.write("a-thing.md", CONCEPT + "\nSee [one](/case-studies/one.md).\n")
        self.assertNotIn("CHECK_5", self.codes(K.WARNING))

    def test_root_relative_link_to_a_missing_file_still_warns(self):
        self.write("a-thing.md", CONCEPT + "\nSee [gone](/nowhere/gone.md).\n")
        self.assertWarns("CHECK_5")

    def test_ai_context_is_tooling_not_concepts(self):
        self.write(".ai_context/system_map.md", "# Map\n\nNo frontmatter.\n")
        self.assertNotIn("CHECK_1", self.codes(K.ERROR))

    def test_ledger_status_may_carry_a_note(self):
        # "Captured *(closed 2026-07-03 remediation pass)*" is captured.
        self.write("ontology.md", ONTOLOGY.replace(
            "| *(none at bundle initialisation)* | — | — | — |\n",
            "| `src` | `coverage/ledger.md` | A doc | ERROR |\n"))
        self.write("coverage/ledger.md", """\
---
type: Coverage Ledger
title: Ledger
description: Inventory.
timestamp: 2026-08-09T00:00:00Z
tags: [coverage]
---

# Ledger

| Unit | Status | Captured in |
|---|---|---|
| Box 4 | Captured *(closed 2026-07-03 remediation pass)* | a-thing.md |
| Box 8 | Partial (see note) | a-thing.md |
""")
        self.assertNotIn("CHECK_9", self.codes(K.ERROR))

    def test_an_annotated_not_yet_checked_still_fails(self):
        # The note must not become a way to smuggle an unresolved row past.
        self.write("ontology.md", ONTOLOGY.replace(
            "| *(none at bundle initialisation)* | — | — | — |\n",
            "| `src` | `coverage/ledger.md` | A doc | ERROR |\n"))
        self.write("coverage/ledger.md", """\
---
type: Coverage Ledger
title: Ledger
description: Inventory.
timestamp: 2026-08-09T00:00:00Z
tags: [coverage]
---

# Ledger

| Unit | Status | Captured in |
|---|---|---|
| Box 4 | Not yet checked *(waiting on the second pass)* | — |
""")
        self.assertFails("CHECK_9")


class TestCertaintyBands(BundleFixture):
    """V12 — declared in the registry, enforced by one rule, WARNING by design."""

    def _with_band(self, band):
        self.write("ontology.md", ONTOLOGY.replace(
            "| Tag | Meaning |\n|---|---|\n| `system` | Infrastructure |",
            "| Tag | Meaning | Certainty band |\n|---|---|---|\n"
            "| `system` | Infrastructure | |\n"
            f"| `confirmed` | Settled | {band} |"))

    def _concept_at(self, confidence):
        self.write("a-thing.md", CONCEPT.replace(
            "tags: [system]",
            f"tags: [system, confirmed]\nconfidence: {confidence}\nconfidence_sources: 1"))

    def test_confidence_inside_the_band_passes(self):
        self._with_band(">= 0.80")
        self._concept_at(0.9)
        self.assertNotIn("V12", self.codes())

    def test_confidence_below_a_ge_band_warns(self):
        self._with_band(">= 0.80")
        self._concept_at(0.6)
        self.assertWarns("V12")

    def test_le_band(self):
        self._with_band("<= 0.80")
        self._concept_at(0.95)
        self.assertWarns("V12")

    def test_range_band(self):
        self._with_band("0.60 - 0.90")
        self._concept_at(0.95)
        self.assertWarns("V12")

    def test_band_breach_never_blocks(self):
        # A band is a sanity check on a judgment, not an authority over it.
        self._with_band(">= 0.95")
        self._concept_at(0.6)
        _, exit_code = K.validate(self.onto) if hasattr(K, "validate") else (None, 0)
        self.assertNotIn("V12", self.codes(K.ERROR))

    def test_empty_band_is_never_checked(self):
        self._with_band("")
        self._concept_at(0.1)
        self.assertNotIn("V12", self.codes())

    def test_unreadable_band_is_an_error_not_silence(self):
        self._with_band("fairly high")
        self._concept_at(0.9)
        self.assertFails("ONTOLOGY")

    def test_band_parsing(self):
        self.assertEqual(K.parse_band(">= 0.80"), (0.8, 1.0))
        self.assertEqual(K.parse_band("<= 0.95"), (0.0, 0.95))
        self.assertEqual(K.parse_band("0.60 - 0.90"), (0.6, 0.9))
        self.assertEqual(K.parse_band("0.60 – 0.90"), (0.6, 0.9))
        self.assertIsNone(K.parse_band("—"))
        self.assertIsNone(K.parse_band(""))
        self.assertEqual(K.parse_band("high-ish"), "malformed")


class TestShowYourWorking(BundleFixture):
    """V3 — confidence must show working: sources OR a Citations section."""

    def test_confidence_with_citations_section_passes(self):
        self.write("a-thing.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nconfidence: 0.9") + "\n## Citations\n\n- a source\n")
        flagged = [f.path for f in self.run_checks() if f.check == "V3"]
        self.assertNotIn("a-thing.md", flagged)

    def test_confidence_with_sources_passes(self):
        self.write("a-thing.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nconfidence: 0.9\nconfidence_sources: 3"))
        flagged = [f.path for f in self.run_checks() if f.check == "V3"]
        self.assertNotIn("a-thing.md", flagged)

    def test_confidence_with_neither_warns(self):
        self.write("a-thing.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nconfidence: 0.9"))
        flagged = [f.path for f in self.run_checks() if f.check == "V3"]
        self.assertIn("a-thing.md", flagged)


class TestStubsAreNotClaims(BundleFixture):
    """A Stub's confidence 0.0 means nothing asserted yet, not asserted weakly."""

    def test_stub_is_exempt_from_v3(self):
        self.write("stubs/gap.md", CONCEPT.replace(
            "type: Concept", "type: Stub").replace(
            "tags: [system]", "tags: [system]\nconfidence: 0.0"))
        flagged = [f.path for f in self.run_checks() if f.check == "V3"]
        self.assertNotIn(os.path.join("stubs", "gap.md"), flagged)

    def test_stub_is_exempt_from_v12(self):
        self.write("ontology.md", ONTOLOGY.replace(
            "| Tag | Meaning |\n|---|---|\n| `system` | Infrastructure |",
            "| Tag | Meaning | Certainty band |\n|---|---|---|\n"
            "| `system` | Infrastructure | |\n| `contested` | Open | 0.60 - 0.90 |"))
        self.write("stubs/gap.md", CONCEPT.replace(
            "type: Concept", "type: Stub").replace(
            "tags: [system]", "tags: [system, contested]\nconfidence: 0.0"))
        self.assertNotIn("V12", self.codes())

    def test_a_real_concept_at_the_same_confidence_is_still_checked(self):
        self.write("a-thing.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nconfidence: 0.0"))
        flagged = [f.path for f in self.run_checks() if f.check == "V3"]
        self.assertIn("a-thing.md", flagged)


class TestSupersession(BundleFixture):
    def test_one_sided_supersession_fails(self):
        self.write("old.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nsuperseded_by: new"))
        self.write("new.md", CONCEPT)
        self.assertFails("V6")

    def test_reciprocated_supersession_passes(self):
        self.write("old.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nsuperseded_by: new"))
        self.write("new.md", CONCEPT.replace(
            "tags: [system]", "tags: [system]\nsupersedes: old"))
        self.assertNotIn("V6", self.codes(K.ERROR))


class TestDeliverableParity(BundleFixture):
    """CHECK_7 — a real set diff once the contract declares how to read records."""

    ROW = "| *(none at bundle initialisation)* | — | — | — | — | — | — |"

    def _contract(self, record_pattern="—", source_pattern="—"):
        self.write("ontology.md", ONTOLOGY.replace(
            self.ROW,
            "| `map` | `deliverables/map.html` | `items/item-*.md` | letter | "
            f"{record_pattern} | {source_pattern} | ERROR |"))

    def _items(self, letters):
        for letter in letters:
            self.write(f"items/item-{letter.lower()}.md",
                       CONCEPT.replace("title: A Thing", f"title: Item {letter} — a thing"))

    def _deliverable(self, letters):
        records = ",".join('{"id":"%s"}' % l for l in letters)
        self.write("deliverables/map.html", f"<script>[{records}]</script>")

    def test_matching_sets_pass_silently(self):
        self._contract('`"id":"([A-Z])"`', "`Item ([A-Z])`")
        self._items("AB"); self._deliverable("AB")
        self.assertNotIn("CHECK_7", self.codes())

    def test_missing_record_is_named(self):
        self._contract('`"id":"([A-Z])"`', "`Item ([A-Z])`")
        self._items("AB"); self._deliverable("A")
        self.assertFails("CHECK_7")
        msg = " ".join(f.message for f in self.run_checks() if f.check == "CHECK_7")
        self.assertIn("B", msg)

    def test_orphan_record_is_named(self):
        # Only a real diff can see this; filename matching never could.
        self._contract('`"id":"([A-Z])"`', "`Item ([A-Z])`")
        self._items("A"); self._deliverable("AZ")
        msg = " ".join(f.message for f in self.run_checks() if f.check == "CHECK_7")
        self.assertIn("no source concept", msg)

    def test_no_record_pattern_reports_skip_never_pass(self):
        self._contract()
        self._items("A")
        self.write("deliverables/map.html", "<p>item-a</p>")
        skips = [f for f in self.run_checks()
                 if f.check == "CHECK_7" and f.severity == K.SKIP]
        self.assertTrue(skips)
        self.assertIn("cannot be detected", skips[0].message)

    def test_pattern_matching_nothing_is_reported_not_diffed(self):
        self._contract('`"id":"([A-Z])"`', "`Item ([A-Z])`")
        self._items("A"); self.write("deliverables/map.html", "<p>nothing here</p>")
        msg = " ".join(f.message for f in self.run_checks() if f.check == "CHECK_7")
        self.assertIn("matched nothing", msg)

    def test_invalid_regex_is_an_error(self):
        self._contract("`([A-Z`", "`Item ([A-Z])`")
        self._items("A"); self._deliverable("A")
        self.assertFails("CHECK_7")

    def test_source_title_not_matching_the_key_pattern_is_an_error(self):
        self._contract('`"id":"([A-Z])"`', "`Scenario ([A-Z])`")
        self._items("A"); self._deliverable("A")
        msg = " ".join(f.message for f in self.run_checks() if f.check == "CHECK_7")
        self.assertIn("no identity key", msg)


class TestCoverageContracts(BundleFixture):
    def _register(self):
        self.write("ontology.md", ONTOLOGY.replace(
            "| *(none at bundle initialisation)* | — | — | — |\n",
            "| `src-coverage` | `coverage/ledger.md` | A document | ERROR |\n"))

    def test_unresolved_ledger_row_fails(self):
        self._register()
        self.write("coverage/ledger.md", """\
---
type: Coverage Ledger
title: Ledger
description: Inventory.
timestamp: 2026-08-09T00:00:00Z
tags: [coverage]
---

# Ledger

| Unit | Status | Captured in |
|---|---|---|
| Box 1 | Captured | a-thing.md |
| Box 4 | Not yet checked | — |
""")
        self.assertFails("CHECK_9")

    def test_fully_resolved_ledger_passes(self):
        self._register()
        self.write("coverage/ledger.md", """\
---
type: Coverage Ledger
title: Ledger
description: Inventory.
timestamp: 2026-08-09T00:00:00Z
tags: [coverage]
---

# Ledger

| Unit | Status | Captured in |
|---|---|---|
| Box 1 | Captured | a-thing.md |
| Box 4 | Not applicable | — |
""")
        self.assertNotIn("CHECK_9", self.codes(K.ERROR))

    def test_missing_ledger_file_fails(self):
        self._register()
        self.assertFails("CHECK_9")


class TestNestedBundles(BundleFixture):
    def test_subtree_with_its_own_ontology_is_not_checked_here(self):
        self.write("sub-bundle/ontology.md", ONTOLOGY)
        self.write("sub-bundle/thing.md", CONCEPT.replace("type: Concept", "type: Pattern"))
        bundle = K.Bundle(self.root)
        self.assertTrue(any(p.endswith("sub-bundle") for p in bundle.nested_bundles))
        self.assertNotIn("V1", [f.check for f in K.run_checks(bundle)[0]])


class TestFrontmatterNesting(unittest.TestCase):
    """OKF v0.2 needs nesting: sources is a list of mappings (§5.1), verified a
    list of {by, at} events (§5.2). The old flat parser turned a block sequence
    into junk keys with no error, which is the one thing it promises not to do.
    """

    def parse(self, frontmatter):
        return K.split_frontmatter("---\ntype: X\n" + frontmatter + "\n---\nbody\n")

    def test_block_sequence_of_flow_mappings(self):
        fm, _, err = self.parse(
            "verified:\n"
            "  - { by: human:adamson, at: 2026-07-29T00:00:00Z }\n"
            "  - { by: process:claim-audit, at: 2026-07-29T00:00:00Z }")
        self.assertIsNone(err)
        self.assertEqual([e["by"] for e in fm["verified"]],
                         ["human:adamson", "process:claim-audit"])

    def test_colons_inside_a_flow_mapping_survive(self):
        # 'resource: https://…' and 'by: human:x' both carry a second colon.
        fm, _, err = self.parse(
            "sources:\n  - { id: a, resource: https://oaic.gov.au/x }")
        self.assertIsNone(err)
        self.assertEqual(fm["sources"][0]["resource"], "https://oaic.gov.au/x")

    def test_nested_block_mapping(self):
        fm, _, err = self.parse("executor:\n  resource: refs/run.md\n  receipt: [job_id]")
        self.assertIsNone(err)
        self.assertEqual(fm["executor"], {"resource": "refs/run.md",
                                          "receipt": ["job_id"]})

    def test_body_is_not_swallowed(self):
        fm, body, err = self.parse("verified:\n  - { by: human:a, at: 2026-01-01 }")
        self.assertIsNone(err)
        self.assertEqual(body.strip(), "body")

    def test_unreadable_nesting_is_reported_not_dropped(self):
        _, _, err = self.parse("verified:\n  - by: human:a\n    at: 2026-01-01")
        self.assertIsNotNone(err)
        self.assertIn("nests under a list item", err)

    def test_flat_frontmatter_still_parses(self):
        fm, _, err = self.parse("title: T\ntags: [a, b]\nconfidence: 0.9")
        self.assertIsNone(err)
        self.assertEqual((fm["title"], fm["tags"], fm["confidence"]),
                         ("T", ["a", "b"], 0.9))


class TestTrustTiers(unittest.TestCase):
    """Spec §5.3. Derived on read, never stored."""

    def test_absent_verified_is_unverified(self):
        self.assertEqual(K.trust_tier({}), "unverified")

    def test_non_human_actors_are_machine_confirmed(self):
        self.assertEqual(
            K.trust_tier({"verified": [{"by": "process:nightly", "at": "x"}]}),
            "machine-confirmed")

    def test_any_human_actor_wins(self):
        self.assertEqual(
            K.trust_tier({"verified": [{"by": "process:nightly", "at": "x"},
                                       {"by": "human:adamson", "at": "x"}]}),
            "human-reviewed")

    def test_bare_mapping_is_a_one_element_list(self):
        # §5.2 requires a consumer to read this form; it is not a convenience.
        self.assertEqual(
            K.trust_tier({"verified": {"by": "human:adamson", "at": "x"}}),
            "human-reviewed")


class TestV02Families(unittest.TestCase):
    def findings(self, front):
        out = []
        K._check_v02_families("t.md", front, out)
        return {(f.check, f.severity) for f in out}

    def test_clean_v02_frontmatter_is_silent(self):
        self.assertEqual(self.findings({
            "generated": {"by": "enrichment_agent/claude-opus-5", "at": "2026-01-01"},
            "verified": {"by": "human:adamson", "at": "2026-01-01"},
            "status": "stable", "stale_after": "2026-12-10"}), set())

    def test_bare_name_is_not_an_actor(self):
        self.assertIn(("V14", K.ERROR),
                      self.findings({"generated": {"by": "Walter", "at": "x"}}))

    def test_generated_without_by_fails(self):
        self.assertIn(("V14", K.ERROR), self.findings({"generated": {"at": "x"}}))

    def test_generated_as_a_scalar_fails(self):
        self.assertIn(("V14", K.ERROR), self.findings({"generated": "2026-01-01"}))

    def test_verified_actor_is_checked_too(self):
        self.assertIn(("V14", K.ERROR),
                      self.findings({"verified": [{"by": "someone", "at": "x"}]}))

    def test_unknown_status_fails(self):
        self.assertIn(("V15", K.ERROR), self.findings({"status": "published"}))

    def test_each_valid_status_passes(self):
        for status in ("draft", "stable", "deprecated"):
            self.assertEqual(self.findings({"status": status}), set())

    def test_stale_after_must_be_a_plain_date(self):
        self.assertIn(("V15", K.ERROR), self.findings({"stale_after": "Dec 2026"}))

    def test_legacy_timestamp_warns_but_does_not_fail(self):
        self.assertEqual(self.findings({"timestamp": "2026-01-01"}),
                         {("V16", K.WARNING)})

    def test_generated_silences_the_legacy_warning(self):
        self.assertEqual(self.findings({
            "timestamp": "2026-01-01",
            "generated": {"by": "human:adamson", "at": "2026-01-01"}}), set())


class TestCellParsing(unittest.TestCase):
    def test_path_globs_pulls_every_path_from_a_prose_cell(self):
        cell = ("`scenarios/scenario-*.md` (one row per file); "
                "`enforcement-timeline/penalties.md` + `x.md` (penalties table)")
        self.assertEqual(K._path_globs(cell),
                         ["scenarios/scenario-*.md",
                          "enforcement-timeline/penalties.md", "x.md"])

    def test_ident_strips_backticks(self):
        self.assertEqual(K._ident("`scenario-decision-map`"), "scenario-decision-map")

    def test_listy_treats_dash_as_empty(self):
        self.assertEqual(K._listy("—"), [])
        self.assertEqual(K._listy("`resource`, `id`"), ["resource", "id"])

    def test_tables_keyed_by_header_not_position(self):
        tables = K.parse_tables("# H\n\n| B | A |\n|---|---|\n| 2 | 1 |\n")
        self.assertEqual(tables["H"], [{"B": "2", "A": "1"}])


class TestProcessContract(BundleFixture):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, SCRIPT, self.root, *args],
                              capture_output=True, text=True)

    def test_clean_bundle_exits_zero(self):
        self.assertEqual(self.run_cli("--quiet").returncode, 0)

    def test_error_exits_one(self):
        self.write("broken.md", "# no frontmatter\n")
        self.assertEqual(self.run_cli("--quiet").returncode, 1)

    def test_warning_alone_still_exits_zero(self):
        self.write("a-thing.md", CONCEPT.replace("tags: [system]", "tags: [invented]"))
        self.assertEqual(self.run_cli("--quiet").returncode, 0)

    def test_missing_directory_exits_two(self):
        result = subprocess.run([sys.executable, SCRIPT, os.path.join(self.root, "nope")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

    def test_json_output_is_parseable(self):
        import json
        result = self.run_cli("--json", "--quiet")
        payload = json.loads(result.stdout)
        self.assertIn("findings", payload)
        self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()
