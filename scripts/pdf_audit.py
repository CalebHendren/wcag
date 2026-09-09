#!/usr/bin/env python3
"""Structural accessibility checks on a PDF.

Covers the machine-checkable part of tagged-PDF accessibility: whether the file
is tagged at all, the document language and title, figure alternative text,
heading structure, table markup, link and form field names, bookmarks, tab
order, and whether the pages carry extractable text or are scanned images.

These map to WCAG 2.2 criteria through the W3C PDF techniques, and to the
machine-checkable subset of the Matterhorn Protocol for PDF/UA-1. The
checkpoints that need human judgement, above all whether the reading order and
the alternative text are actually correct, are listed at the end of the run as
work for a person.

Requires pypdf (pip install pypdf). Falls back to pikepdf if pypdf is absent.

Usage:
  pdf_audit.py report.pdf
  pdf_audit.py report.pdf --json > findings.json
  pdf_audit.py report.pdf --dump-tags        # print the structure tree
"""

from __future__ import annotations

import argparse
import json
import re
import sys

SEVERITY_ORDER = ["advisory", "low", "medium", "high", "critical"]

# Structure element types that carry meaning for assistive technology.
HEADING_TYPES = {f"H{n}" for n in range(1, 7)} | {"H"}
GROUPING_TYPES = {"Document", "Part", "Art", "Sect", "Div", "BlockQuote",
                  "Caption", "TOC", "TOCI", "Index", "NonStruct", "Private"}


def load_reader(path):
    try:
        from pypdf import PdfReader
        return PdfReader(path), "pypdf"
    except ImportError:
        pass
    try:
        import pikepdf  # noqa: F401
        raise SystemExit(
            "pikepdf is installed but this script reads structure through pypdf.\n"
            "Install it with:  pip install pypdf")
    except ImportError:
        raise SystemExit(
            "No PDF library found. Install one with:  pip install pypdf")


class PdfAudit:
    def __init__(self, path):
        self.path = path
        self.reader, self.backend = load_reader(path)
        self.findings = []
        self.tags = []
        self.stats = {
            "pages": len(self.reader.pages),
            "tagged": False,
            "structure_elements": 0,
            "headings": [],
            "figures": 0,
            "figures_without_alt": 0,
            "tables": 0,
            "links": 0,
            "form_fields": 0,
            "pages_without_text": [],
        }

    def add(self, sc, sc_title, level, severity, location, issue, impact, fix,
            verification, confidence="confirmed", matterhorn=None):
        self.findings.append({
            "id": f"F-{len(self.findings) + 1:03d}",
            "sc": sc,
            "sc_title": sc_title,
            "level": level,
            "severity": severity,
            "location": location,
            "selector": None,
            "issue": issue,
            "impact": impact,
            "evidence": None,
            "fix": fix,
            "verification": verification,
            "source": "tool",
            "confidence": confidence,
            "matterhorn": matterhorn,
        })

    def catalog(self):
        try:
            return self.reader.trailer["/Root"]
        except Exception:
            return {}

    def check_tagging(self):
        root = self.catalog()
        mark_info = root.get("/MarkInfo")
        marked = False
        if mark_info is not None:
            try:
                marked = bool(mark_info.get_object().get("/Marked", False))
            except Exception:
                marked = False
        has_tree = "/StructTreeRoot" in root
        self.stats["tagged"] = bool(marked and has_tree)

        if not has_tree:
            self.add("1.3.1", "Info and Relationships", "A", "critical",
                     f"{self.path} (document)",
                     "The PDF has no structure tree, so it is untagged.",
                     "Assistive technology has no headings, lists, tables, reading order, "
                     "or alternative text to work with. A screen reader can only guess at "
                     "the order of the text, and often gets it wrong.",
                     "Retag the document. Fix the source file first (in Word, InDesign, "
                     "or the authoring tool), then re-export with tagging enabled, rather "
                     "than tagging the PDF by hand.",
                     "Open the tag tree in Acrobat and confirm a full structure exists.",
                     matterhorn="01-005")
        elif not marked:
            self.add("1.3.1", "Info and Relationships", "A", "high",
                     f"{self.path} (document)",
                     "A structure tree exists but /MarkInfo /Marked is not true.",
                     "Some readers treat the file as untagged and ignore the structure "
                     "entirely.",
                     "Set the Marked flag in the document catalog.",
                     "Confirm the document reports as tagged in a PDF/UA checker.",
                     matterhorn="01-005")

    def check_metadata(self):
        root = self.catalog()
        lang = root.get("/Lang")
        if not lang:
            self.add("3.1.1", "Language of Page", "A", "high",
                     f"{self.path} (document catalog)",
                     "The document has no /Lang entry.",
                     "Screen readers use the wrong pronunciation rules for the whole "
                     "document, which can make it unintelligible.",
                     "Set the document language in the authoring tool before export, or "
                     "in the PDF properties.",
                     "Check document properties show a language.",
                     matterhorn="11-001")
        elif not re.fullmatch(r"[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*", str(lang).strip()):
            self.add("3.1.1", "Language of Page", "A", "medium",
                     f"{self.path} (document catalog)",
                     f"The document language {lang!r} is not a valid BCP 47 tag.",
                     "An invalid tag is ignored, leaving the document with no declared "
                     "language.",
                     "Set a valid tag such as en, en-GB, or fr-CA.",
                     "Validate the tag against BCP 47.")

        title = None
        try:
            info = self.reader.metadata
            title = info.title if info else None
        except Exception:
            title = None
        if not title or not str(title).strip():
            self.add("2.4.2", "Page Titled", "A", "medium",
                     f"{self.path} (document metadata)",
                     "The document has no title in its metadata.",
                     "Assistive technology and window titles fall back to the filename, "
                     "which is often meaningless.",
                     "Set a descriptive document title in the file properties.",
                     "Check the window title shows the document title, not the filename.",
                     matterhorn="07-001")
        else:
            prefs = root.get("/ViewerPreferences")
            display = None
            if prefs is not None:
                try:
                    display = prefs.get_object().get("/DisplayDocTitle")
                except Exception:
                    display = None
            if not display:
                self.add("2.4.2", "Page Titled", "A", "low",
                         f"{self.path} (viewer preferences)",
                         "DisplayDocTitle is not set, so readers show the filename "
                         "instead of the document title.",
                         "The title exists but users never see or hear it.",
                         "Set ViewerPreferences /DisplayDocTitle to true.",
                         "Open the file and confirm the window title is the document "
                         "title.",
                         matterhorn="07-002")

        if len(self.reader.pages) > 9:
            outlines = root.get("/Outlines")
            has_bookmarks = False
            if outlines is not None:
                try:
                    has_bookmarks = bool(outlines.get_object().get("/First"))
                except Exception:
                    has_bookmarks = False
            if not has_bookmarks:
                self.add("2.4.5", "Multiple Ways", "AA", "medium",
                         f"{self.path} (document)",
                         f"A {len(self.reader.pages)} page document has no bookmarks.",
                         "Readers have no way to jump between sections, so navigating a "
                         "long document means scrolling through all of it.",
                         "Generate bookmarks from the heading structure on export.",
                         "Open the bookmarks panel and confirm it mirrors the headings.")

        try:
            if self.reader.is_encrypted:
                self.add("1.3.1", "Info and Relationships", "A", "high",
                         f"{self.path} (document)",
                         "The document is encrypted. Check that the permissions allow "
                         "content extraction for accessibility.",
                         "Encryption that blocks text extraction stops screen readers "
                         "from reading the file at all.",
                         "Re-save with accessibility extraction permitted, or without "
                         "encryption.",
                         "Confirm a screen reader can read the document text.",
                         confidence="needs-review", matterhorn="26-001")
        except Exception:
            pass

    def walk_structure(self):
        root = self.catalog()
        tree = root.get("/StructTreeRoot")
        if tree is None:
            return
        try:
            tree = tree.get_object()
        except Exception:
            return
        seen = set()

        def visit(node, depth=0):
            try:
                node = node.get_object()
            except Exception:
                return
            node_id = id(node)
            if node_id in seen or depth > 60:
                return
            seen.add(node_id)

            if isinstance(node, dict) and "/S" in node:
                self.stats["structure_elements"] += 1
                stype = str(node.get("/S", "")).lstrip("/")
                alt = node.get("/Alt")
                actual = node.get("/ActualText")
                self.tags.append({
                    "depth": depth, "type": stype,
                    "alt": str(alt) if alt else None,
                    "actual_text": str(actual) if actual else None,
                })
                self.inspect_element(stype, node, depth)

            children = None
            if isinstance(node, dict):
                children = node.get("/K")
            if children is None:
                return
            try:
                children = children.get_object()
            except Exception:
                pass
            if isinstance(children, list):
                for child in children:
                    visit(child, depth + 1)
            elif isinstance(children, dict):
                visit(children, depth + 1)

        visit(tree, 0)

    def inspect_element(self, stype, node, depth):
        if stype in HEADING_TYPES:
            self.stats["headings"].append(stype)
        elif stype == "Figure":
            self.stats["figures"] += 1
            alt = node.get("/Alt")
            actual = node.get("/ActualText")
            text = (str(alt) if alt else "") or (str(actual) if actual else "")
            if not text.strip():
                self.stats["figures_without_alt"] += 1
                self.add("1.1.1", "Non-text Content", "A", "high",
                         f"{self.path} (Figure element, depth {depth})",
                         "A Figure structure element has no /Alt or /ActualText.",
                         "The image is announced as a figure with nothing to describe it, "
                         "so its information is lost.",
                         "Add alternative text in the authoring tool and re-export, or "
                         "add /Alt to the Figure tag.",
                         "Read the alt aloud with the image hidden and check it conveys "
                         "the same information.",
                         matterhorn="13-004")
            elif text.strip().lower() in ("image", "figure", "graphic", "picture",
                                          "photo", "logo", "chart", "img"):
                self.add("1.1.1", "Non-text Content", "A", "medium",
                         f"{self.path} (Figure element, depth {depth})",
                         f'The figure alternative text is "{text.strip()}", which names '
                         "the medium rather than the content.",
                         "A reader learns an image is present but not what it shows.",
                         "Replace it with what the image conveys in context.",
                         "Read the alt aloud and check it stands in for the image.")
        elif stype == "Table":
            self.stats["tables"] += 1
        elif stype == "Link":
            self.stats["links"] += 1
        elif stype == "Form":
            self.stats["form_fields"] += 1

    def check_headings(self):
        levels = []
        for tag in self.tags:
            if tag["type"] in HEADING_TYPES and tag["type"] != "H":
                levels.append(int(tag["type"][1:]))
        if self.stats["tagged"] and not levels and self.stats["pages"] > 1:
            self.add("1.3.1", "Info and Relationships", "A", "high",
                     f"{self.path} (structure tree)",
                     "The tagged document contains no heading elements.",
                     "Readers cannot navigate by heading, so a long document has to be "
                     "read start to finish.",
                     "Apply real heading styles in the source document and re-export. "
                     "Text made large and bold is not a heading.",
                     "Open the tag tree and confirm headings appear at the right levels.")
            return
        previous = 0
        for index, level in enumerate(levels):
            if previous and level > previous + 1:
                self.add("1.3.1", "Info and Relationships", "A", "medium",
                         f"{self.path} (heading {index + 1} in the structure tree)",
                         f"The heading level jumps from H{previous} to H{level}.",
                         "A skipped level makes the document outline wrong and suggests "
                         "missing content.",
                         f"Change the heading to H{previous + 1}, or add the missing "
                         "intermediate heading in the source document.",
                         "Review the tag tree outline for levels descending by one.",
                         matterhorn="14-002")
            previous = level

    def check_tables(self):
        types = [t["type"] for t in self.tags]
        if "Table" in types and "TH" not in types:
            self.add("1.3.1", "Info and Relationships", "A", "high",
                     f"{self.path} (structure tree)",
                     f"{self.stats['tables']} table(s) are tagged but no TH header cells "
                     "exist.",
                     "Screen reader users hear cell values with no headers, so the table "
                     "becomes an undifferentiated list of values.",
                     "Mark the header row and column as header cells in the source "
                     "document, and set the scope on each.",
                     "Navigate the table with a screen reader and confirm each cell "
                     "announces its headers.",
                     matterhorn="15-003")

    def check_text_layer(self):
        empty = []
        for index, page in enumerate(self.reader.pages, 1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            if len(text.strip()) < 10:
                empty.append(index)
        self.stats["pages_without_text"] = empty
        if not empty:
            return
        if len(empty) == self.stats["pages"]:
            self.add("1.1.1", "Non-text Content", "A", "critical",
                     f"{self.path} (all {self.stats['pages']} pages)",
                     "No page contains extractable text. The document appears to be a "
                     "scan or a set of images.",
                     "There is nothing for a screen reader to read, nothing to search, "
                     "and nothing that reflows when magnified. The document is entirely "
                     "unavailable to blind readers.",
                     "Run OCR to produce a real text layer, correct the recognition "
                     "errors, then tag the structure. Where the original source file "
                     "exists, re-export from it instead, which gives a better result.",
                     "Select and copy text from each page, and confirm it matches what "
                     "is printed.")
        else:
            pages = ", ".join(str(p) for p in empty[:12])
            more = f" and {len(empty) - 12} more" if len(empty) > 12 else ""
            self.add("1.1.1", "Non-text Content", "A", "high",
                     f"{self.path} (pages {pages}{more})",
                     f"{len(empty)} of {self.stats['pages']} pages contain no extractable "
                     "text.",
                     "Those pages are invisible to screen readers and to search.",
                     "OCR the image-only pages, or replace them with tagged text.",
                     "Copy text from each listed page and confirm it is present.")

    def check_page_setup(self):
        for index, page in enumerate(self.reader.pages, 1):
            try:
                tabs = page.get("/Tabs")
            except Exception:
                continue
            if self.stats["tagged"] and tabs is not None and str(tabs) != "/S":
                self.add("2.4.3", "Focus Order", "A", "medium",
                         f"{self.path} page {index}",
                         f"The page tab order is {tabs} rather than /S (structure order).",
                         "Keyboard focus moves through links and form fields in an order "
                         "unrelated to the reading order.",
                         "Set the page tab order to follow the document structure.",
                         "Tab through the page and confirm the order matches the reading "
                         "order.",
                         matterhorn="04-001")
            elif self.stats["tagged"] and tabs is None:
                self.add("2.4.3", "Focus Order", "A", "low",
                         f"{self.path} page {index}",
                         "The page has no /Tabs entry, so tab order is left to the "
                         "reader application.",
                         "Focus order may not follow the reading order.",
                         "Set /Tabs to /S on every page.",
                         "Tab through the page and check the order.",
                         confidence="needs-review", matterhorn="04-001")

    def check_forms(self):
        root = self.catalog()
        acro = root.get("/AcroForm")
        if acro is None:
            return
        try:
            fields = acro.get_object().get("/Fields", [])
        except Exception:
            return
        unnamed = 0
        total = 0
        for field in fields:
            try:
                obj = field.get_object()
            except Exception:
                continue
            total += 1
            if not obj.get("/TU"):
                unnamed += 1
        self.stats["form_fields"] = max(self.stats["form_fields"], total)
        if unnamed:
            self.add("1.3.1", "Info and Relationships", "A", "critical",
                     f"{self.path} (AcroForm)",
                     f"{unnamed} of {total} form fields have no tooltip (/TU), which is "
                     "the accessible name for a PDF field.",
                     "Screen reader users hear the field type with no indication of what "
                     "to enter, so the form cannot be completed.",
                     "Set the tooltip on each field to the visible label text.",
                     "Tab through the form with a screen reader and confirm every field "
                     "announces its label.",
                     matterhorn="15-005")

    def run(self):
        self.check_tagging()
        self.check_metadata()
        self.walk_structure()
        self.check_headings()
        self.check_tables()
        self.check_text_layer()
        self.check_forms()
        if self.stats["tagged"]:
            self.check_page_setup()
        self.findings.sort(key=lambda f: -SEVERITY_ORDER.index(f["severity"]))
        for index, finding in enumerate(self.findings, 1):
            finding["id"] = f"F-{index:03d}"
        return self.findings


MANUAL_CHECKS = [
    "Reading order: read the whole document with a screen reader, or use the Order "
    "panel. Tag order that looks right in a tree can still read a two-column page "
    "across instead of down. (1.3.2)",
    "Alternative text quality: does each figure's alt convey what the figure conveys, "
    "in context? Charts usually need a long description or an adjacent data table. (1.1.1)",
    "Colour and contrast: measure text against its background with scripts/contrast.py. "
    "PDF structure carries no colour information. (1.4.3, 1.4.11)",
    "Colour as the only cue: check for status, required fields, or chart series shown by "
    "colour alone. (1.4.1)",
    "Table complexity: tables with merged cells or two header levels need headers/id "
    "associations, not just scope. (1.3.1)",
    "Link text: does each link say where it goes when read on its own? (2.4.4)",
    "Artifacts: are page numbers, running heads, and decorative rules marked as "
    "artifacts rather than read as content? (1.3.1)",
    "Lists: are bulleted lists tagged as L / LI / LBody rather than as paragraphs? (1.3.1)",
    "Language of parts: are passages in another language tagged with their own "
    "language? (3.1.2)",
    "Scanned text quality: where OCR was used, spot-check that the text layer matches "
    "the printed words. (1.1.1)",
]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Structural accessibility checks on a PDF (WCAG 2.2 and PDF/UA).")
    parser.add_argument("path", help="PDF file")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--dump-tags", action="store_true",
                        help="print the structure tree instead of findings")
    args = parser.parse_args(argv)

    audit = PdfAudit(args.path)
    findings = audit.run()

    if args.dump_tags:
        if not audit.tags:
            print("No structure tree. The document is untagged.")
            return 0
        for tag in audit.tags:
            marker = ""
            if tag["alt"]:
                marker = f'  /Alt="{tag["alt"][:70]}"'
            elif tag["actual_text"]:
                marker = f'  /ActualText="{tag["actual_text"][:70]}"'
            print("  " * tag["depth"] + tag["type"] + marker)
        return 0

    if args.as_json:
        print(json.dumps({
            "tool": "pdf_audit.py",
            "standard": "WCAG 2.2 and PDF/UA-1",
            "file": args.path,
            "stats": audit.stats,
            "findings": findings,
            "manual_checks_required": MANUAL_CHECKS,
        }, indent=2))
        return 0

    stats = audit.stats
    print(f"{args.path}")
    print(f"  pages              {stats['pages']}")
    print(f"  tagged             {'yes' if stats['tagged'] else 'NO'}")
    print(f"  structure elements {stats['structure_elements']}")
    print(f"  headings           {len(stats['headings'])}")
    print(f"  figures            {stats['figures']} "
          f"({stats['figures_without_alt']} without alt)")
    print(f"  tables             {stats['tables']}")
    print(f"  form fields        {stats['form_fields']}")
    if stats["pages_without_text"]:
        print(f"  pages with no text {len(stats['pages_without_text'])}")
    print()

    if not findings:
        print("No structural findings.")
    for finding in findings:
        print(f"[{finding['severity'].upper():8}] {finding['sc']} "
              f"{finding['sc_title']} ({finding['level']})")
        print(f"           {finding['location']}")
        print(f"           {finding['issue']}")
        print(f"           Fix: {finding['fix']}\n")

    print("Still to check by hand, because no tool can judge these:")
    for check in MANUAL_CHECKS:
        print(f"  - {check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
