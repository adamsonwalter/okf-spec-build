#!/usr/bin/env python3
"""Scaffold a new OKF knowledge bundle, ready to ingest and already conformant.

Run this from the kit. It creates a **separate repo** for the new corpus — the
kit never holds knowledge, and a bundle never holds a copy of the machinery.

    python3 scripts/okf_new_bundle.py ../my-new-corpus --title "My New Corpus"

What you get, in a new directory:

    okf-kit/            the kit, as a submodule pinned to its current commit
    ontology.md         DOMAIN ADDITIONS ONLY — the kit's registries are inherited
    log.md  index.md  README.md
    inbox/              put source material here
    check.command       double-click: build projections + run every check
    update-kit.command  double-click: move to a newer kit
    .github/workflows/  CI running the same checks

The new bundle's `ontology.md` deliberately does **not** copy the kit's type
registry, relationship taxonomy or rules. It inherits them from `okf-kit/` and
declares only what is specific to the domain. A copy is what drifts: one bundle
held a copy of the kit's rules, V3 went missing from it, and nothing noticed
because nothing compared the two. There is no copy here to lose a rule from.

The scaffold is checked before this script exits. A bundle that is not
conformant at birth is a bundle nobody can tell has broken later.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
KIT_URL = "https://github.com/adamsonwalter/okf-spec-build.git"

STANDARD_DIRS = ["inbox", "stubs", "archive", "reports", "coverage",
                 "projections", ".github/workflows"]

ONTOLOGY = """\
---
type: Ontology
title: {title}
description: Domain registry for the {title} bundle. Types, tags, relationships and rules \
not declared here are inherited from the kit at okf-kit/ontology.md.
memory_tier: semantic
confidence: 1.0
confidence_sources: 0
okf_version: "0.1"
timestamp: {timestamp}
tags: [ontology, system, governance]
---

> **This file declares domain additions only.** The generic type registry, the ten-relationship
> taxonomy, the system tags and rules V1–V13 are **inherited** from `okf-kit/ontology.md` and
> must not be copied here. A copy drifts silently — that is how a rule went missing from a
> bundle once, and nothing noticed because nothing compared the two.
>
> To extend: add a row below and update `timestamp`. Never delete — deprecate.

---

# Type Registry

## Project-Specific Types

> Types this domain needs beyond the inherited generic set.
> Format: `| Type | Description | Typical Body Sections | Required Sections | Required Fields |`
> Use `—` where nothing is required. Declaring a requirement here is what makes V9 enforce it —
> do not write a new validation rule for a per-type requirement.

| Type | Description | Typical Body Sections | Required Sections | Required Fields |
|---|---|---|---|---|
| *(none yet — add as the corpus grows)* | — | — | — | — |

---

# Tag Taxonomy

## Domain Tags

> Format: `| tag-name | meaning | certainty band |`
> Leave the band empty unless the tag genuinely implies a confidence range, and set it to what
> the corpus actually holds rather than an aspiration — a band tighter than authored practice
> fails a pile of concepts on day one and then gets switched off.

| Tag | Meaning | Certainty band |
|---|---|---|
| *(none yet — add as the corpus grows)* | — | |

---

# Validation Rules

> V1–V13 are reserved by the kit and inherited. A rule specific to this bundle **must** be
> named `V-<slug>`, never a bare number — a bare number either shadows a kit rule or collides
> with the next one the kit adds.

| Rule | Check | Severity |
|---|---|---|
| *(none yet)* | — | — |

---

# Authority Posture

> What each part of this bundle is **for**, declared per area so new material inherits its
> posture from where it lands. Without this, a bundle carrying adjacent context needs a caveat
> maintained in every file — which drifts, and the first caveat to go is on the material that
> most needs one.

| Scope | Posture | Note |
|---|---|---|
| *(declare the first time this bundle carries material outside its own authority)* | — | — |

---

# Projection

| Setting | Value |
|---|---|
| `Bundle slug` | `{slug}` |
| `Bundle title` | {title} |
| `Schema id` | `{slug}/concepts` |
| `Tag slices` | |
| `Disclaimer` | {disclaimer} |

---

# Ontology Version History

| Version | Date | Change |
|---|---|---|
| 0.1 | {today} | Bundle initialised from the okf-spec-build kit. Domain registries empty; kit registries inherited. |
"""

INDEX = """\
---
okf_version: "0.1"
---

# {title}

Root index. Maintained by INDEX_AGENT.
All types and relationships are governed by [ontology.md](ontology.md), which inherits the
kit's registries from [okf-kit/ontology.md](okf-kit/ontology.md).

## Governance

* [ontology.md](ontology.md) — domain types, tags, rules, authority posture, projection config

## Concepts

*(populated by INDEX_AGENT as concepts are created)*

## Stubs

*(populated as known gaps are recorded)*

## Reports

*(populated by LOG_AGENT)*

## Archive

*(populated as concepts are superseded)*
"""

LOG = """\
# Bundle Update Log

## {today}

* **Initialization**: `{slug}` OKF bundle created from the [okf-spec-build]({url}) kit. \
Kit attached as a submodule at `okf-kit/`, pinned at `{pin}`. Domain registries empty; kit \
registries inherited. Awaiting first ingest.
"""

README = """\
# {title}

An OKF knowledge bundle. Machinery comes from the [OKF kit]({url}), carried at `okf-kit/` as a
git submodule **pinned to one commit** — so this bundle records exactly which version of the
machinery last built and checked it.

The two files other projects consume, once there is content:

| File | For |
|---|---|
| `projections/{slug}-master.md` | Upload to a cloud LLM Project. One file in, one file out. |
| `projections/{slug}-master.json` | An application. Typed concepts, the ontology, and the relationship graph as `edges`. |

Both are **generated**. Never edit them by hand.

## Daily use

1. Put source material in `inbox/`, or edit a concept.
2. Double-click **`check.command`** — rebuilds projections, runs every check.
3. If it says OK, commit and push.

Double-click **`update-kit.command`** to move to a newer kit. Nothing arrives on its own.

## Before the first ingest

Declare in `ontology.md`:

- **`# Authority Posture`** — what this bundle is the authority for, and what it merely carries
  as context. Declared per folder, so later material inherits it.
- **`# Projection`** — a `Disclaimer` if the corpus needs one; `Tag slices` if you want
  pre-built per-tag projections.

Domain types, tags and rules go in `ontology.md` too. **Do not copy anything from
`okf-kit/ontology.md`** — it is inherited. A bundle rule must be named `V-<slug>`, never a bare
number.

Operating instructions: [`okf-kit/docs/OPERATING.md`](okf-kit/docs/OPERATING.md).
Why the checks are shaped as they are: [`okf-kit/docs/DECISIONS.md`](okf-kit/docs/DECISIONS.md).
"""


def run(cmd, cwd, quiet=True):
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0 and not quiet:
        print(result.stdout + result.stderr, file=sys.stderr)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Scaffold a new OKF bundle as its own repo.")
    parser.add_argument("path", help="directory for the new bundle (must not exist)")
    parser.add_argument("--title", help="human title (default: derived from the directory)")
    parser.add_argument("--disclaimer", default="",
                        help="carried in the projection header, e.g. 'Information, not advice.'")
    parser.add_argument("--kit-url", default=KIT_URL)
    parser.add_argument("--no-git", action="store_true",
                        help="scaffold files only — no git init, no submodule")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if root.exists() and any(root.iterdir()):
        print(f"error: {root} already exists and is not empty", file=sys.stderr)
        return 2

    slug = root.name
    title = args.title or slug.replace("-", " ").replace("_", " ").title()
    today = date.today().isoformat()
    root.mkdir(parents=True, exist_ok=True)
    for directory in STANDARD_DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)

    pin = "unpinned"
    if not args.no_git:
        run(["git", "init", "-q"], root)
        print("Attaching the kit as a submodule…")
        result = run(["git", "submodule", "add", "-q", args.kit_url, "okf-kit"], root)
        if result.returncode != 0:
            print("error: could not attach the kit submodule.\n" + result.stderr,
                  file=sys.stderr)
            return 2
        pin = run(["git", "-C", "okf-kit", "rev-parse", "--short", "HEAD"],
                  root).stdout.strip() or "unknown"

    fields = dict(slug=slug, title=title, today=today, url=args.kit_url, pin=pin,
                  timestamp=f"{today}T00:00:00Z",
                  disclaimer=args.disclaimer or "—")
    (root / "ontology.md").write_text(ONTOLOGY.format(**fields), encoding="utf-8")
    (root / "index.md").write_text(INDEX.format(**fields), encoding="utf-8")
    (root / "log.md").write_text(LOG.format(**fields), encoding="utf-8")
    (root / "README.md").write_text(README.format(**fields), encoding="utf-8")
    (root / "inbox" / "README.md").write_text(
        "# inbox\n\nPut source material here, then ask an agent to ingest it.\n"
        "Processed sources move to `inbox/processed/<date>/`.\n", encoding="utf-8")
    (root / ".gitignore").write_text(
        ".DS_Store\nThumbs.db\n*.swp\n*~\n__pycache__/\n*.pyc\n", encoding="utf-8")

    for name in ("check.command", "update-kit.command"):
        source = KIT / "templates" / name
        if source.exists():
            shutil.copy2(source, root / name)
            os.chmod(root / name, 0o755)
    workflow = KIT / "templates" / "bundle-conformance.yml"
    if workflow.exists():
        shutil.copy2(workflow, root / ".github" / "workflows" / "conformance.yml")

    # A bundle that is not conformant at birth is one nobody can tell has broken
    # later, so prove it here rather than leaving it to the first run.
    print("\nChecking the new bundle…")
    checker = (root / "okf-kit" / "scripts" / "okf_check.py")
    if not checker.exists():
        checker = KIT / "scripts" / "okf_check.py"
    result = subprocess.run([sys.executable, str(checker), str(root), "--quiet"],
                            capture_output=True, text=True)
    print(result.stdout.strip() or result.stderr.strip())

    print(f"\nCreated {root}")
    print("\nNext:")
    print(f"  1. cd {root}")
    print("  2. declare # Authority Posture in ontology.md — what this bundle is the")
    print("     authority for, and what it only carries as context")
    print("  3. put source material in inbox/, then ask an agent to ingest it")
    print("  4. ./check.command, then commit")
    return 0 if result.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
