#!/usr/bin/env python3
"""Validate this plugin: manifests, skill frontmatter, links, and the criteria table.

Run before committing. Everything it checks has broken a plugin at least once:
a manifest that fails to parse silently drops the plugin, a skill without a
description never triggers, and a reference link that does not resolve sends the
model looking for a file that is not there.

Usage:
  python3 scripts/selfcheck.py
  python3 scripts/selfcheck.py --quiet     # only report problems
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

MANIFESTS = [
    (".claude-plugin/marketplace.json", ["name", "owner", "plugins"]),
    (".claude-plugin/plugin.json", ["name"]),
    (".cursor-plugin/plugin.json", ["name"]),
    (".codex-plugin/plugin.json", ["name"]),
    (".agents/plugins/marketplace.json", ["name", "plugins"]),
]

# Level counts in WCAG 2.2, with 4.1.1 Parsing removed.
EXPECTED_LEVELS = {"A": 31, "AA": 24, "AAA": 31}

EM_DASH = "\u2014"

# Directories that hold generated or third-party content rather than this
# repository's own prose and code.
SKIP = {".git", "node_modules", "wcag-workspace", "__pycache__", "vendor"}

problems: list[str] = []
notes: list[str] = []


def fail(message: str) -> None:
    problems.append(message)


def note(message: str) -> None:
    notes.append(message)


def check_manifests() -> None:
    for relative, required in MANIFESTS:
        path = ROOT / relative
        if not path.is_file():
            fail(f"{relative}: missing")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{relative}: invalid JSON, {exc}")
            continue
        for key in required:
            if key not in data:
                fail(f"{relative}: missing required key {key!r}")
        note(f"{relative}: valid")

    marketplace = ROOT / ".claude-plugin/marketplace.json"
    plugin = ROOT / ".claude-plugin/plugin.json"
    if marketplace.is_file() and plugin.is_file():
        market = json.loads(marketplace.read_text(encoding="utf-8"))
        manifest = json.loads(plugin.read_text(encoding="utf-8"))
        entries = {p.get("name") for p in market.get("plugins", [])}
        if manifest.get("name") not in entries:
            fail(f"marketplace.json lists {sorted(entries)} but plugin.json is named "
                 f"{manifest.get('name')!r}. The install command would not resolve.")
        versions = {p.get("version") for p in market.get("plugins", [])
                    if p.get("name") == manifest.get("name")}
        if versions and manifest.get("version") not in versions:
            fail(f"version mismatch: plugin.json {manifest.get('version')}, "
                 f"marketplace entry {versions.pop()}")


def parse_frontmatter(text: str) -> dict | None:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    fields, key = {}, None
    for line in match.group(1).splitlines():
        pair = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if pair:
            key = pair.group(1)
            fields[key] = pair.group(2).strip().strip('"')
        elif key and line.startswith((" ", "\t")):
            fields[key] += " " + line.strip()
    return fields


def check_skills() -> None:
    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        fail("skills/: missing")
        return
    found = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if not found:
        fail("skills/: no skill directories")
    for directory in found:
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            fail(f"skills/{directory.name}/: no SKILL.md")
            continue
        text = skill_file.read_text(encoding="utf-8")
        fields = parse_frontmatter(text)
        if fields is None:
            fail(f"skills/{directory.name}/SKILL.md: no YAML frontmatter")
            continue
        if fields.get("name") != directory.name:
            fail(f"skills/{directory.name}/SKILL.md: frontmatter name is "
                 f"{fields.get('name')!r}, which does not match the directory. The skill "
                 "would be invoked under the wrong name.")
        description = fields.get("description", "")
        if not description:
            fail(f"skills/{directory.name}/SKILL.md: no description. The skill will "
                 "never trigger.")
        elif len(description) < 80:
            fail(f"skills/{directory.name}/SKILL.md: description is {len(description)} "
                 "characters. Too short to describe when the skill applies.")
        body_lines = len(text.splitlines())
        if body_lines > 500:
            fail(f"skills/{directory.name}/SKILL.md: {body_lines} lines. Move detail into "
                 "a reference file and point at it.")
        note(f"skills/{directory.name}: {body_lines} lines, "
             f"description {len(description)} chars")


def check_links() -> None:
    for path in ROOT.rglob("*.md"):
        if SKIP.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"`((?:\.\.?/)[^`\s()]+\.(?:md|py|json))`", text):
            target = (path.parent / match.group(1)).resolve()
            if not target.exists():
                fail(f"{path.relative_to(ROOT)}: link to {match.group(1)} does not resolve")
        for match in re.finditer(r"\]\((?!https?:|#)([^)]+\.(?:md|py|json))\)", text):
            target = (path.parent / match.group(1)).resolve()
            if not target.exists():
                fail(f"{path.relative_to(ROOT)}: link to {match.group(1)} does not resolve")


def check_scripts() -> None:
    scripts = sorted((ROOT / "scripts").glob("*.py"))
    if not scripts:
        fail("scripts/: no Python scripts")
    for script in scripts:
        source = script.read_text(encoding="utf-8")
        try:
            compile(source, str(script), "exec")
        except SyntaxError as exc:
            fail(f"scripts/{script.name}: syntax error on line {exc.lineno}")
            continue
        if not source.startswith("#!/usr/bin/env python3"):
            fail(f"scripts/{script.name}: no shebang")
        import ast
        if not ast.get_docstring(ast.parse(source)):
            fail(f"scripts/{script.name}: no module docstring explaining what it does")
        note(f"scripts/{script.name}: compiles")


def check_criteria_table() -> None:
    report = ROOT / "scripts/report.py"
    if not report.is_file():
        fail("scripts/report.py: missing")
        return
    namespace: dict = {}
    exec(compile(report.read_text(encoding="utf-8"), str(report), "exec"),
         {"__name__": "selfcheck"}, namespace)
    criteria = namespace.get("CRITERIA", [])
    counts: dict[str, int] = {}
    for _number, _title, level, _version in criteria:
        counts[level] = counts.get(level, 0) + 1
    if counts != EXPECTED_LEVELS:
        fail(f"scripts/report.py CRITERIA: level counts are {counts}, expected "
             f"{EXPECTED_LEVELS} for WCAG 2.2 with 4.1.1 removed")
    else:
        note(f"criteria table: {sum(counts.values())} criteria, "
             f"{counts['A']} A / {counts['AA']} AA / {counts['AAA']} AAA")

    numbers = [c[0] for c in criteria]
    if len(set(numbers)) != len(numbers):
        fail("scripts/report.py CRITERIA: duplicate criterion numbers")
    if "4.1.1" in numbers:
        fail("scripts/report.py CRITERIA: 4.1.1 Parsing was removed in WCAG 2.2 and "
             "should not appear in the table")

    # Every criterion should be documented in the reference catalogue.
    catalogue = ""
    for name in ("sc-perceivable", "sc-operable", "sc-understandable", "sc-robust"):
        path = ROOT / "references" / f"{name}.md"
        if path.is_file():
            catalogue += path.read_text(encoding="utf-8")
        else:
            fail(f"references/{name}.md: missing")
    missing = [n for n in numbers
               if f"### {n} " not in catalogue and f"## {n} " not in catalogue]
    if missing:
        fail(f"references/: {len(missing)} criteria have no catalogue entry: "
             f"{', '.join(missing[:12])}")
    else:
        note("criteria catalogue: every criterion has an entry")


def check_prose() -> None:
    """The docs follow the anti-slop rules, which ban the em dash outright."""
    offenders = []
    for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.py")):
        if SKIP.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if EM_DASH in text:
            offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        fail(f"em dash found in: {', '.join(offenders)}. The documentation follows the "
             "anti-slop rules, which replace it with a period, comma, colon, or "
             "parentheses.")
    else:
        note("prose: no em dashes")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate the wcag plugin.")
    parser.add_argument("--quiet", action="store_true", help="only report problems")
    args = parser.parse_args(argv)

    check_manifests()
    check_skills()
    check_scripts()
    check_criteria_table()
    check_links()
    check_prose()

    if not args.quiet:
        for line in notes:
            print(f"  ok  {line}")
        print()
    for line in problems:
        print(f"FAIL  {line}", file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} problem(s).", file=sys.stderr)
        return 1
    print(f"All checks passed ({len(notes)} verified).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
