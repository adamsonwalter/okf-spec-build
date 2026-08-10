#!/usr/bin/env python3
"""PROJECTION_AGENT in code — compile any OKF bundle into its projection files.

Ported from a per-bundle `build_projection.py` that lived only inside one target
repo. That copy is why a new bundle cloned from this kit had no way to produce a
master file at all: the generator did not ship the one script every bundle needs.

Nothing here is bundle-specific. Title, slug, schema id and the pre-built tag
slices are read from a `# Projection` section in the bundle's own `ontology.md`,
with defaults derived from the directory when that section is absent — declare it
in the registry, let one script serve every bundle (docs/DECISIONS.md D1).

Two artefacts, two consumers:
  <slug>-master.md    prose, for a model to read whole or paste into a cloud Project
  <slug>-master.json  typed, for an application to consume without parsing prose

The JSON carries the relationship graph as `edges` when okf_graph.py is present.
An application reading the markdown would otherwise have to infer relationships
back out of prose, which is exactly where errors enter.

Usage:
    python3 scripts/okf_project.py [bundle_root]

Exit codes:
    0  projections written
    1  an ontology registry was empty, or an artefact conformance check failed
    2  the bundle could not be read
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {
    "projections", "deliverables", "stubs", "archive", "inbox", "scripts",
    "tests", "templates", ".git", ".ai_context", "__pycache__",
}
EXCLUDE_FILES = {"index.md", "log.md"}
RESERVED_NAMES = {"index.md", "log.md"}

ONTOLOGY_TABLES = {
    "types": ("Type Registry",
              ("name", "description", "bodySections", "requiredSections", "requiredFields")),
    "relationships": ("Relationship Taxonomy", ("name", "direction", "prose", "example")),
    "tags": ("Tag Taxonomy", ("name", "meaning", "certaintyBand")),
    "validationRules": ("Validation Rules", ("id", "check", "severity")),
    "deprecatedTypes": ("Deprecated Types", ("name", "note")),
}


# ---------------------------------------------------------------------------
# Per-bundle configuration, declared in ontology.md
# ---------------------------------------------------------------------------

def read_projection_config(root: Path, ontology_text: str) -> dict:
    """Bundle slug, title, schema id and tag slices from `# Projection`.

    Absent, every value has a defensible default derived from the bundle itself,
    so a freshly cloned bundle produces projections without being configured.
    """
    config = {
        "slug": root.name,
        "title": root.name,
        "schema": f"{root.name}/concepts",
        "tag_slices": [],
    }
    meta, _ = strip_frontmatter(ontology_text)
    if meta.get("title"):
        config["title"] = meta["title"]

    section = _section_body(ontology_text, "Projection")
    if section is None:
        return config
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or re.match(r"^[\s:|-]+$", cells[0]):
            continue
        key, value = cells[0].lower(), cells[1].strip()
        if key in ("setting", ""):
            continue
        if key == "bundle slug" and value:
            config["slug"] = value
        elif key == "bundle title" and value:
            config["title"] = value
        elif key == "schema id" and value:
            config["schema"] = value
        elif key == "tag slices":
            config["tag_slices"] = [t.strip().strip("`") for t in value.split(",") if t.strip()]
    return config


def _section_body(text: str, name: str) -> str | None:
    parts = re.split(r"^# (.+)$", text, flags=re.MULTILINE)
    for i in range(1, len(parts) - 1, 2):
        if parts[i].strip().startswith(name):
            return parts[i + 1]
    return None


# ---------------------------------------------------------------------------
# Bundle reading
# ---------------------------------------------------------------------------

def read_log_dates(root: Path) -> tuple[str, str]:
    """The corpus version, and the newest log entry of any kind.

    Downstream applications key their release on the corpus version: a session
    assessed under an older release is flagged for reassessment. That is right
    when a concept has changed and noise when a build script has, so a date whose
    every entry is marked ``Kit`` is tooling and does not move it.
    """
    log_path = root / "log.md"
    if not log_path.exists():
        return "unknown", "unknown"
    log = log_path.read_text(encoding="utf-8")
    parts = re.split(r"^## (\d{4}-\d{2}-\d{2})\s*$", log, flags=re.MULTILINE)
    newest_any = content_head = "unknown"
    for i in range(1, len(parts) - 1, 2):
        date, body = parts[i], parts[i + 1]
        if newest_any == "unknown":
            newest_any = date
        kinds = set(re.findall(r"^\* \*\*([A-Za-z][A-Za-z ]*)\*\*", body, re.MULTILINE))
        if not (bool(kinds) and kinds <= {"Kit"}) and content_head == "unknown":
            content_head = date
    if content_head == "unknown":
        content_head = newest_any
    return content_head, newest_any


def strip_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, text[end + 5:]


def parse_tags(raw: str) -> list:
    raw = (raw or "").strip()
    if raw.startswith("[") and raw.endswith("]"):
        return [t.strip().strip("'\"") for t in raw[1:-1].split(",") if t.strip()]
    return [raw] if raw else []


def collect_concept_files(root: Path) -> list:
    files = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_FILES or path.name in RESERVED_NAMES:
            continue
        if path.name.isupper():
            continue                        # ALL CAPS = agent instructions
        files.append(path)
    return files


def concept_title(meta: dict, path: Path) -> str:
    return meta.get("title") or path.stem.replace("-", " ").title()


def metadata_line(meta: dict) -> str:
    parts = [f"Type: {meta.get('type', 'Concept')}"]
    if meta.get("confidence"):
        parts.append(f"Confidence: {meta['confidence']}")
    tags = parse_tags(meta.get("tags", ""))
    if tags:
        parts.append(f"Tags: {', '.join(tags)}")
    if meta.get("timestamp"):
        parts.append(f"Updated: {meta['timestamp']}")
    return "*{}*".format(" | ".join(parts))


def sync_status(generated_date: str, log_head: str) -> str:
    if log_head == "unknown":
        return "Current"
    return "Current" if generated_date >= log_head else "STALE"


def build_header(config, scope, concept_count, generated, log_head) -> str:
    upload = (
        "> **UPLOAD INSTRUCTIONS**: Upload THIS FILE ONLY to your cloud LLM Project "
        "(Gemini Gem, Claude.ai Project, ChatGPT Project). Do NOT upload index.md, "
        "log.md, or individual concept files alongside it — this file already "
        "contains the ontology and all concepts.\n"
        "> To update: regenerate this file and replace the existing upload.\n"
        "> **ONE FILE IN = ONE FILE OUT.**"
    )
    return (
        f"# {config['title']} — Knowledge Projection\n\n"
        f"| Field | Value |\n|---|---|\n"
        f"| Generated | {generated} |\n"
        f"| Scope | {scope} |\n"
        f"| Concepts included | {concept_count} |\n"
        f"| Log head | {log_head} |\n"
        f"| Sync status | {sync_status(generated[:10], log_head)} |\n\n"
        f"{upload}\n"
    )


def compile_projection(root, config, files, generated, log_head, tag=None):
    ontology_path = root / "ontology.md"
    ontology_body = strip_frontmatter(ontology_path.read_text(encoding="utf-8"))[1]

    entries = []
    for path in files:
        if path == ontology_path:
            continue
        meta, body = strip_frontmatter(path.read_text(encoding="utf-8"))
        if tag and tag not in parse_tags(meta.get("tags", "")):
            continue
        entries.append((concept_title(meta, path), metadata_line(meta), meta, body, path))
    entries.sort(key=lambda e: e[0].lower())

    sections = [
        build_header(config, f"tag: {tag}" if tag else "master (all concepts)",
                     len(entries), generated, log_head),
        "---\n", "## §0 Ontology\n\n", ontology_body.strip(), "\n",
    ]
    for title, meta_line, _meta, body, _path in entries:
        sections.extend(["\n---\n\n", f"## {title}\n\n", meta_line, "\n\n", body.strip(), "\n"])
    return "".join(sections), len(entries), entries


# ---------------------------------------------------------------------------
# Structured projection
# ---------------------------------------------------------------------------

def extract_citations(body: str) -> list:
    out, in_block = [], False
    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^#\s*Citations\s*$", stripped, re.I):
            in_block = True
            continue
        if in_block and stripped.startswith("#"):
            break
        if in_block and stripped.startswith("-"):
            text = stripped.lstrip("-").strip()
            match = re.search(r"https?://\S+", text)
            out.append({"text": text, "url": match.group(0).rstrip(".,;") if match else ""})
    return out


def parse_confidence(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ontology(text: str) -> dict:
    """Every registry in ontology.md, as data. Fails loudly on an empty section.

    An empty registry is indistinguishable from a permissive one, so a section
    that yields no rows stops the build rather than shipping a permissive artefact.
    """
    parts = re.split(r"^# (.+)$", text, flags=re.MULTILINE)
    by_name = {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}

    def rows_of(prefix):
        body = next((v for k, v in by_name.items() if k.startswith(prefix)), None)
        if body is None:
            return []
        rows = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("|") or re.match(r"^\|[\s:|-]+\|?$", line):
                continue
            cells = [c.strip().strip("`") for c in line.strip("|").split("|")]
            if not cells or not cells[0]:
                continue
            if cells[0].lower() in {"type", "relationship", "tag", "rule", "contract id",
                                    "version", "directory", "deprecated type", "deprecated",
                                    "setting", "field"}:
                continue
            rows.append(cells)
        return rows

    ontology = {}
    for key, (prefix, fields) in ONTOLOGY_TABLES.items():
        rows = rows_of(prefix)
        if not rows:
            raise SystemExit(
                f"Ontology check failed: section '{prefix}' yielded no rows. "
                f"An empty registry is indistinguishable from a permissive one — "
                f"fix ontology.md or the parser before shipping artefacts."
            )
        ontology[key] = [{f: (r[n] if n < len(r) else "") for n, f in enumerate(fields)}
                         for r in rows]

    version_rows = rows_of("Ontology Version History")
    dated = [(r[1], r[0]) for r in version_rows
             if len(r) > 1 and re.match(r"^\d{4}-\d{2}-\d{2}$", r[1])]
    ontology["version"] = max(dated)[1] if dated else "unknown"
    ontology["versionAsAt"] = max(dated)[0] if dated else ""
    return ontology


def read_edges(root: Path) -> tuple:
    """The typed relationship graph, so an application need not parse prose.

    Reported as absent rather than empty when the extractor is unavailable — an
    application must be able to tell "no graph shipped" from "no relationships".
    """
    try:
        import okf_check
        import okf_graph
    except ImportError:
        return None, "okf_graph.py unavailable"
    try:
        edges, _ = okf_graph.extract_edges(okf_check.Bundle(str(root)))
    except Exception as exc:                      # never fail a build on the graph
        return None, f"extraction failed: {exc}"
    return [e.as_dict() for e in edges], None


def build_structured(root, config, entries, scope, generated, log_head, ontology):
    concepts = []
    for title, _meta_line, meta, body, path in entries:
        concepts.append({
            "title": title,
            "type": meta.get("type", ""),
            "description": meta.get("description", ""),
            "resource": meta.get("resource", ""),
            "confidence": parse_confidence(meta.get("confidence", "")),
            "tags": parse_tags(meta.get("tags", "")),
            "updated": meta.get("timestamp", ""),
            "sourcePath": str(path.relative_to(root)),
            "body": body.strip(),
            "citations": extract_citations(body),
        })
    edges, edges_note = read_edges(root)
    payload = {
        "schema": config["schema"],
        "schemaVersion": 1,
        "generated": generated,
        "scope": scope,
        "logHead": log_head,
        "logHeadAnyEntry": read_log_dates(root)[1],
        "syncStatus": sync_status(generated[:10], log_head),
        "ontology": ontology,
        "conceptCount": len(concepts),
        "concepts": concepts,
    }
    if edges is None:
        payload["edges"] = None
        payload["edgesUnavailable"] = edges_note
    else:
        payload["edgeCount"] = len(edges)
        payload["edges"] = edges
    return payload


# ---------------------------------------------------------------------------
# Artefact conformance
# ---------------------------------------------------------------------------

def check_artefacts_against_standard(root: Path, written: list) -> bool:
    """Every artefact written is registered in AGENTS.MD, and vice versa.

    It is possible to add an artefact and never register it — that happened, and
    nothing complained, so an artefact existed outside the instructions and anyone
    following them would not have known to regenerate it.
    """
    standard_path = root / "AGENTS.MD"
    if not standard_path.exists():
        print("WARN: AGENTS.MD not found — artefact conformance not checked")
        return True
    standard = standard_path.read_text(encoding="utf-8")
    problems = []

    match = re.search(r"Rebuild the pre-built set \(([^)]*)\)", standard, re.S)
    declared = ({t.strip() for t in re.split(r"[,\s]+", match.group(1)) if t.strip()}
                if match else set())

    for path in written:
        registered = (path.stem in declared if path.parent.name == "by-tag"
                      else path.name in standard)
        if not registered:
            where = (f"projections/by-tag/{path.name}" if path.parent.name == "by-tag"
                     else path.name)
            problems.append(f"  written but not registered: {where}")

    named = set(re.findall(r"projections/(?:by-tag/)?([A-Za-z0-9._<>-]+\.(?:md|json))", standard))
    named = {n for n in named if "<" not in n and ">" not in n} - {"README.md"}
    for name in sorted(named - {p.name for p in written}):
        problems.append(f"  registered but not written: projections/{name}")

    if problems:
        print("Artefact conformance failed against AGENTS.MD:")
        for problem in problems:
            print(problem)
        return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compile an OKF bundle's projections.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    ontology_path = root / "ontology.md"
    if not ontology_path.exists():
        print(f"error: no ontology.md in {root} — not an OKF bundle", file=sys.stderr)
        return 2

    ontology_text = ontology_path.read_text(encoding="utf-8")
    config = read_projection_config(root, ontology_text)
    projections = root / "projections"
    by_tag = projections / "by-tag"
    projections.mkdir(exist_ok=True)

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_head = read_log_dates(root)[0]
    files = collect_concept_files(root)
    written = []

    text, count, entries = compile_projection(root, config, files, generated, log_head)
    out = projections / f"{config['slug']}-master.md"
    out.write_text(text, encoding="utf-8")
    written.append(out)
    if not args.quiet:
        print(f"Wrote {out} ({count} concepts)")

    structured = build_structured(root, config, entries, "master (all concepts)",
                                  generated, log_head, parse_ontology(ontology_text))
    out = projections / f"{config['slug']}-master.json"
    out.write_text(json.dumps(structured, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    written.append(out)
    if not args.quiet:
        edges = structured.get("edgeCount")
        detail = f", {edges} edges" if edges is not None else ", graph unavailable"
        print(f"Wrote {out} ({structured['conceptCount']} concepts{detail}, typed)")

    if config["tag_slices"]:
        by_tag.mkdir(exist_ok=True)
    for tag in config["tag_slices"]:
        text, count, _ = compile_projection(root, config, files, generated, log_head, tag=tag)
        out = by_tag / f"{tag}.md"
        out.write_text(text, encoding="utf-8")
        written.append(out)
        if not args.quiet:
            print(f"Wrote {out} ({count} concepts)")

    return 0 if check_artefacts_against_standard(root, written) else 1


if __name__ == "__main__":
    sys.exit(main())
