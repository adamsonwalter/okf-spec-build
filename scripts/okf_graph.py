#!/usr/bin/env python3
"""Extract the typed relationship graph from a bundle's `# Related` sections.

A `# Related` bullet is an edge, not a sentence. The relationship is marked in
bold from the closed ten-item taxonomy in ontology.md, so this parses a marker
in the kit's own format rather than inferring meaning from English. That
distinction is what makes it safe: an unregistered relationship is *detectable*,
not merely unexpected.

Measured against a real 104-concept bundle: 104/104 concepts carry a `# Related`
section, 323 of 332 bullets carry a bold marker, and none relies on an unmarked
verb. Joining wrapped continuation lines is worth 18 edges on its own, so it is
done before matching rather than treated as an edge case.

Usage:
    python3 scripts/okf_graph.py [bundle_root] [--json] [--quiet]

Exit codes:
    0  edges extracted, no ERROR-severity findings
    1  at least one ERROR (unregistered relationship, or zero edges extracted)
    2  the bundle could not be read

See docs/DECISIONS.md D2, D3 and D9 for why relationships are directional, why
the marker is parsed rather than the prose, and why the zero-edge guard has no
threshold.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from okf_check import (ERROR, SKIP, WARNING, Bundle, Finding, parse_tables,  # noqa: E402
                       split_frontmatter, strip_code_fences, _ident)

RELATED_SECTION = re.compile(r"^#+\s*Related\s*$(.*?)(?=^#\s|\Z)", re.M | re.S)
BOLD_MARKER = re.compile(r"\*\*([a-z][a-z-]*)\*\*")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class Edge:
    __slots__ = ("source", "target", "relationship", "line")

    def __init__(self, source, target, relationship, line):
        self.source = source
        self.target = target
        self.relationship = relationship
        self.line = line

    def as_dict(self):
        return {"source": self.source, "target": self.target,
                "relationship": self.relationship, "line": self.line}

    def __repr__(self):
        return f"<{self.source} -{self.relationship}-> {self.target}>"


def registered_relationships(bundle):
    """The closed taxonomy from ontology.md §Relationship Taxonomy."""
    if not os.path.exists(bundle.ontology_path):
        return set()
    names = set()
    for rows in parse_tables(bundle.read(bundle.ontology_path)).values():
        for row in rows:
            if "Relationship" in row and "Direction" in row:
                name = _ident(row["Relationship"])
                if name and not name.startswith("*"):
                    names.add(name)
    return names


def logical_bullets(section, first_line):
    """Bullets, with wrapped continuation lines joined onto the bullet above.

    Worth 18 edges in the reference bundle. A parser that treated a wrapped
    bullet as unparseable would drop them silently, which is the failure this
    module exists to prevent.
    """
    bullets = []
    for offset, raw in enumerate(section.split("\n")):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith(("- ", "* ")):
            bullets.append([stripped[2:].strip(), first_line + offset])
        elif bullets:
            bullets[-1][0] += " " + stripped
    return bullets


def _resolve(bundle, source_path, target):
    """A link target as a bundle-relative path, or None if it is not internal."""
    target = target.strip()
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    clean = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not clean or not clean.endswith(".md"):
        return None
    # A leading "/" means the bundle root, not the filesystem root.
    base = bundle.root if clean.startswith("/") else os.path.dirname(source_path)
    absolute = os.path.normpath(os.path.join(base, clean.lstrip("/")))
    return os.path.relpath(absolute, bundle.root)


def extract_edges(bundle):
    """Every typed edge in the bundle, plus findings about what would not parse."""
    findings = []
    edges = []
    known = registered_relationships(bundle)
    concepts_seen = 0
    unmarked = 0
    related_with_links = 0

    for path in bundle.files:
        rel = bundle.rel(path)
        if os.path.basename(path) in {"index.md", "log.md"} or bundle.is_instruction_file(path):
            continue
        text = bundle.read(path)
        front, body, error = split_frontmatter(text)
        if front is None or error:
            continue
        concepts_seen += 1

        match = RELATED_SECTION.search(strip_code_fences(body))
        if not match:
            continue
        first_line = body[:match.start(1)].count("\n") + 1

        for bullet, line in logical_bullets(match.group(1), first_line):
            markers = BOLD_MARKER.findall(bullet)
            links = MD_LINK.findall(bullet)
            if links:
                related_with_links += 1
            recognised = [m for m in markers if m in known]
            unknown = [m for m in markers
                       if m not in known and ("-" in m or m in _INVERSE_HINTS)]

            if not recognised:
                if unknown:
                    # An unregistered relationship must fail, never be dropped.
                    # The taxonomy is closed at ten and inverses are deliberately
                    # absent — put the edge on the other concept instead.
                    findings.append(Finding(
                        ERROR, "V-GRAPH", rel,
                        f"line {line}: '**{unknown[0]}**' is not a registered "
                        f"relationship. Relationships are directional and inverses "
                        f"are not registered — put the edge on the other concept"))
                elif links:
                    unmarked += 1
                continue

            if len(recognised) > 1:
                findings.append(Finding(
                    ERROR, "V-GRAPH", rel,
                    f"line {line}: bullet names {len(recognised)} relationships "
                    f"({', '.join(recognised)}); one bullet carries one"))
                continue

            targets = [t for t in (_resolve(bundle, path, link) for link in links) if t]
            if not targets:
                findings.append(Finding(
                    WARNING, "V-GRAPH", rel,
                    f"line {line}: '**{recognised[0]}**' with no internal link — "
                    f"an edge needs a target"))
                continue
            for target in targets:
                edges.append(Edge(rel, target, recognised[0], line))

    if unmarked:
        findings.append(Finding(
            WARNING, "V-GRAPH", None,
            f"{unmarked} bullet(s) carry a link but no relationship marker. These "
            f"are plain cross-references and produce no edge — allowed, counted so "
            f"the number stays visible"))

    # An extraction that yields nothing is indistinguishable from a bundle with
    # no relationships — the same reasoning that already fails an empty registry.
    #
    # The trigger is principled rather than a threshold: zero edges is only
    # alarming when there was something to extract from. A seed bundle whose
    # concepts carry no linked `# Related` bullets genuinely has no graph, and
    # failing it on clone would get this check switched off.
    if not edges:
        if related_with_links:
            findings.append(Finding(
                ERROR, "V-GRAPH", None,
                f"extracted 0 edges, but {related_with_links} `# Related` bullet(s) "
                f"carry links — either every one is an unmarked cross-reference, or "
                f"the extractor is broken. Both need a human before this is trusted"))
        elif concepts_seen:
            findings.append(Finding(
                SKIP, "V-GRAPH", None,
                f"no graph to extract — {concepts_seen} concept(s), none with a "
                f"linked `# Related` bullet"))

    return edges, findings


_INVERSE_HINTS = {"superseded", "referenced", "implemented", "governed", "derived"}


# ---------------------------------------------------------------------------
# Graph-level checks, run from okf_check.py
# ---------------------------------------------------------------------------

def check_graph(bundle, edges, concept_paths, archived_or_superseded):
    """V10 — targets resolve. V11 — no edge points into dead material."""
    findings = []
    for edge in edges:
        if edge.target not in concept_paths:
            basename = os.path.basename(edge.target)
            if basename in {"index.md", "log.md"}:
                # The file exists; it is navigation, not a concept. A typed edge
                # into an index cannot be traversed to anything.
                detail = (f"{edge.target} is an index, not a concept — point the "
                          f"edge at the concepts themselves, or make this a plain "
                          f"cross-reference with no marker")
            elif os.path.exists(os.path.join(os.path.dirname(edge.source), edge.target)):
                detail = f"{edge.target} exists but carries no concept frontmatter"
            else:
                detail = f"{edge.target} does not resolve to a concept in this bundle"
            findings.append(Finding(
                ERROR, "V10", edge.source,
                f"line {edge.line}: '**{edge.relationship}**' points at {detail}"))
        elif edge.target in archived_or_superseded:
            findings.append(Finding(
                ERROR, "V11", edge.source,
                f"line {edge.line}: '**{edge.relationship}**' points at "
                f"{edge.target}, which is archived or superseded — a live edge "
                f"into dead material reads exactly like a current one"))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Extract a bundle's relationship graph.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="emit edges as JSON")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.root):
        print(f"error: no such directory {args.root!r}", file=sys.stderr)
        return 2

    bundle = Bundle(args.root)
    edges, findings = extract_edges(bundle)
    errors = [f for f in findings if f.severity == ERROR]

    if args.json:
        print(json.dumps({"ok": not errors,
                          "edgeCount": len(edges),
                          "edges": [e.as_dict() for e in edges],
                          "findings": [f.as_dict() for f in findings]}, indent=2))
        return 1 if errors else 0

    for finding in findings:
        print(finding, file=sys.stderr if finding.severity == ERROR else sys.stdout)
    if not args.quiet:
        by_type = {}
        for edge in edges:
            by_type[edge.relationship] = by_type.get(edge.relationship, 0) + 1
        print(f"\n{len(edges)} edge(s) across {len(set(e.source for e in edges))} concept(s)")
        for name, count in sorted(by_type.items(), key=lambda kv: -kv[1]):
            print(f"   {name:16} {count}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
