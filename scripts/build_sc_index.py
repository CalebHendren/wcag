#!/usr/bin/env python3
"""Generate references/sc-index.md from the criteria table in report.py.

The index is the one place that lists every WCAG 2.2 guideline and success
criterion together, so an agent building the criteria table for a report does
not have to load four catalogue files to find out what is on it. It is
generated rather than written, because a hand-maintained second copy of the
specification's numbering drifts from the first one.

Run it after changing CRITERIA in report.py. selfcheck.py fails if the file on
disk does not match what this script would produce.

Usage:
  build_sc_index.py            # write references/sc-index.md
  build_sc_index.py --check    # exit 1 if the file is out of date
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "references/sc-index.md"

PRINCIPLES = {
    "1": ("Perceivable", "sc-perceivable.md"),
    "2": ("Operable", "sc-operable.md"),
    "3": ("Understandable", "sc-understandable.md"),
    "4": ("Robust", "sc-robust.md"),
}

HEADER = """# Every WCAG 2.2 guideline and success criterion

The complete list: 4 principles, 13 guidelines, and 86 success criteria, at 31 Level A, 24
Level AA, and 31 Level AAA. 4.1.1 Parsing was removed in WCAG 2.2 and is listed at the end
rather than in the table, because reporting a failure against it in a 2.2 audit is wrong.

Read this file when you need the whole list at once: building the criteria table for a
report, checking that nothing at the target level went unconsidered, or answering which
criteria a level contains. For what a criterion means, how to test it, and what actually
fails it, read the catalogue file named in the last column.

`New` marks the nine criteria added in WCAG 2.2. A target audited against 2.2 is assessed
against all of these; a target audited against 2.1 is not.
"""

FOOTER = """
## Removed in WCAG 2.2

**4.1.1 Parsing** was obsoleted in WCAG 2.1 and removed in WCAG 2.2. Do not report a
finding against it in a 2.2 audit. Where a duplicate `id` or malformed markup actually
breaks a label association or an ARIA reference, report it under 1.3.1 or 4.1.2 and name
the consequence. An audit against WCAG 2.0 or 2.1, for a legal regime that cites one of
those versions, may still have to address it.

## Counts by level

| Level | Criteria | Cumulative |
|---|---|---|
| A | 31 | 31 |
| AA | 24 | 55 |
| AAA | 31 | 86 |

Level AA conformance requires every Level A and every Level AA criterion to be satisfied,
which is 55 criteria. `conformance.md` covers what a claim at each level may say.
"""


def guideline_titles() -> dict[str, str]:
    """Read the guideline headings out of the catalogue files."""
    titles: dict[str, str] = {}
    for _principle, (_name, filename) in PRINCIPLES.items():
        path = ROOT / "references" / filename
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"^## Guideline (\d+\.\d+) (.+)$", text, re.M):
            titles[match.group(1)] = match.group(2).strip()
    return titles


def load_criteria() -> list[tuple[str, str, str, str]]:
    report = ROOT / "scripts/report.py"
    namespace: dict = {}
    exec(compile(report.read_text(encoding="utf-8"), str(report), "exec"),
         {"__name__": "build_sc_index"}, namespace)
    return list(namespace["CRITERIA"])


def sort_key(number: str) -> tuple[int, ...]:
    return tuple(int(part) for part in number.split("."))


def render() -> str:
    criteria = sorted(load_criteria(), key=lambda c: sort_key(c[0]))
    titles = guideline_titles()
    out = [HEADER]
    current_principle = None
    current_guideline = None
    for number, title, level, version in criteria:
        principle = number.split(".")[0]
        guideline = number.rsplit(".", 1)[0]
        if principle != current_principle:
            name, filename = PRINCIPLES[principle]
            out.append(f"## {principle}. {name}\n")
            current_principle = principle
            current_guideline = None
        if guideline != current_guideline:
            heading = titles.get(guideline, "")
            if current_guideline is not None:
                out.append("")
            out.append(f"### Guideline {guideline} {heading}".rstrip() + "\n")
            out.append("| Criterion | Title | Level | Added | Detail |")
            out.append("|---|---|---|---|---|")
            current_guideline = guideline
        filename = PRINCIPLES[principle][1]
        added = "New in 2.2" if version == "2.2" else version
        out.append(f"| {number} | {title} | {level} | {added} | `{filename}` |")
    return "\n".join(out).rstrip() + "\n" + FOOTER


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the WCAG 2.2 criteria index from report.py.")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if references/sc-index.md is out of date")
    args = parser.parse_args(argv)

    wanted = render()
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != wanted:
            print("references/sc-index.md is out of date. Run "
                  "python3 scripts/build_sc_index.py", file=sys.stderr)
            return 1
        print("references/sc-index.md is current.")
        return 0
    OUTPUT.write_text(wanted, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
