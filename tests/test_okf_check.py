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

| Contract ID | Deliverable file | Source scope | Identity key | Severity |
|---|---|---|---|---|
| *(none at bundle initialisation)* | — | — | — | — |

**Worked example** (illustrative only — not a live contract):

| Contract ID | Deliverable file | Source scope | Identity key | Severity |
|---|---|---|---|---|
| `made-up` | `deliverables/nope.html` | `scenarios/scenario-*.md` (one per file) | letter | ERROR |

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
