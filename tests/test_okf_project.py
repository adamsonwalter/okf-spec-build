#!/usr/bin/env python3
"""Tests for scripts/okf_project.py — the bundle-agnostic projection builder.

The point of promoting this into the kit was that it works on a bundle it has
never seen. These build synthetic bundles in a temp directory and assert on the
output, rather than depending on any particular corpus.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "okf_project.py")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import okf_project as P  # noqa: E402


ONTOLOGY = """\
---
type: Ontology
title: Widget Registry
description: Registry.
memory_tier: semantic
confidence: 1.0
confidence_sources: 0
timestamp: 2026-08-09T00:00:00Z
tags: [ontology, system, governance]
---

# Type Registry

| Type | Description | Typical Body Sections |
|---|---|---|
| `Concept` | An idea. | Schema |
| `Ontology` | This file. | — |

# Relationship Taxonomy

| Relationship | Direction | Prose signal | Example |
|---|---|---|---|
| `depends-on` | A → B | "requires" | A depends on B |

# Tag Taxonomy

| Tag | Meaning |
|---|---|
| `system` | Infrastructure |
| `widget` | Widgets |

# Validation Rules

| Rule | Check | Severity |
|---|---|---|
| V1 | Every concept's `type` is registered | ERROR |

# Deprecated Types

| Deprecated Type | Note |
|---|---|
| `Gadget` | Replaced by Widget |

# Ontology Version History

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-01 | Initial |
| 0.2 | 2026-08-09 | Added widget tag |
"""

LOG = """\
# Bundle Update Log

## 2026-08-09

* **Kit**: tooling only.

## 2026-08-05

* **Creation**: a concept was written.
"""


def concept(title, tags="[system]", body="Body.", related=""):
    return f"""\
---
type: Concept
title: {title}
description: About {title}.
resource: https://example.org/{title.lower().replace(' ', '-')}
confidence: 0.9
tags: {tags}
timestamp: 2026-08-09T00:00:00Z
---

# {title}

{body}

# Related

{related}

# Citations

- A source: https://example.org/source
"""


class ProjectionFixture(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.write("ontology.md", ONTOLOGY)
        self.write("log.md", LOG)
        self.write("alpha.md", concept("Alpha Thing"))
        self.write("beta.md", concept("Beta Thing", tags="[system, widget]"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def build(self, *args):
        return subprocess.run([sys.executable, SCRIPT, self.root, "--quiet", *args],
                              capture_output=True, text=True)

    def master_json(self, slug):
        with open(os.path.join(self.root, "projections", f"{slug}-master.json")) as handle:
            return json.load(handle)


class TestWorksWithNoConfiguration(ProjectionFixture):
    """A bundle the builder has never seen must still produce projections."""

    def test_builds_with_defaults_from_the_directory(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        slug = os.path.basename(self.root)
        payload = self.master_json(slug)
        self.assertEqual(payload["conceptCount"], 2)
        self.assertEqual(payload["schema"], f"{slug}/concepts")

    def test_title_defaults_to_the_ontology_title(self):
        self.build()
        slug = os.path.basename(self.root)
        with open(os.path.join(self.root, "projections", f"{slug}-master.md")) as handle:
            self.assertIn("# Widget Registry — Knowledge Projection", handle.read())

    def test_no_tag_slices_by_default(self):
        self.build()
        self.assertFalse(os.path.exists(os.path.join(self.root, "projections", "by-tag")))


class TestDeclaredConfiguration(ProjectionFixture):
    def _configure(self):
        self.write("ontology.md", ONTOLOGY + """
# Projection

| Setting | Value |
|---|---|
| `Bundle slug` | `widgets` |
| `Bundle title` | The Widget Corpus |
| `Schema id` | `widgets/concepts` |
| `Tag slices` | `widget` |
""")

    def test_slug_title_schema_and_slices_are_read_from_the_registry(self):
        self._configure()
        self.assertEqual(self.build().returncode, 0)
        payload = self.master_json("widgets")
        self.assertEqual(payload["schema"], "widgets/concepts")
        slice_path = os.path.join(self.root, "projections", "by-tag", "widget.md")
        self.assertTrue(os.path.exists(slice_path))
        with open(slice_path) as handle:
            text = handle.read()
        self.assertIn("The Widget Corpus", text)
        self.assertIn("Beta Thing", text)
        self.assertNotIn("## Alpha Thing", text)   # not tagged widget


class TestStructuredOutput(ProjectionFixture):
    def test_concept_fields_are_carried_typed(self):
        self.build()
        payload = self.master_json(os.path.basename(self.root))
        alpha = next(c for c in payload["concepts"] if c["title"] == "Alpha Thing")
        self.assertEqual(alpha["type"], "Concept")
        self.assertEqual(alpha["confidence"], 0.9)
        self.assertEqual(alpha["tags"], ["system"])
        self.assertEqual(alpha["sourcePath"], "alpha.md")
        self.assertEqual(alpha["citations"][0]["url"], "https://example.org/source")

    def test_ontology_registries_travel_as_data(self):
        self.build()
        ontology = self.master_json(os.path.basename(self.root))["ontology"]
        self.assertEqual({t["name"] for t in ontology["types"]}, {"Concept", "Ontology"})
        self.assertEqual(ontology["version"], "0.2")   # newest dated row, not the first

    def test_graph_ships_with_the_knowledge(self):
        self.write("alpha.md", concept(
            "Alpha Thing", related="- Rests on [Beta](beta.md) — **depends-on**."))
        self.build()
        payload = self.master_json(os.path.basename(self.root))
        self.assertEqual(payload["edgeCount"], 1)
        self.assertEqual(payload["edges"][0]["relationship"], "depends-on")
        self.assertEqual(payload["edges"][0]["target"], "beta.md")

    def test_absent_graph_is_reported_not_silently_empty(self):
        # An application must be able to tell "no graph shipped" from "no
        # relationships exist".
        edges, note = P.read_edges(P.Path(self.root))
        self.assertIsNotNone(edges)      # available here
        self.assertIsNone(note)


class TestLogSemantics(ProjectionFixture):
    def test_kit_only_dates_do_not_move_the_corpus_version(self):
        self.build()
        payload = self.master_json(os.path.basename(self.root))
        self.assertEqual(payload["logHead"], "2026-08-05")        # newest content entry
        self.assertEqual(payload["logHeadAnyEntry"], "2026-08-09")  # newest of any kind

    def test_missing_log_does_not_break_the_build(self):
        os.remove(os.path.join(self.root, "log.md"))
        self.assertEqual(self.build().returncode, 0)


class TestFailsLoudly(ProjectionFixture):
    def test_empty_registry_section_stops_the_build(self):
        # An empty registry is indistinguishable from a permissive one.
        self.write("ontology.md", ONTOLOGY.replace(
            "| `depends-on` | A → B | \"requires\" | A depends on B |", ""))
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("yielded no rows", result.stdout + result.stderr)

    def test_not_a_bundle_exits_two(self):
        os.remove(os.path.join(self.root, "ontology.md"))
        self.assertEqual(self.build().returncode, 2)

    def test_excluded_trees_are_not_projected(self):
        self.write("inbox/raw.md", concept("Raw Input"))
        self.write("archive/old.md", concept("Old Thing"))
        self.build()
        titles = {c["title"] for c in self.master_json(os.path.basename(self.root))["concepts"]}
        self.assertNotIn("Raw Input", titles)
        self.assertNotIn("Old Thing", titles)


if __name__ == "__main__":
    unittest.main()
