#!/usr/bin/env python3
"""Tests for scripts/okf_graph.py — relationship extraction, V10 and V11."""

import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import okf_check as K  # noqa: E402
import okf_graph as G  # noqa: E402

ONTOLOGY = """\
---
type: Ontology
title: Bundle Ontology
description: Registry.
memory_tier: semantic
confidence: 1.0
confidence_sources: 0
timestamp: 2026-08-09T00:00:00Z
tags: [ontology, system, governance]
---

# Type Registry

| Type | Description | Typical Body Sections | Required Sections | Required Fields |
|---|---|---|---|---|
| `Concept` | An idea. | Schema | — | — |
| `Ontology` | This file. | — | — | — |

# Relationship Taxonomy

| Relationship | Direction | Prose signal | Example |
|---|---|---|---|
| `depends-on` | A → B | "requires" | A depends on B |
| `references` | A → B | "see" | A references B |
| `supersedes` | A → B | "replaces" | A supersedes B |
| `part-of` | A → B | "component of" | A is part of B |
| `derived-from` | A → B | "based on" | A derived from B |

# Tag Taxonomy

| Tag | Meaning |
|---|---|
| `system` | Infrastructure |
| `ontology` | Registry |
| `governance` | Rules |
"""

LOG = "# Bundle Update Log\n\n## 2026-08-09\n\n* **Kit**: x\n"


def concept(title="A Thing", related="", extra=""):
    return f"""\
---
type: Concept
title: {title}
description: A thing.
timestamp: 2026-08-09T00:00:00Z
tags: [system]
{extra}---

# {title}

Body text.

# Related

{related}
"""


class GraphFixture(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.write("ontology.md", ONTOLOGY)
        self.write("log.md", LOG)
        self.write("target.md", concept("Target"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def extract(self):
        return G.extract_edges(K.Bundle(self.root))

    def edges_from(self, related):
        self.write("source.md", concept("Source", related))
        return self.extract()

    def full_check(self):
        return K.run_checks(K.Bundle(self.root))[0]


class TestExtraction(GraphFixture):
    def test_marked_bullet_becomes_an_edge(self):
        edges, _ = self.edges_from("- Anchored by [Target](target.md) — **depends-on**.")
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].relationship, "depends-on")
        self.assertEqual(edges[0].target, "target.md")
        self.assertEqual(edges[0].source, "source.md")

    def test_wrapped_bullet_still_parses(self):
        # Worth 18 edges in the reference bundle. The marker is on line two.
        edges, _ = self.edges_from(
            "- The substantive rights and their timeframes are [Target](target.md)\n"
            "  — **references**.")
        self.assertEqual([e.relationship for e in edges], ["references"])

    def test_one_bullet_many_links_makes_many_edges(self):
        self.write("second.md", concept("Second"))
        edges, _ = self.edges_from(
            "- Milestones: [Target](target.md), [Second](second.md) — **references**.")
        self.assertEqual(sorted(e.target for e in edges), ["second.md", "target.md"])
        self.assertTrue(all(e.relationship == "references" for e in edges))

    def test_external_links_are_not_edges(self):
        edges, findings = self.edges_from(
            "- See [the Act](https://example.org/act) — **references**.")
        self.assertEqual(edges, [])
        self.assertIn("V-GRAPH", [f.check for f in findings if f.severity == K.WARNING])

    def test_unregistered_inverse_is_an_error(self):
        _, findings = self.edges_from("- Used by [Target](target.md) — **referenced-by**.")
        errors = [f for f in findings if f.severity == K.ERROR]
        # Two errors is correct: the unregistered inverse, and the zero-edge
        # guard, since a linked bullet was present and produced nothing.
        self.assertTrue(any("directional" in f.message for f in errors), errors)

    def test_past_tense_inverse_is_an_error(self):
        _, findings = self.edges_from("- Amended by [Target](target.md) — **superseded** wording.")
        self.assertTrue(any(f.severity == K.ERROR for f in findings))

    def test_two_relationships_in_one_bullet_is_an_error(self):
        _, findings = self.edges_from(
            "- [Target](target.md) — **depends-on** and **references**.")
        errors = [f for f in findings if f.severity == K.ERROR]
        self.assertTrue(errors)
        self.assertIn("one bullet carries one", errors[0].message)

    def test_link_without_marker_is_allowed_and_counted(self):
        edges, findings = self.edges_from("- Sits outside this ladder — see [Target](target.md).")
        self.assertEqual(edges, [])
        warned = [f for f in findings if f.severity == K.WARNING and "no relationship marker" in f.message]
        self.assertEqual(len(warned), 1)

    def test_marker_without_link_warns(self):
        edges, findings = self.edges_from("- Governs the whole area — **depends-on**.")
        self.assertEqual(edges, [])
        self.assertTrue(any("needs a target" in f.message for f in findings))


class TestZeroEdgeGuard(GraphFixture):
    def test_links_present_but_no_edges_is_an_error(self):
        # Something to extract from, and nothing extracted: either every bullet
        # is an unmarked cross-reference, or the extractor is broken.
        self.write("source.md", concept("Source", "- See [Target](target.md)."))
        _, findings = self.extract()
        errors = [f for f in findings if f.severity == K.ERROR]
        self.assertTrue(errors)
        self.assertIn("extractor is broken", errors[0].message)

    def test_no_linked_related_bullets_is_a_skip_not_an_error(self):
        # A seed bundle genuinely has no graph. Failing it on clone would get
        # this check switched off.
        _, findings = self.extract()
        self.assertFalse([f for f in findings if f.severity == K.ERROR])
        self.assertTrue(any(f.severity == K.SKIP for f in findings))


class TestGraphChecks(GraphFixture):
    def test_v10_edge_into_an_index_is_named_as_such(self):
        self.write("sub/index.md", "# Sub index\n")
        self.write("source.md", concept("Source", "- [Sub](sub/index.md) — **references**."))
        findings = self.full_check()
        v10 = [f for f in findings if f.check == "V10"]
        self.assertEqual(len(v10), 1)
        self.assertIn("is an index, not a concept", v10[0].message)

    def test_v10_edge_to_a_missing_file(self):
        self.write("source.md", concept("Source", "- [Gone](gone.md) — **references**."))
        findings = self.full_check()
        self.assertTrue(any(f.check == "V10" for f in findings))

    def test_v11_edge_into_archive(self):
        self.write("archive/old.md", concept("Old"))
        self.write("source.md", concept("Source", "- [Old](archive/old.md) — **references**."))
        findings = self.full_check()
        v11 = [f for f in findings if f.check == "V11"]
        self.assertEqual(len(v11), 1)
        self.assertIn("archived or superseded", v11[0].message)

    def test_v11_edge_into_a_superseded_concept(self):
        self.write("old.md", concept("Old", extra="superseded_by: target\nsupersedes: nothing\n"))
        self.write("source.md", concept("Source", "- [Old](old.md) — **references**."))
        findings = self.full_check()
        self.assertTrue(any(f.check == "V11" for f in findings))

    def test_live_edge_passes_both(self):
        self.write("source.md", concept("Source", "- [Target](target.md) — **depends-on**."))
        findings = self.full_check()
        self.assertFalse([f for f in findings if f.check in ("V10", "V11")])


class TestTaxonomyIsReadFromOntology(GraphFixture):
    def test_relationship_registered_only_in_ontology_is_accepted(self):
        self.write("ontology.md", ONTOLOGY.replace(
            "| `supersedes` | A → B | \"replaces\" | A supersedes B |",
            "| `supersedes` | A → B | \"replaces\" | A supersedes B |\n"
            "| `governs` | A → B | \"governs\" | A governs B |"))
        edges, _ = self.edges_from("- [Target](target.md) — **governs**.")
        self.assertEqual([e.relationship for e in edges], ["governs"])

    def test_relationship_absent_from_ontology_is_rejected(self):
        _, findings = self.edges_from("- [Target](target.md) — **authored-by**.")
        self.assertTrue(any(f.severity == K.ERROR for f in findings))


if __name__ == "__main__":
    unittest.main()


class TestAuthorityPosture(GraphFixture):
    """V13 — authority must not rest on context (docs/DECISIONS.md, ontology v0.9)."""

    POSTURE = """
# Authority Posture

| Scope | Posture | Note |
|---|---|---|
| `law/` | authoritative | The provisions. |
| `context/` | supporting | Helpful, not complete. |
| `sources/` | provenance | What it rests on. |
"""

    def _bundle(self, source_dir, target_dir, relationship):
        self.write("ontology.md", ONTOLOGY + self.POSTURE)
        self.write(f"{target_dir}/target.md", concept("Target"))
        self.write(f"{source_dir}/source.md", concept(
            "Source", f"- Rests on [Target](../{target_dir}/target.md) — **{relationship}**."))
        return K.run_checks(K.Bundle(self.root))[0]

    def test_authoritative_resting_on_supporting_warns(self):
        findings = self._bundle("law", "context", "depends-on")
        v13 = [f for f in findings if f.check == "V13"]
        self.assertEqual(len(v13), 1)
        self.assertEqual(v13[0].severity, K.WARNING)
        self.assertIn("rests on supporting", v13[0].message)

    def test_part_of_and_derived_from_are_load_bearing_too(self):
        for relationship in ("part-of", "derived-from"):
            with self.subTest(relationship=relationship):
                self.setUp()
                findings = self._bundle("law", "context", relationship)
                self.assertTrue([f for f in findings if f.check == "V13"])

    def test_references_is_not_load_bearing(self):
        # Citing context is fine; resting on it is not.
        findings = self._bundle("law", "context", "references")
        self.assertFalse([f for f in findings if f.check == "V13"])

    def test_provenance_is_exempt(self):
        # Resting on a source document is what provenance is for.
        findings = self._bundle("law", "sources", "derived-from")
        self.assertFalse([f for f in findings if f.check == "V13"])

    def test_supporting_resting_on_supporting_is_fine(self):
        findings = self._bundle("context", "context", "depends-on")
        self.assertFalse([f for f in findings if f.check == "V13"])

    def test_undeclared_paths_default_to_supporting(self):
        # Understating authority is safe; overstating it is not.
        self.write("ontology.md", ONTOLOGY + self.POSTURE)
        self.assertEqual(K.posture_of("nowhere/thing.md", [("law/", "authoritative")]),
                         K.DEFAULT_POSTURE)

    def test_longest_matching_scope_wins(self):
        postures = [("law/", "authoritative"), ("law/draft/", "illustrative")]
        self.assertEqual(K.posture_of("law/x.md", postures), "authoritative")
        self.assertEqual(K.posture_of("law/draft/x.md", postures), "illustrative")

    def test_no_declaration_reports_skip_not_silence(self):
        findings = self.full_check()
        skips = [f for f in findings if f.check == "V13" and f.severity == K.SKIP]
        self.assertTrue(skips)

    def test_unknown_posture_is_an_error(self):
        self.write("ontology.md", ONTOLOGY + self.POSTURE.replace(
            "| `law/` | authoritative |", "| `law/` | pretty-solid |"))
        findings = K.run_checks(K.Bundle(self.root))[0]
        self.assertTrue([f for f in findings
                         if f.check == "ONTOLOGY" and f.severity == K.ERROR])
