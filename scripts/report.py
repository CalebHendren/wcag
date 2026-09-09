#!/usr/bin/env python3
"""Turn findings JSON into a report, a ticket export, or a VPAT skeleton.

Takes the output of html_audit.py, axe_scan.py, pdf_audit.py, or a hand-written
findings file in the same schema, merges them, removes duplicates, and writes
one of three deliverables.

The criteria table is generated from the full WCAG 2.2 catalogue, so every
criterion at the target level appears with a status. Criteria with no finding
default to "not tested" rather than "pass", because a tool that did not look at
something has not established that it passes. Mark real passes explicitly with
--passed, or edit the table afterwards.

Usage:
  report.py findings.json --title "Checkout flow" --out audit.md
  report.py axe.json html.json --format markdown --level AA
  report.py findings.json --format csv --out tickets.csv
  report.py findings.json --format vpat --out acr.md
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import sys
from collections import Counter, OrderedDict

SEVERITY_ORDER = ["critical", "high", "medium", "low", "advisory"]

# Number, title, level, version. Generated from the W3C WCAG 2.2 guidelines
# source, so the numbering and titles match the specification exactly.
CRITERIA = [
    ("1.1.1", "Non-text Content", "A", "2.0"),
    ("1.2.1", "Audio-only and Video-only (Prerecorded)", "A", "2.0"),
    ("1.2.2", "Captions (Prerecorded)", "A", "2.0"),
    ("1.2.3", "Audio Description or Media Alternative (Prerecorded)", "A", "2.0"),
    ("1.2.4", "Captions (Live)", "AA", "2.0"),
    ("1.2.5", "Audio Description (Prerecorded)", "AA", "2.0"),
    ("1.2.6", "Sign Language (Prerecorded)", "AAA", "2.0"),
    ("1.2.7", "Extended Audio Description (Prerecorded)", "AAA", "2.0"),
    ("1.2.8", "Media Alternative (Prerecorded)", "AAA", "2.0"),
    ("1.2.9", "Audio-only (Live)", "AAA", "2.0"),
    ("1.3.1", "Info and Relationships", "A", "2.0"),
    ("1.3.2", "Meaningful Sequence", "A", "2.0"),
    ("1.3.3", "Sensory Characteristics", "A", "2.0"),
    ("1.3.4", "Orientation", "AA", "2.1"),
    ("1.3.5", "Identify Input Purpose", "AA", "2.1"),
    ("1.3.6", "Identify Purpose", "AAA", "2.1"),
    ("1.4.1", "Use of Color", "A", "2.0"),
    ("1.4.2", "Audio Control", "A", "2.0"),
    ("1.4.3", "Contrast (Minimum)", "AA", "2.0"),
    ("1.4.4", "Resize Text", "AA", "2.0"),
    ("1.4.5", "Images of Text", "AA", "2.0"),
    ("1.4.6", "Contrast (Enhanced)", "AAA", "2.0"),
    ("1.4.7", "Low or No Background Audio", "AAA", "2.0"),
    ("1.4.8", "Visual Presentation", "AAA", "2.0"),
    ("1.4.9", "Images of Text (No Exception)", "AAA", "2.0"),
    ("1.4.10", "Reflow", "AA", "2.1"),
    ("1.4.11", "Non-text Contrast", "AA", "2.1"),
    ("1.4.12", "Text Spacing", "AA", "2.1"),
    ("1.4.13", "Content on Hover or Focus", "AA", "2.1"),
    ("2.1.1", "Keyboard", "A", "2.0"),
    ("2.1.2", "No Keyboard Trap", "A", "2.0"),
    ("2.1.3", "Keyboard (No Exception)", "AAA", "2.0"),
    ("2.1.4", "Character Key Shortcuts", "A", "2.1"),
    ("2.2.1", "Timing Adjustable", "A", "2.0"),
    ("2.2.2", "Pause, Stop, Hide", "A", "2.0"),
    ("2.2.3", "No Timing", "AAA", "2.0"),
    ("2.2.4", "Interruptions", "AAA", "2.0"),
    ("2.2.5", "Re-authenticating", "AAA", "2.0"),
    ("2.2.6", "Timeouts", "AAA", "2.1"),
    ("2.3.1", "Three Flashes or Below Threshold", "A", "2.0"),
    ("2.3.2", "Three Flashes", "AAA", "2.0"),
    ("2.3.3", "Animation from Interactions", "AAA", "2.1"),
    ("2.4.1", "Bypass Blocks", "A", "2.0"),
    ("2.4.2", "Page Titled", "A", "2.0"),
    ("2.4.3", "Focus Order", "A", "2.0"),
    ("2.4.4", "Link Purpose (In Context)", "A", "2.0"),
    ("2.4.5", "Multiple Ways", "AA", "2.0"),
    ("2.4.6", "Headings and Labels", "AA", "2.0"),
    ("2.4.7", "Focus Visible", "AA", "2.0"),
    ("2.4.8", "Location", "AAA", "2.0"),
    ("2.4.9", "Link Purpose (Link Only)", "AAA", "2.0"),
    ("2.4.10", "Section Headings", "AAA", "2.0"),
    ("2.4.11", "Focus Not Obscured (Minimum)", "AA", "2.2"),
    ("2.4.12", "Focus Not Obscured (Enhanced)", "AAA", "2.2"),
    ("2.4.13", "Focus Appearance", "AAA", "2.2"),
    ("2.5.1", "Pointer Gestures", "A", "2.1"),
    ("2.5.2", "Pointer Cancellation", "A", "2.1"),
    ("2.5.3", "Label in Name", "A", "2.1"),
    ("2.5.4", "Motion Actuation", "A", "2.1"),
    ("2.5.5", "Target Size (Enhanced)", "AAA", "2.1"),
    ("2.5.6", "Concurrent Input Mechanisms", "AAA", "2.1"),
    ("2.5.7", "Dragging Movements", "AA", "2.2"),
    ("2.5.8", "Target Size (Minimum)", "AA", "2.2"),
    ("3.1.1", "Language of Page", "A", "2.0"),
    ("3.1.2", "Language of Parts", "AA", "2.0"),
    ("3.1.3", "Unusual Words", "AAA", "2.0"),
    ("3.1.4", "Abbreviations", "AAA", "2.0"),
    ("3.1.5", "Reading Level", "AAA", "2.0"),
    ("3.1.6", "Pronunciation", "AAA", "2.0"),
    ("3.2.1", "On Focus", "A", "2.0"),
    ("3.2.2", "On Input", "A", "2.0"),
    ("3.2.3", "Consistent Navigation", "AA", "2.0"),
    ("3.2.4", "Consistent Identification", "AA", "2.0"),
    ("3.2.5", "Change on Request", "AAA", "2.0"),
    ("3.2.6", "Consistent Help", "A", "2.2"),
    ("3.3.1", "Error Identification", "A", "2.0"),
    ("3.3.2", "Labels or Instructions", "A", "2.0"),
    ("3.3.3", "Error Suggestion", "AA", "2.0"),
    ("3.3.4", "Error Prevention (Legal, Financial, Data)", "AA", "2.0"),
    ("3.3.5", "Help", "AAA", "2.0"),
    ("3.3.6", "Error Prevention (All)", "AAA", "2.0"),
    ("3.3.7", "Redundant Entry", "A", "2.2"),
    ("3.3.8", "Accessible Authentication (Minimum)", "AA", "2.2"),
    ("3.3.9", "Accessible Authentication (Enhanced)", "AAA", "2.2"),
    ("4.1.2", "Name, Role, Value", "A", "2.0"),
    ("4.1.3", "Status Messages", "AA", "2.1"),
]

LEVEL_SETS = {"A": {"A"}, "AA": {"A", "AA"}, "AAA": {"A", "AA", "AAA"}}


def load(paths):
    findings, sources = [], []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            findings.extend(data)
            sources.append({"file": path, "tool": "unknown"})
        else:
            findings.extend(data.get("findings", []))
            sources.append({
                "file": path,
                "tool": data.get("tool", "unknown"),
                "url": data.get("url") or data.get("file"),
                "coverage_note": data.get("coverage_note"),
            })
    return findings, sources


CRITERIA_BY_NUMBER = {c[0]: c for c in CRITERIA}


def normalize(findings):
    """Give every finding the specification's own title and level for its SC.

    Tools name rules in their own vocabulary, for example axe's "Images must
    have alternative text". A report that mixes rule names with criterion titles
    is hard to cross-check against the standard, so the criterion wins and the
    rule name is kept alongside it.
    """
    for finding in findings:
        entry = CRITERIA_BY_NUMBER.get(finding.get("sc"))
        if not entry:
            continue
        if finding.get("sc_title") and finding["sc_title"] != entry[1]:
            finding.setdefault("rule_name", finding["sc_title"])
        finding["sc_title"] = entry[1]
        finding["level"] = entry[2]
    return findings


def dedupe(findings, keep_ids=False):
    """Drop duplicate findings and renumber the survivors.

    Renumbering keeps ids contiguous when several tools are merged, but it
    rewrites ids a person may have referenced from one finding to another. Pass
    keep_ids to leave hand-authored ids alone.
    """
    seen, unique = set(), []
    for finding in findings:
        key = (finding.get("sc"), finding.get("location"),
               finding.get("selector"), (finding.get("issue") or "")[:80])
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    unique.sort(key=lambda f: (SEVERITY_ORDER.index(f.get("severity", "medium"))
                               if f.get("severity") in SEVERITY_ORDER else 2,
                               f.get("sc", "")))
    if not keep_ids:
        for index, finding in enumerate(unique, 1):
            finding["id"] = f"F-{index:03d}"
    return unique


def criteria_status(findings, level, passed, not_applicable=frozenset()):
    """Give every criterion at the level a status.

    A criterion with no finding defaults to "Not tested" rather than "Pass",
    because a tool that did not look at something has not established anything
    about it. Genuine passes and genuine non-applicability are asserted by the
    person writing the report, through --passed and --not-applicable, so the
    default never flatters the result.
    """
    wanted = LEVEL_SETS[level]
    failed = {f.get("sc") for f in findings if f.get("confidence") != "needs-review"}
    review = {f.get("sc") for f in findings if f.get("confidence") == "needs-review"}
    rows = []
    for number, title, sc_level, version in CRITERIA:
        if sc_level not in wanted:
            continue
        if number in failed:
            status = "Fail"
        elif number in review:
            status = "Needs review"
        elif number in not_applicable:
            status = "Not applicable"
        elif number in passed:
            status = "Pass"
        else:
            status = "Not tested"
        rows.append((number, title, sc_level, version, status))
    return rows


def markdown(findings, sources, args, passed, not_applicable=frozenset()):
    today = datetime.date.today().isoformat()
    counts = Counter(f.get("severity", "medium") for f in findings)
    levels = Counter(f.get("level", "n/a") for f in findings)
    rows = criteria_status(findings, args.level, passed, not_applicable)
    status_counts = Counter(r[4] for r in rows)

    out = [f"# Accessibility audit: {args.title}", ""]
    out += [f"Tested against WCAG {args.version} Level {args.level} on {today}.", ""]

    out += ["## Scope and method", ""]
    for source in sources:
        target = source.get("url") or source["file"]
        out.append(f"- `{source['tool']}` on {target}")
    if args.scope:
        out += ["", args.scope]
    out.append("")

    out += ["## What was not tested", ""]
    not_tested = [r for r in rows if r[4] == "Not tested"]
    out.append(
        f"{len(not_tested)} of {len(rows)} Level {args.level} criteria were not "
        "evaluated in this run. A criterion with no finding has not been shown to "
        "pass, only left unchecked. Where a criterion genuinely does not apply to "
        "this target, mark it not applicable rather than leaving it here.")
    out.append("")
    if not_tested:
        out.append("Criteria still needing assessment: "
                   + ", ".join(r[0] for r in not_tested) + ".")
        out.append("")
    notes = [s.get("coverage_note") for s in sources if s.get("coverage_note")]
    for note in OrderedDict.fromkeys(notes):
        out += [f"> {note}", ""]

    out += ["## Summary", ""]
    if findings:
        summary = ", ".join(f"{counts[s]} {s}" for s in SEVERITY_ORDER if counts[s])
        out.append(f"{len(findings)} findings: {summary}.")
        out.append("")
        by_level = ", ".join(f"{levels[l]} at Level {l}"
                             for l in ("A", "AA", "AAA") if levels[l])
        if by_level:
            out += [f"By conformance level: {by_level}.", ""]
        out += ["Fix these first:", ""]
        for finding in findings[:3]:
            out.append(f"1. **{finding['sc']} {finding.get('sc_title', '')}** at "
                       f"`{finding.get('location')}`. {finding.get('issue')}")
        out.append("")
    else:
        out += ["No findings were recorded. This is not the same as conformance: "
                f"{status_counts.get('Not tested', 0)} criteria were not tested.", ""]

    out += ["## Findings", ""]
    for finding in findings:
        out.append(f"### {finding['id']}  {finding.get('sc')} "
                   f"{finding.get('sc_title', '')} ({finding.get('level')}, "
                   f"{finding.get('severity')})")
        out.append("")
        out.append(f"Location: `{finding.get('location')}`"
                   + (f"  Selector: `{finding['selector']}`"
                      if finding.get("selector") else ""))
        out.append("")
        out.append(f"{finding.get('issue')}")
        out.append("")
        if finding.get("impact"):
            out += [f"Who this affects: {finding['impact']}", ""]
        if finding.get("evidence"):
            out += ["```html", str(finding["evidence"])[:400], "```", ""]
        if finding.get("fix"):
            out += [f"Fix: {finding['fix']}", ""]
        if finding.get("verification"):
            out += [f"Verify: {finding['verification']}", ""]
        if finding.get("confidence") == "needs-review":
            out += ["This finding needs a person to confirm it.", ""]

    out += ["## Criteria assessed", "",
            f"| SC | Title | Level | Since | Status |", "|---|---|---|---|---|"]
    for number, title, sc_level, version, status in rows:
        out.append(f"| {number} | {title} | {sc_level} | {version} | {status} |")
    out.append("")

    out += ["## Conformance position", ""]
    if status_counts.get("Fail"):
        out.append(
            f"This target does not conform to WCAG {args.version} Level {args.level}. "
            f"{status_counts['Fail']} criteria failed.")
    elif status_counts.get("Not tested") or status_counts.get("Needs review"):
        out.append(
            f"No conformance claim can be made. {status_counts.get('Not tested', 0)} "
            f"criteria were not tested and {status_counts.get('Needs review', 0)} need "
            "human confirmation. Conformance requires every criterion at the level to "
            "be satisfied on every page in scope and every step of the processes in "
            "scope.")
    else:
        out.append(
            f"Every Level {args.level} criterion assessed here passed on the pages "
            "tested. Conformance for the wider site also depends on the full pages and "
            "complete processes requirements, so state the scope precisely in any claim.")
    out.append("")
    return "\n".join(out)


def vpat(findings, sources, args, passed, not_applicable=frozenset()):
    today = datetime.date.today().isoformat()
    rows = criteria_status(findings, args.level, passed, not_applicable)
    by_sc = {}
    for finding in findings:
        by_sc.setdefault(finding.get("sc"), []).append(finding)

    def conformance(status, count):
        # A real ACR distinguishes "Partially Supports" from "Does Not Support"
        # by whether some instances conform. An audit cannot settle that from
        # counts alone, so a single finding is drafted as partial and anything
        # larger as a failure. Review every row before issuing the document.
        if status == "Fail":
            return "Partially Supports" if count == 1 else "Does Not Support"
        if status == "Pass":
            return "Supports"
        if status == "Not applicable":
            return "Not Applicable"
        return "Not Evaluated"

    out = [f"# Accessibility Conformance Report: {args.title}", "",
           "Based on the VPAT structure. This is a draft prepared from an audit, not a "
           "signed vendor statement. Every row marked Not Evaluated needs testing before "
           "this document is issued.", "",
           f"Report date: {today}", f"Standard: WCAG {args.version} Level {args.level}",
           ""]
    out += ["## Evaluation methods", ""]
    for source in sources:
        out.append(f"- `{source['tool']}` on {source.get('url') or source['file']}")
    out += ["", "## WCAG success criteria", "",
            "| Criteria | Level | Conformance level | Remarks and explanations |",
            "|---|---|---|---|"]
    for number, title, sc_level, _version, status in rows:
        related = by_sc.get(number, [])
        if related:
            remark = (f"{len(related)} finding(s). "
                      + related[0].get("issue", "").replace("|", "/")[:160])
        elif status == "Not applicable":
            remark = "The product has no content or functionality this criterion covers."
        elif status == "Not tested":
            remark = "Not evaluated in this audit."
        else:
            remark = "No issues found on the pages tested."
        out.append(f"| {number} {title} | {sc_level} | "
                   f"{conformance(status, len(related))} | {remark} |")
    out.append("")
    return "\n".join(out)


def write_csv(findings, path):
    fields = ["id", "sc", "sc_title", "level", "severity", "location", "selector",
              "issue", "impact", "fix", "verification", "source", "confidence"]
    handle = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for finding in findings:
        writer.writerow(finding)
    if path:
        handle.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a report, ticket export, or VPAT draft from findings JSON.")
    parser.add_argument("findings", nargs="+", help="one or more findings JSON files")
    parser.add_argument("--format", choices=["markdown", "csv", "vpat"],
                        default="markdown")
    parser.add_argument("--title", default="Untitled target")
    parser.add_argument("--level", choices=["A", "AA", "AAA"], default="AA")
    parser.add_argument("--version", default="2.2")
    parser.add_argument("--scope", help="a paragraph describing what was in scope")
    parser.add_argument("--passed", default="",
                        help="comma separated SC numbers verified as passing")
    parser.add_argument("--not-applicable", default="", dest="not_applicable",
                        help="comma separated SC numbers with no relevant content in "
                             "this target, for example 1.2.x on a document with no media")
    parser.add_argument("--keep-ids", action="store_true", dest="keep_ids",
                        help="preserve the finding ids as written, instead of "
                             "renumbering them on merge. Use this when findings "
                             "cross-reference each other by id.")
    parser.add_argument("--out", help="write here instead of stdout")
    args = parser.parse_args(argv)

    findings, sources = load(args.findings)
    findings = dedupe(normalize(findings), keep_ids=args.keep_ids)
    passed = {s.strip() for s in args.passed.split(",") if s.strip()}
    not_applicable = {s.strip() for s in args.not_applicable.split(",") if s.strip()}
    overlap = passed & not_applicable
    if overlap:
        print(f"error: {sorted(overlap)} marked both passed and not applicable",
              file=sys.stderr)
        return 2

    if args.format == "csv":
        write_csv(findings, args.out)
        if args.out:
            print(f"Wrote {len(findings)} findings to {args.out}", file=sys.stderr)
        return 0

    text = (vpat if args.format == "vpat" else markdown)(
        findings, sources, args, passed, not_applicable)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text)
        print(f"Wrote {args.out} ({len(findings)} findings)", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
