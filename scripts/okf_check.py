#!/usr/bin/env python3
"""OKF bundle conformance checker.

Runs the checks AGENTS.MD §CONFORMANCE_AGENT describes, in code, and exits
non-zero on failure. Every one of CHECK_1..CHECK_9 is mechanically decidable —
frontmatter parses, dates sort, links resolve, a Status column has no "Not yet
checked" — so none of them needs an agent's judgment.

The point is not that an agent audits badly. It is that an agent-run check that
reports PASS and a check that was never run are indistinguishable afterwards.

Usage:
    python3 scripts/okf_check.py [bundle_root] [--json] [--quiet]

Exit codes:
    0  no ERROR-severity failures (warnings may still be printed)
    1  at least one ERROR
    2  the bundle could not be read at all

Stdlib only. Works on this kit and on any bundle generated from it.

Design decisions behind these checks — what was rejected and why, with the
measurements that drove each one — are recorded in docs/DECISIONS.md. Read it
before changing a severity, relaxing a guard, or adding a rule.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

ERROR, WARNING, SKIP = "ERROR", "WARNING", "SKIP"

RESERVED_NAMES = {"index.md", "log.md"}
POSTURES = {"authoritative", "supporting", "provenance", "illustrative"}
# Understating authority is safe; overstating it is not.
DEFAULT_POSTURE = "supporting"
# Authority may rest on provenance — that is what provenance is for.
WEAK_POSTURES = {"supporting", "illustrative"}
LOAD_BEARING = {"depends-on", "part-of", "derived-from"}
# Generated or non-concept trees. projections/ is rebuilt from the concepts, so
# checking it would double-report every finding against a derived copy.
EXCLUDED_DIRS = {".git", "projections", "node_modules", "__pycache__", ".venv",
                 "templates",      # seeds for reserved files, not concepts
                 "inbox",          # raw source documents awaiting ingestion
                 ".ai_context",    # agent scratch, not concepts
                 "deliverables"}   # hand-authored artifacts, not concepts

ISO_DATE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
NONE_MARKERS = {"", "—", "-", "–", "n/a", "none", "*(none)*"}


class Finding:
    def __init__(self, severity, check, path, message):
        self.severity, self.check, self.path, self.message = severity, check, path, message

    def as_dict(self):
        return {"severity": self.severity, "check": self.check,
                "file": self.path, "message": self.message}

    def __str__(self):
        return f"{self.severity:7} {self.check:9} {self.path or '-'}\n          {self.message}"


# ---------------------------------------------------------------------------
# Parsing. Small and strict: anything not understood is reported, never skipped.
# ---------------------------------------------------------------------------

def split_frontmatter(text):
    """Return (frontmatter_dict_or_None, body, error_or_None).

    Handles the nesting OKF v0.2 needs: `sources` is a list of mappings (§5.1)
    and `verified` is a list of `{by, at}` events (§5.2). The previous parser was
    flat, so a block sequence turned into junk keys (`- { by`) with no error —
    silent misreading, which is the one thing this parser promises not to do.
    """
    if not text.startswith("---"):
        return None, text, None                      # no frontmatter at all
    end = text.find("\n---", 3)
    if end == -1:
        return None, text, "frontmatter block is never closed"
    raw = text[3:end].strip("\n")
    body = text[end + 4:]

    lines = []
    for lineno, line in enumerate(raw.split("\n"), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        lines.append((len(line) - len(line.lstrip(" ")), line.strip(), lineno))

    try:
        data, consumed = _parse_block(lines, 0, lines[0][0] if lines else 0)
    except _FrontmatterError as exc:
        return None, body, str(exc)
    if consumed != len(lines):
        return None, body, (f"frontmatter line {lines[consumed][2]} has unexpected "
                            f"indentation: {lines[consumed][1]!r}")
    return data, body, None


class _FrontmatterError(Exception):
    pass


def _parse_block(lines, i, indent):
    """Parse a mapping or sequence at `indent`. Returns (value, next_index)."""
    if i < len(lines) and lines[i][1].startswith("- "):
        items = []
        while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
            items.append(_scalar(lines[i][1][2:].strip()))
            i += 1
            # A deeper block under a `- ` item is not something this dialect
            # writes; refuse it rather than drop it.
            if i < len(lines) and lines[i][0] > indent:
                raise _FrontmatterError(
                    f"frontmatter line {lines[i][2]} nests under a list item, which "
                    f"this parser does not read: {lines[i][1]!r}")
        return items, i

    data = {}
    while i < len(lines) and lines[i][0] == indent:
        _, content, lineno = lines[i]
        if ":" not in content:
            raise _FrontmatterError(
                f"frontmatter line {lineno} is not 'key: value': {content!r}")
        key, _, value = content.partition(":")
        key, value = key.strip(), value.strip()
        i += 1
        if value:
            data[key] = _scalar(value)
            continue
        # Empty value: either a nested block below, or a genuinely empty scalar.
        if i < len(lines) and lines[i][0] > indent:
            data[key], i = _parse_block(lines, i, lines[i][0])
        else:
            data[key] = ""
    return data, i


def _scalar(value):
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1].strip()
        if not inner:
            return {}
        out = {}
        for part in _split_top_level(inner):
            k, sep, v = part.partition(":")
            if not sep:
                return value            # not a mapping we understand; keep raw
            out[k.strip()] = _scalar(v.strip())
        return out
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [_scalar(v.strip()) for v in _split_top_level(inner)] if inner else []
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d*\.\d+", value):
        return float(value)
    return value


def _split_top_level(text):
    """Split on commas that are not inside nested brackets or quotes."""
    parts, depth, quote, current = [], 0, None, []
    for ch in text:
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append("".join(current))
            current = []
            continue
        current.append(ch)
    if current:
        parts.append("".join(current))
    return [p.strip() for p in parts if p.strip()]


def parse_tables(text):
    """Every markdown table in the file, keyed by the heading above it.

    Rows are dicts keyed on the header cells, so a column added or reordered in
    ontology.md does not silently shift meaning the way positional parsing does.
    """
    tables = {}
    heading = None
    header = None
    illustrative = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            header = None
            illustrative = False
            continue
        # A declared marker, not inferred prose: everything from here to the next
        # heading is an illustration and must never be read as a live registry row.
        if stripped.startswith("**Worked example**"):
            illustrative = True
            header = None
            continue
        if illustrative:
            continue
        if not stripped.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if re.match(r"^\|[\s:|-]+\|?$", stripped):
            continue                                  # separator row
        if header is None:
            header = cells
            continue
        tables.setdefault(heading, []).append(dict(zip(header, cells)))
    return tables


BAND_GE = re.compile(r"^>=\s*([0-9.]+)$")
BAND_LE = re.compile(r"^<=\s*([0-9.]+)$")
BAND_RANGE = re.compile(r"^([0-9.]+)\s*[-–—]\s*([0-9.]+)$")


def parse_band(text):
    """A Certainty band cell as (low, high).

    None when the tag declares nothing. The string "malformed" when a band was
    written but cannot be read — an unreadable band must be reported, never
    treated as absent, or a typo silently switches the check off.
    """
    if not text:
        return None
    cleaned = text.strip().strip("`").strip()
    if not cleaned or cleaned.lower() in NONE_MARKERS:
        return None
    m = BAND_GE.match(cleaned)
    if m:
        return (float(m.group(1)), 1.0)
    m = BAND_LE.match(cleaned)
    if m:
        return (0.0, float(m.group(1)))
    m = BAND_RANGE.match(cleaned)
    if m:
        return (float(m.group(1)), float(m.group(2)))
    return "malformed"


def _listy(value):
    """A registry cell holding zero or more comma-separated names."""
    if value is None:
        return []
    cleaned = value.strip().strip("*")
    if cleaned.lower() in NONE_MARKERS:
        return []
    return [p.strip().strip("`") for p in cleaned.split(",") if p.strip()]


# ---------------------------------------------------------------------------
# Bundle model
# ---------------------------------------------------------------------------

class Bundle:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.files = []
        self.nested_bundles = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
            # A subtree carrying its own ontology.md is a bundle in its own right
            # and is governed by that registry, not this one. Checking its
            # concepts against the parent registry reports differences as defects.
            if dirpath != self.root and "ontology.md" in filenames:
                self.nested_bundles.append(dirpath)
                dirnames[:] = []
                continue
            for name in sorted(filenames):
                if name.endswith(".md"):
                    self.files.append(os.path.join(dirpath, name))
        self.ontology_path = os.path.join(self.root, "ontology.md")
        self.log_path = os.path.join(self.root, "log.md")

    def rel(self, path):
        return os.path.relpath(path, self.root)

    @staticmethod
    def is_instruction_file(path):
        """ALL CAPS .md files are agent instructions, not concepts."""
        stem = os.path.basename(path)[:-3]
        return stem.upper() == stem and any(c.isalpha() for c in stem)

    def read(self, path):
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()


def load_registries(bundle, findings):
    """Types, tags and rules from ontology.md, keyed by name."""
    registries = {"types": {}, "tags": set(), "bands": {}, "postures": [], "relationships": set(),
                  "rules": {}, "deliverable_contracts": [], "coverage_contracts": []}
    if not os.path.exists(bundle.ontology_path):
        findings.append(Finding(ERROR, "ONTOLOGY", "ontology.md",
                                "no ontology.md — nothing defines what a valid concept is"))
        return registries

    # A bundle inherits the kit's registries rather than copying them. A copy
    # drifts: privacy-act-okf held a copy of V1-V4 and V3 went missing from it,
    # and nobody noticed because nothing compared the two. Inheriting means a
    # bundle has no copy to drop a rule from.
    sources = []
    kit_ontology = os.path.join(bundle.root, "okf-kit", "ontology.md")
    if os.path.exists(kit_ontology):
        sources.append(bundle.read(kit_ontology))
    sources.append(bundle.read(bundle.ontology_path))

    tables = {}
    for text in sources:
        for heading, rows in parse_tables(text).items():
            tables.setdefault(heading, []).extend(rows)

    for heading, rows in tables.items():
        low = heading.lower()
        for row in rows:
            if "Type" in row and ("Description" in row or "Created By" in row):
                name = _ident(row["Type"])
                if name and not name.startswith("*"):
                    registries["types"][name] = {
                        "required_fields": _listy(row.get("Required Fields")),
                        "required_sections": _listy(row.get("Required Sections")),
                    }
            if "Tag" in row and "Meaning" in row:
                tag = _ident(row["Tag"])
                if tag and not tag.startswith("*"):
                    registries["tags"].add(tag)
                    band = parse_band(row.get("Certainty band"))
                    if band == "malformed":
                        findings.append(Finding(
                            ERROR, "ONTOLOGY", "ontology.md",
                            f"tag {tag!r} has an unreadable Certainty band "
                            f"{row.get('Certainty band')!r}; use '>= 0.80', "
                            f"'<= 0.95' or '0.60 - 0.90'"))
                    elif band:
                        registries["bands"][tag] = band
            if "Relationship" in row:
                registries["relationships"].add(_ident(row["Relationship"]))
            if "Rule" in row and "Check" in row:
                registries["rules"][_ident(row["Rule"])] = row.get("Severity", ERROR).strip()
            if "Scope" in row and "Posture" in row:
                scope = _ident(row["Scope"])
                posture = _ident(row["Posture"]).lower()
                if scope and not scope.startswith("*"):
                    if posture not in POSTURES:
                        findings.append(Finding(
                            ERROR, "ONTOLOGY", "ontology.md",
                            f"authority posture {posture!r} for scope {scope!r} is not one "
                            f"of {sorted(POSTURES)}"))
                    else:
                        registries["postures"].append((scope, posture))
            if "Contract ID" in row and "Deliverable file" in row:
                registries["deliverable_contracts"].append(row)
            if "Contract ID" in row and any(
                k.lower().startswith("coverage ledger") for k in row
            ):
                registries["coverage_contracts"].append(row)
    return registries


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def run_checks(bundle):
    findings = []
    registries = load_registries(bundle, findings)
    concepts = []

    for path in bundle.files:
        rel = bundle.rel(path)
        name = os.path.basename(path)
        text = bundle.read(path)
        front, body, error = split_frontmatter(text)

        if name in RESERVED_NAMES:
            if name == "index.md":
                # CHECK_3 — index.md carries no frontmatter, except okf_version at root.
                if front is not None:
                    allowed = rel == "index.md" and set(front) <= {"okf_version"}
                    if not allowed:
                        findings.append(Finding(ERROR, "CHECK_3", rel,
                                                "index.md contains a frontmatter block"))
            continue

        if bundle.is_instruction_file(path):
            continue                                   # ALL CAPS = instructions

        # CHECK_1 — parseable frontmatter.
        if error:
            findings.append(Finding(ERROR, "CHECK_1", rel, error))
            continue
        if front is None:
            findings.append(Finding(ERROR, "CHECK_1", rel,
                                    "concept document has no YAML frontmatter block"))
            continue

        # CHECK_2 — non-empty type.
        concept_type = str(front.get("type", "")).strip()
        if not concept_type:
            findings.append(Finding(ERROR, "CHECK_2", rel,
                                    "frontmatter has no non-empty 'type' field"))
            continue

        concepts.append((path, rel, front, body, concept_type))

    _check_types_and_fields(bundle, registries, concepts, findings)
    _check_links(bundle, concepts, findings)
    _check_log(bundle, findings)
    _check_supersession(bundle, concepts, findings)
    _check_coverage_contracts(bundle, registries, findings)
    _check_deliverable_contracts(bundle, registries, findings)
    _check_relationship_graph(bundle, concepts, findings)
    return findings, registries


def _check_relationship_graph(bundle, concepts, findings):
    """V10 / V11 — the typed edges in every `# Related` section.

    Imported lazily so okf_check.py still runs if okf_graph.py is absent, but
    a missing extractor is reported rather than passed over: a graph check that
    did not run must not read as a graph check that passed.
    """
    try:
        import okf_graph
    except ImportError as exc:
        findings.append(Finding(SKIP, "V10/V11", None,
                                f"relationship graph not checked — okf_graph.py "
                                f"unavailable ({exc})"))
        return

    edges, graph_findings = okf_graph.extract_edges(bundle)
    findings.extend(graph_findings)

    concept_paths = {rel for _, rel, _, _, _ in concepts}
    dead = set()
    for _, rel, front, _, _ in concepts:
        if rel.replace(os.sep, "/").startswith("archive/") or front.get("superseded_by"):
            dead.add(rel)
    findings.extend(okf_graph.check_graph(bundle, edges, concept_paths, dead))

    _check_authority_posture(bundle, edges, findings)


def posture_of(rel_path, postures):
    """The declared posture for a concept path, or the safe default.

    Longest matching scope wins, so a specific folder can override a broad one.
    """
    best, best_len = DEFAULT_POSTURE, -1
    normalised = rel_path.replace(os.sep, "/")
    for scope, posture in postures:
        scope_norm = scope.rstrip("/")
        if (normalised == scope_norm or normalised.startswith(scope_norm + "/")) \
                and len(scope_norm) > best_len:
            best, best_len = posture, len(scope_norm)
    return best


def _check_authority_posture(bundle, edges, findings):
    """V13 — authority must not rest on context.

    Invisible in prose, obvious in the graph: an authoritative concept that
    depends on supporting material is quietly borrowing weight it does not have.
    """
    registries = load_registries(bundle, [])
    postures = registries["postures"]
    if not postures:
        findings.append(Finding(SKIP, "V13", None,
                                "no Authority Posture declared — every concept defaults to "
                                f"{DEFAULT_POSTURE!r}, so nothing is checked"))
        return
    for edge in edges:
        if edge.relationship not in LOAD_BEARING:
            continue
        source_posture = posture_of(edge.source, postures)
        target_posture = posture_of(edge.target, postures)
        if source_posture == "authoritative" and target_posture in WEAK_POSTURES:
            findings.append(Finding(
                WARNING, "V13", edge.source,
                f"line {edge.line}: authoritative material rests on {target_posture} "
                f"material — '**{edge.relationship}**' to {edge.target}. Either the "
                f"target is more authoritative than declared, or this should be a "
                f"'references' edge rather than a load-bearing one"))


ACTOR = re.compile(r"^(?:human:\S+|process:\S+|[A-Za-z0-9._-]+/\S+)$")
STATUSES = {"draft", "stable", "deprecated"}
ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _verification_events(value):
    """`verified` as a list of events. A bare mapping is a one-element list.

    Spec §5.2 requires a consumer to read a bare `{by, at}` mapping as a
    one-element list, so this is the one shape normalisation the checker owes
    the format rather than a convenience.
    """
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return value
    return []


def trust_tier(front):
    """Derived trust tier, per spec §5.3. Derived on read, never stored."""
    events = _verification_events(front.get("verified"))
    if not events:
        return "unverified"
    for event in events:
        by = event.get("by") if isinstance(event, dict) else None
        if isinstance(by, str) and by.startswith("human:"):
            return "human-reviewed"
    return "machine-confirmed"


def _check_v02_families(rel, front, findings):
    """V14 (actor form), V15 (lifecycle shapes), V16 (legacy timestamp)."""
    # V14 — generated carries an actor in `by`.
    generated = front.get("generated")
    if generated is not None and generated != "":
        if not isinstance(generated, dict):
            findings.append(Finding(ERROR, "V14", rel,
                                    "'generated' must be a mapping with 'by' and 'at' "
                                    "(§5.2) — write generated: { by: ..., at: ... }"))
        else:
            by = generated.get("by")
            if not by:
                findings.append(Finding(ERROR, "V14", rel,
                                        "'generated' is missing 'by' (§5.2)"))
            elif not ACTOR.match(str(by)):
                findings.append(Finding(ERROR, "V14", rel,
                                        f"'generated.by' {by!r} is not an actor — use "
                                        f"'human:<id>', 'process:<id>' or "
                                        f"'<producer>/<version>' (§7)"))

    # V14 — every verification event carries an actor.
    verified = front.get("verified")
    if verified is not None and verified != "":
        events = _verification_events(verified)
        if not events:
            findings.append(Finding(ERROR, "V14", rel,
                                    "'verified' must be a {by, at} mapping or a list "
                                    "of them (§5.2)"))
        for event in events:
            if not isinstance(event, dict):
                findings.append(Finding(ERROR, "V14", rel,
                                        f"'verified' entry {event!r} is not a "
                                        f"{{by, at}} mapping (§5.2)"))
                continue
            by = event.get("by")
            if not by:
                findings.append(Finding(ERROR, "V14", rel,
                                        "a 'verified' entry is missing 'by' (§5.2)"))
            elif not ACTOR.match(str(by)):
                findings.append(Finding(ERROR, "V14", rel,
                                        f"'verified[].by' {by!r} is not an actor (§7)"))

    # V15 — lifecycle field shapes.
    status = front.get("status")
    if status and status not in STATUSES:
        findings.append(Finding(ERROR, "V15", rel,
                                f"status {status!r} is not one of "
                                f"{sorted(STATUSES)} (§5.4)"))
    stale_after = front.get("stale_after")
    if stale_after and not ISO_DAY.match(str(stale_after)):
        findings.append(Finding(ERROR, "V15", rel,
                                f"stale_after {stale_after!r} is not a YYYY-MM-DD "
                                f"date (§5.5)"))

    # V16 — still on the superseded key. A warning, not an error: §13.1 lets a
    # consumer fall back to a legacy timestamp, so this is migration debt that
    # stays visible rather than a broken concept.
    if not front.get("generated") and front.get("timestamp"):
        findings.append(Finding(WARNING, "V16", rel,
                                "carries the superseded 'timestamp' and no 'generated' "
                                "— migrate to generated: { by, at } (§5.2, §13.1)"))


def _check_types_and_fields(bundle, registries, concepts, findings):
    known_types = registries["types"]
    known_tags = registries["tags"]

    for path, rel, front, body, concept_type in concepts:
        # V1 — the type is registered.
        if known_types and concept_type not in known_types:
            findings.append(Finding(ERROR, "V1", rel,
                                    f"type {concept_type!r} is not registered in ontology.md"))
            spec = {"required_fields": [], "required_sections": []}
        else:
            spec = known_types.get(concept_type, {"required_fields": [], "required_sections": []})

        # V9 — universal frontmatter, plus this type's declared requirements.
        # 'generated' supersedes 'timestamp' (spec §5.2, §13.1). Either satisfies
        # V9 while the corpus migrates; V16 below marks the ones still on the
        # legacy key, so "migrated" and "not yet migrated" stay distinguishable.
        for field in ("title", "description", "tags"):
            if not front.get(field):
                findings.append(Finding(ERROR, "V9", rel,
                                        f"missing required frontmatter field {field!r}"))
        if not front.get("generated") and not front.get("timestamp"):
            findings.append(Finding(ERROR, "V9", rel,
                                    "missing required frontmatter field 'generated' "
                                    "(or the legacy 'timestamp' it supersedes)"))
        for field in spec["required_fields"]:
            if not front.get(field):
                findings.append(Finding(ERROR, "V9", rel,
                                        f"type {concept_type!r} requires frontmatter "
                                        f"field {field!r} (§Type Registry)"))
        if spec["required_sections"]:
            headings = [h.strip().lower() for h in HEADING.findall(body)]
            for section in spec["required_sections"]:
                wanted = section.lower()
                if not any(h == wanted or h.startswith(wanted) for h in headings):
                    findings.append(Finding(ERROR, "V9", rel,
                                            f"type {concept_type!r} requires a "
                                            f"'{section}' section (§Type Registry)"))

        # V2 — tags are registered.
        if known_tags:
            for tag in front.get("tags") or []:
                if tag not in known_tags:
                    findings.append(Finding(WARNING, "V2", rel,
                                            f"tag {tag!r} is not registered in ontology.md"))

        # V4 — stubs live in stubs/. Archived stubs are the declared exception:
        # §Concept Hierarchy Rules 5 puts every superseded concept in archive/,
        # and the two rules would otherwise contradict each other forever.
        normalised = rel.replace(os.sep, "/")
        if (concept_type == "Stub"
                and not normalised.startswith("stubs/")
                and not normalised.startswith("archive/")):
            findings.append(Finding(WARNING, "V4", rel,
                                    "type: Stub must live in the stubs/ subdirectory"))

        # V3 — a concept carrying confidence shows its working. Either a counted
        # set of sources, or a Citations section. The old form presumed
        # confidence was computed; measured against a real corpus, 0 of 104
        # concepts carried confidence_sources and 104 of 104 carried Citations,
        # so the rule was wrong for judgment-based bundles and got dropped
        # rather than argued with. Presence, not truth: 'confidence_sources: 0'
        # is a declared zero, correct for a Stub at confidence 0.0.
        # A Stub is a placeholder, not a claim. Its confidence 0.0 means "nothing
        # asserted yet", not "asserted weakly", so neither showing working (V3)
        # nor sitting inside a certainty band (V12) applies to it.
        is_stub = concept_type == "Stub"

        if front.get("confidence") is not None and not is_stub:
            has_sources = front.get("confidence_sources") is not None
            has_citations = any(h.strip().lower().startswith("citations")
                                for h in HEADING.findall(body))
            if not has_sources and not has_citations:
                findings.append(Finding(
                    WARNING, "V3", rel,
                    "carries 'confidence' but shows no working — add "
                    "'confidence_sources', or a '# Citations' section"))

        # V12 — confidence sits inside the band its tags declare. WARNING by
        # design: certainty is a judgment and a band is a sanity check on it,
        # not an authority over it.
        confidence = front.get("confidence")
        if confidence is not None and not is_stub:
            for tag in front.get("tags") or []:
                band = registries["bands"].get(tag)
                if not band:
                    continue
                low, high = band
                if not (low <= float(confidence) <= high):
                    findings.append(Finding(
                        WARNING, "V12", rel,
                        f"confidence {confidence} is outside the band "
                        f"{low}-{high} declared for tag {tag!r}"))

        # V14/V15/V16 — the OKF v0.2 trust and lifecycle families.
        _check_v02_families(rel, front, findings)

        # V8 — the ontology's own frontmatter.
        if rel == "ontology.md":
            if front.get("confidence") != 1.0 or front.get("memory_tier") != "semantic":
                findings.append(Finding(ERROR, "V8", rel,
                                        "ontology.md must carry memory_tier: semantic "
                                        "and confidence: 1.0"))

        # CHECK_6 — a concept must not be named index.md or log.md.
        if os.path.basename(rel) in RESERVED_NAMES:
            findings.append(Finding(ERROR, "CHECK_6", rel,
                                    "reserved filename used as a concept document"))


def strip_code_fences(text):
    """Body text with fenced blocks removed.

    A link inside a ``` fence is an example, not a link. Checking it reports a
    broken link for a file that was never meant to exist — and worse, teaches
    authors that the checker cries wolf.
    """
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return "\n".join(out)


def _check_links(bundle, concepts, findings):
    """CHECK_5 — internal markdown links resolve to files on disk."""
    for path, rel, front, body, _ in concepts:
        base = os.path.dirname(path)
        for target in MD_LINK.findall(strip_code_fences(body)):
            target = target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            # A leading "/" means the bundle root, not the filesystem root. A
            # real corpus used this convention throughout and produced 134 false
            # broken links against 20 distinct, existing targets.
            if clean.startswith("/"):
                resolved = os.path.join(bundle.root, clean.lstrip("/"))
            else:
                resolved = os.path.join(base, clean)
            if not os.path.exists(os.path.normpath(resolved)):
                findings.append(Finding(WARNING, "CHECK_5", rel,
                                        f"link target does not exist on disk: {target}"))


def _check_log(bundle, findings):
    """CHECK_4 and CHECK_8 — the log is dated, ordered, and not a placeholder."""
    if not os.path.exists(bundle.log_path):
        findings.append(Finding(ERROR, "CHECK_8", "log.md", "no log.md in the bundle"))
        return
    text = bundle.read(bundle.log_path)
    dates = ISO_DATE.findall(text)
    if not dates:
        findings.append(Finding(ERROR, "CHECK_8", "log.md",
                                "log.md has no '## YYYY-MM-DD' blocks — placeholder only"))
        return
    if dates != sorted(dates, reverse=True):
        out_of_order = next(
            (f"{a} appears above {b}" for a, b in zip(dates, dates[1:]) if a < b), "")
        findings.append(Finding(ERROR, "CHECK_4", "log.md",
                                f"date headings are not newest-first ({out_of_order})"))
    front, _, _ = split_frontmatter(text)
    if front is not None:
        findings.append(Finding(ERROR, "CHECK_4", "log.md", "log.md must not have frontmatter"))


def _check_supersession(bundle, concepts, findings):
    """V6 — superseded_by must be reciprocated by supersedes in the target."""
    by_stem = {os.path.basename(rel)[:-3]: (rel, front) for _, rel, front, _, _ in concepts}
    for _, rel, front, _, _ in concepts:
        target = front.get("superseded_by")
        if not target:
            continue
        stem = os.path.basename(str(target)).replace(".md", "")
        if stem not in by_stem:
            findings.append(Finding(ERROR, "V6", rel,
                                    f"superseded_by names {target!r}, which is not a concept"))
            continue
        target_rel, target_front = by_stem[stem]
        supersedes = target_front.get("supersedes")
        mine = os.path.basename(rel)[:-3]
        listed = supersedes if isinstance(supersedes, list) else [supersedes] if supersedes else []
        if not any(mine in str(item) for item in listed):
            findings.append(Finding(ERROR, "V6", rel,
                                    f"superseded_by {stem!r}, but {target_rel} does not "
                                    f"list a reciprocal 'supersedes'"))



def _ident(value):
    """A cell holding a single identifier, written `like-this` in the table."""
    return (value or "").strip().strip("`").strip()


def _path_globs(value):
    """Every path-like span in a registry cell that also carries prose.

    A real Source scope reads:
        `scenarios/scenario-*.md` (one row per file); `a/b.md` + `c.md` (...)
    Several globs, with explanation between them. Taking the whole cell matches
    nothing; taking only the first silently guards a fraction of the contract.
    """
    if not value:
        return []
    marked = [m.strip() for m in re.findall(r"`([^`]+)`", value)]
    paths = [m for m in marked if "/" in m or m.endswith(".md") or "*" in m]
    if paths:
        return paths
    bare = value.strip().split(" (")[0].strip()
    return [bare] if bare and bare.lower() not in NONE_MARKERS else []


def _live_contract_rows(rows, id_field="Contract ID"):
    """Drop placeholder rows — '*(none at bundle initialisation ...)*' and '—'."""
    live = []
    for row in rows:
        ident = _ident(row.get(id_field))
        if not ident or ident.startswith("*") or ident.lower() in NONE_MARKERS:
            continue
        live.append(row)
    return live


def _check_coverage_contracts(bundle, registries, findings):
    """CHECK_9 — every Source Coverage Contract's ledger is fully resolved.

    Reads the ledger's Status column only. Whether the ledger itself still
    matches the source document is ENRICHMENT_AGENT's job at ingestion; this
    cannot re-derive it and does not pretend to.
    """
    contracts = _live_contract_rows(registries["coverage_contracts"])
    if not contracts:
        findings.append(Finding(SKIP, "CHECK_9", None,
                                "no Source Coverage Contracts registered"))
        return
    for row in contracts:
        ledger_key = next((k for k in row if k.lower().startswith("coverage ledger")), None)
        ledger = _ident(row.get(ledger_key, ""))
        contract_id = _ident(row.get("Contract ID", "?"))
        if not ledger or ledger.startswith("*"):
            continue
        ledger_path = os.path.join(bundle.root, ledger.lstrip("/"))
        if not os.path.exists(ledger_path):
            findings.append(Finding(ERROR, "CHECK_9", ledger,
                                    f"contract {contract_id!r} names a ledger that "
                                    f"does not exist"))
            continue
        unresolved = []
        for table_rows in parse_tables(bundle.read(ledger_path)).values():
            for entry in table_rows:
                status_key = next((k for k in entry if k.strip().lower() == "status"), None)
                if not status_key:
                    continue
                # The Status cell often carries a note — "Captured *(closed
                # 2026-07-03 remediation pass)*". Match the leading status word,
                # not the whole cell, or every annotated row reads as unresolved.
                raw_status = entry[status_key].strip().strip("*").strip()
                status = re.split(r"\s*[*(\[]", raw_status, 1)[0].strip().lower()
                if status not in {"captured", "not applicable", "n/a", "partial",
                                  "not required"}:
                    first = next(iter(entry.values()), "?")
                    unresolved.append(f"{first} ({entry[status_key].strip()})")
        if unresolved:
            findings.append(Finding(ERROR, "CHECK_9", ledger,
                                    f"contract {contract_id!r}: {len(unresolved)} row(s) not "
                                    f"resolved — " + "; ".join(unresolved[:5])))


def _source_key(path, pattern, findings, contract_id):
    """A source file's identity key: from its title via `pattern`, else its stem."""
    stem = os.path.basename(path)[:-3]
    if not pattern:
        return stem
    try:
        with open(path, "r", encoding="utf-8") as handle:
            front, _, _ = split_frontmatter(handle.read())
    except OSError:
        return stem
    title = str((front or {}).get("title", ""))
    match = re.search(pattern, title)
    if match and match.groups():
        return match.group(1)
    findings.append(Finding(
        ERROR, "CHECK_7", os.path.basename(path),
        f"contract {contract_id!r}: Source key pattern {pattern!r} does not match "
        f"this file's title {title!r} — it has no identity key, so it cannot be "
        f"diffed against the deliverable"))
    return None


def _check_deliverable_contracts(bundle, registries, findings):
    """CHECK_7 — source files and deliverable records correspond 1:1.

    With a `Record pattern` declared, this is a real set diff in both directions,
    so an orphan record in the deliverable is caught as well as a missing one.
    Without one it can only prove every source appears somewhere by name, which
    cannot see an orphan — so that case reports SKIP and never PASS. A check that
    cannot fully decide must not read as though it did.
    """
    contracts = _live_contract_rows(registries["deliverable_contracts"])
    if not contracts:
        findings.append(Finding(SKIP, "CHECK_7", None,
                                "no Deliverable Parity Contracts registered"))
        return
    import glob as _glob
    for row in contracts:
        contract_id = _ident(row.get("Contract ID", "?"))
        scopes = _path_globs(row.get("Source scope", ""))
        deliverable = (_path_globs(row.get("Deliverable file", "")) or [""])[0]
        if not scopes or not deliverable:
            continue
        sources = sorted({m for scope in scopes
                          for m in _glob.glob(os.path.join(bundle.root, scope))})
        deliverable_path = os.path.join(bundle.root, deliverable.lstrip("/"))
        if not os.path.exists(deliverable_path):
            findings.append(Finding(ERROR, "CHECK_7", deliverable,
                                    f"contract {contract_id!r} names a deliverable that "
                                    f"does not exist"))
            continue
        if not sources:
            findings.append(Finding(ERROR, "CHECK_7", deliverable,
                                    f"contract {contract_id!r}: source scope {scopes!r} "
                                    f"matches no files — the contract guards nothing"))
            continue

        content = bundle.read(deliverable_path)
        record_pattern = _ident(row.get("Record pattern", ""))
        source_pattern = _ident(row.get("Source key pattern", ""))

        if not record_pattern or record_pattern in NONE_MARKERS:
            missing = [os.path.basename(s)[:-3] for s in sources
                       if os.path.basename(s)[:-3] not in content]
            if missing:
                findings.append(Finding(ERROR, "CHECK_7", deliverable,
                                        f"contract {contract_id!r}: no record found for "
                                        + ", ".join(missing[:5])))
            else:
                findings.append(Finding(
                    SKIP, "CHECK_7", deliverable,
                    f"contract {contract_id!r}: {len(sources)} source file(s) all appear "
                    f"by name, but no 'Record pattern' is declared, so an extra record in "
                    f"the deliverable cannot be detected. Declare one to make this a diff"))
            continue

        try:
            found = re.findall(record_pattern, content)
        except re.error as exc:
            findings.append(Finding(ERROR, "CHECK_7", "ontology.md",
                                    f"contract {contract_id!r}: Record pattern "
                                    f"{record_pattern!r} is not a valid regex ({exc})"))
            continue
        if found and isinstance(found[0], tuple):
            findings.append(Finding(ERROR, "CHECK_7", "ontology.md",
                                    f"contract {contract_id!r}: Record pattern must have "
                                    f"exactly one capture group"))
            continue
        deliverable_keys = set(found)

        source_keys = {}
        for path in sources:
            key = _source_key(path, source_pattern, findings, contract_id)
            if key is not None:
                source_keys.setdefault(key, os.path.relpath(path, bundle.root))

        if not deliverable_keys:
            findings.append(Finding(
                ERROR, "CHECK_7", deliverable,
                f"contract {contract_id!r}: Record pattern {record_pattern!r} matched "
                f"nothing. A pattern that finds no records makes every source file look "
                f"missing, so this is reported rather than diffed"))
            continue

        absent = sorted(set(source_keys) - deliverable_keys)
        orphans = sorted(deliverable_keys - set(source_keys))
        if absent:
            findings.append(Finding(
                ERROR, "CHECK_7", deliverable,
                f"contract {contract_id!r}: no record in the deliverable for "
                + ", ".join(f"{k} ({source_keys[k]})" for k in absent[:5])))
        if orphans:
            # Only a real diff can see this. Filename matching never could.
            findings.append(Finding(
                ERROR, "CHECK_7", deliverable,
                f"contract {contract_id!r}: record(s) in the deliverable with no source "
                f"concept: " + ", ".join(orphans[:5])))
        # A clean diff with a declared Record pattern is a genuine pass, and passes
        # are silent like every other check. Reporting SKIP here would say "could
        # not decide" about the one case where it fully did.


# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Check an OKF bundle for conformance.")
    parser.add_argument("root", nargs="?", default=".", help="bundle root (default: .)")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument("--quiet", action="store_true", help="suppress the summary line")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.root):
        print(f"error: no such directory {args.root!r}", file=sys.stderr)
        return 2

    bundle = Bundle(args.root)
    if not bundle.files:
        print(f"error: no .md files under {args.root!r} — not an OKF bundle", file=sys.stderr)
        return 2

    findings, _ = run_checks(bundle)
    errors = [f for f in findings if f.severity == ERROR]
    warnings = [f for f in findings if f.severity == WARNING]
    skipped = [f for f in findings if f.severity == SKIP]

    if args.json:
        print(json.dumps({"ok": not errors,
                          "errors": len(errors), "warnings": len(warnings),
                          "skipped": len(skipped),
                          "findings": [f.as_dict() for f in findings]}, indent=2))
        return 1 if errors else 0

    for finding in errors + warnings + skipped:
        print(finding, file=sys.stderr if finding.severity == ERROR else sys.stdout)

    if not args.quiet:
        print(f"\n{'NON-CONFORMANT' if errors else 'CONFORMANT'} — "
              f"{len(errors)} error(s), {len(warnings)} warning(s), "
              f"{len(skipped)} not fully decidable, "
              f"{len(bundle.files)} file(s) scanned")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
