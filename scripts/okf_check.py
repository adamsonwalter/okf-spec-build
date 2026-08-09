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
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

ERROR, WARNING, SKIP = "ERROR", "WARNING", "SKIP"

RESERVED_NAMES = {"index.md", "log.md"}
# Generated or non-concept trees. projections/ is rebuilt from the concepts, so
# checking it would double-report every finding against a derived copy.
EXCLUDED_DIRS = {".git", "projections", "node_modules", "__pycache__", ".venv",
                 "templates",      # seeds for reserved files, not concepts
                 "inbox",          # raw source documents awaiting ingestion
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
    """Return (frontmatter_dict_or_None, body, error_or_None)."""
    if not text.startswith("---"):
        return None, text, None                      # no frontmatter at all
    end = text.find("\n---", 3)
    if end == -1:
        return None, text, "frontmatter block is never closed"
    raw = text[3:end].strip("\n")
    body = text[end + 4:]
    data = {}
    for line in raw.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None, body, f"frontmatter line is not 'key: value': {line.strip()!r}"
        key, _, value = line.partition(":")
        data[key.strip()] = _scalar(value.strip())
    return data, body, None


def _scalar(value):
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [v.strip().strip("\"'") for v in inner.split(",") if v.strip()] if inner else []
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d*\.\d+", value):
        return float(value)
    return value


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
    registries = {"types": {}, "tags": set(), "relationships": set(),
                  "rules": {}, "deliverable_contracts": [], "coverage_contracts": []}
    if not os.path.exists(bundle.ontology_path):
        findings.append(Finding(ERROR, "ONTOLOGY", "ontology.md",
                                "no ontology.md — nothing defines what a valid concept is"))
        return registries

    tables = parse_tables(bundle.read(bundle.ontology_path))
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
            if "Relationship" in row:
                registries["relationships"].add(_ident(row["Relationship"]))
            if "Rule" in row and "Check" in row:
                registries["rules"][_ident(row["Rule"])] = row.get("Severity", ERROR).strip()
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
    return findings, registries


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
        for field in ("title", "description", "timestamp", "tags"):
            if not front.get(field):
                findings.append(Finding(ERROR, "V9", rel,
                                        f"missing required frontmatter field {field!r}"))
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

        # V3 — confidence without its sources.
        if front.get("confidence") is not None and not front.get("confidence_sources"):
            findings.append(Finding(WARNING, "V3", rel,
                                    "carries 'confidence' with no 'confidence_sources'"))

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


def _check_links(bundle, concepts, findings):
    """CHECK_5 — internal markdown links resolve to files on disk."""
    for path, rel, front, body, _ in concepts:
        base = os.path.dirname(path)
        for target in MD_LINK.findall(body):
            target = target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, clean))):
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
                status = entry[status_key].strip().strip("*").lower()
                if status not in {"captured", "not applicable", "n/a", "partial"}:
                    first = next(iter(entry.values()), "?")
                    unresolved.append(f"{first} ({entry[status_key].strip()})")
        if unresolved:
            findings.append(Finding(ERROR, "CHECK_9", ledger,
                                    f"contract {contract_id!r}: {len(unresolved)} row(s) not "
                                    f"resolved — " + "; ".join(unresolved[:5])))


def _check_deliverable_contracts(bundle, registries, findings):
    """CHECK_7 — source files and deliverable records correspond 1:1.

    The source side is a glob and is checked. The deliverable side is a
    hand-authored artifact whose record format is not specified by the kit, so
    this searches it for each source identity key as a literal string. That is
    weaker than a real diff, so a clean result is reported as SKIP rather than
    PASS: a check that cannot fully decide must not read as if it did.
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
        missing = [os.path.basename(s)[:-3] for s in sources
                   if os.path.basename(s)[:-3] not in content]
        if missing:
            findings.append(Finding(ERROR, "CHECK_7", deliverable,
                                    f"contract {contract_id!r}: no record found for "
                                    + ", ".join(missing[:5])))
        else:
            findings.append(Finding(SKIP, "CHECK_7", deliverable,
                                    f"contract {contract_id!r}: {len(sources)} source file(s) "
                                    f"all appear in the deliverable by name; a true "
                                    f"record-level diff needs the deliverable's own format"))


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
