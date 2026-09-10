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


def merged_attributes(node) -> dict:
    """Return the structure element's /A attribute dictionaries, merged.

    /A is either one dictionary or an array of them, optionally interleaved
    with revision numbers. Table properties such as Scope, RowSpan, ColSpan and
    Headers live here rather than as direct keys on the element, which is why
    looking for node["/Scope"] finds nothing on a correctly built file and
    nothing on a broken one alike.
    """
    raw = node.get("/A")
    if raw is None:
        return {}
    try:
        raw = raw.get_object()
    except Exception:
        return {}
    merged = {}
    for entry in (raw if isinstance(raw, list) else [raw]):
        try:
            entry = entry.get_object()
        except Exception:
            continue
        if isinstance(entry, dict):
            for key in entry:
                try:
                    merged[str(key)] = entry[key]
                except Exception:
                    pass
    return merged


def _int_attr(attrs: dict, name: str, default: int = 1) -> int:
    value = attrs.get(name, default)
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return default


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
        self.tables = []
        self.stats = {
            "pages": len(self.reader.pages),
            "tagged": False,
            "structure_elements": 0,
            "headings": [],
            "figures": 0,
            "figures_without_alt": 0,
            "tables": 0,
            "table_cells": 0,
            "header_cells": 0,
            "header_cells_with_scope": 0,
            "data_cells_with_headers": 0,
            "cells_with_spans": 0,
            "untagged_content": 0,
            "artifact_text_share": 0.0,
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

    def collect_tables(self):
        """Read every Table element into rows of (kind, attributes)."""
        root = self.catalog()
        tree = root.get("/StructTreeRoot")
        if tree is None:
            return
        try:
            tree = tree.get_object()
        except Exception:
            return
        seen = set()

        def children(node):
            kids = node.get("/K") if isinstance(node, dict) else None
            if kids is None:
                return []
            try:
                kids = kids.get_object()
            except Exception:
                pass
            return kids if isinstance(kids, list) else [kids]

        def read_table(node):
            rows = []

            def descend(current, row=None, depth=0):
                try:
                    current = current.get_object()
                except Exception:
                    return
                if not isinstance(current, dict) or depth > 40:
                    return
                if id(current) in seen:
                    return
                seen.add(id(current))
                kind = str(current.get("/S", "")).lstrip("/")
                if kind == "TR":
                    row = []
                    rows.append(row)
                elif kind in ("TH", "TD") and row is not None:
                    row.append((kind, merged_attributes(current)))
                for child in children(current):
                    if not isinstance(child, int):
                        descend(child, row, depth + 1)

            descend(node)
            return rows

        def find_tables(node, depth=0):
            try:
                node = node.get_object()
            except Exception:
                return
            if not isinstance(node, dict) or depth > 60:
                return
            if str(node.get("/S", "")).lstrip("/") == "Table":
                self.tables.append(read_table(node))
                return
            for child in children(node):
                if not isinstance(child, int):
                    find_tables(child, depth + 1)

        find_tables(tree)

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
        """Check header association, not just header presence.

        A table can carry every TH the standard asks for and still tell a screen
        reader nothing, because the association between a header and the cells it
        governs lives in /Scope, or in /Headers and /ID for anything complex. A
        check that only asks whether TH exists passes exactly the tables that fail
        their readers.
        """
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
            return

        for index, rows in enumerate(self.tables, 1):
            if not rows:
                continue
            label = (f"{self.path} (table {index} of {len(self.tables)})"
                     if len(self.tables) > 1 else f"{self.path} (the table)")
            cells = [cell for row in rows for cell in row]
            headers = [c for c in cells if c[0] == "TH"]
            data = [c for c in cells if c[0] == "TD"]
            self.stats["table_cells"] += len(cells)
            self.stats["header_cells"] += len(headers)
            if not headers:
                continue

            scoped = [c for c in headers if c[1].get("/Scope")]
            identified = [c for c in headers if c[1].get("/ID")]
            associated = [c for c in data if c[1].get("/Headers")]
            spanned = [c for c in cells
                       if c[1].get("/RowSpan") or c[1].get("/ColSpan")]
            self.stats["header_cells_with_scope"] += len(scoped)
            self.stats["data_cells_with_headers"] += len(associated)
            self.stats["cells_with_spans"] += len(spanned)

            # A table with headers down the first column as well as across the top
            # needs more than scope, and gets those wrong more often.
            first_row_headers = sum(1 for c in rows[0] if c[0] == "TH") if rows else 0
            row_headers = sum(1 for row in rows[1:] if row and row[0][0] == "TH")
            both_axes = first_row_headers > 1 and row_headers > 1

            if not scoped and not identified and not associated:
                self.add("1.3.1", "Info and Relationships", "A",
                         "critical" if both_axes else "high", label,
                         f"None of the {len(headers)} header cells carry /Scope, and "
                         f"none of the {len(data)} data cells carry /Headers. The cells "
                         "are typed TH and TD, but nothing says which header governs "
                         "which cell.",
                         "A screen reader announces cell contents with no header "
                         "attached, so the reader gets values with nothing to attach "
                         "them to."
                         + (" This table has headers on both axes, so every cell needs "
                            "two headers and currently has none." if both_axes else ""),
                         "Mark the header row and header column in the source document "
                         "and re-export, so each TH carries Scope. A table with headers "
                         "on both axes usually also needs Headers and ID associations.",
                         "Navigate the table cell by cell with a screen reader and "
                         "confirm each cell announces the headers that govern it.",
                         matterhorn="15-003")
            elif len(scoped) < len(headers) and not associated:
                self.add("1.3.1", "Info and Relationships", "A", "medium", label,
                         f"{len(headers) - len(scoped)} of {len(headers)} header cells "
                         "carry no /Scope.",
                         "The unscoped headers are left for the reader to guess at, and "
                         "readers guess differently.",
                         "Set the scope on every header cell.",
                         "Confirm each cell announces the right row and column header.")

            if both_axes and not associated and len(data) > 12:
                self.add("1.3.1", "Info and Relationships", "A", "high", label,
                         f"The table has headers on both axes and {len(data)} data "
                         "cells, but no data cell carries /Headers associations.",
                         "Scope alone resolves a grid only when the layout is regular. "
                         "In a table this size a reader that guesses wrong attaches the "
                         "wrong header to the value.",
                         "Give each header an /ID and each data cell a /Headers array "
                         "naming the headers that govern it.",
                         "Spot-check cells in the middle of the table and confirm both "
                         "headers are announced.",
                         confidence="needs-review", matterhorn="15-004")

            # Rows narrower than the table imply merged cells. Undeclared, the
            # reader fills columns left to right and every later cell shifts.
            widths = []
            for row in rows:
                widths.append(sum(_int_attr(a, "/ColSpan") for _kind, a in row))
            if widths:
                expected = max(widths)
                short = [i for i, w in enumerate(widths) if w < expected]
                if short and not spanned and expected > 1:
                    sample = ", ".join(f"row {i + 1} has {widths[i]}" for i in short[:4])
                    self.add("1.3.1", "Info and Relationships", "A", "critical", label,
                             f"{len(short)} of {len(rows)} rows hold fewer cells than "
                             f"the table's {expected} columns ({sample}), and no cell "
                             "declares /RowSpan or /ColSpan.",
                             "The merged cells the layout depends on are invisible to "
                             "assistive technology, so the reader fills columns left to "
                             "right and every cell after a merge is attributed to the "
                             "wrong column. A user is told a value belongs to a column "
                             "it does not, which is worse than being told nothing "
                             "because the answer sounds authoritative.",
                             "Re-export so merged cells declare their spans. Where the "
                             "exporter keeps dropping them, simplify the source table "
                             "so one visual row is one table row.",
                             "Confirm every row reports the full column count, counting "
                             "declared spans, and that a screen reader names the correct "
                             "column for cells after a merge.",
                             matterhorn="15-005")
                elif short and spanned:
                    self.add("1.3.1", "Info and Relationships", "A", "medium", label,
                             f"{len(short)} of {len(rows)} rows are narrower than the "
                             f"table's {expected} columns even after counting the "
                             f"{len(spanned)} declared spans.",
                             "Some merges are declared and some are not, so part of the "
                             "grid resolves correctly and part does not.",
                             "Check the source table for merged cells whose spans did "
                             "not survive the export.",
                             "Confirm every row resolves to the full column count.",
                             confidence="needs-review", matterhorn="15-005")

    def check_untagged_content(self):
        """Find content that is neither tagged nor marked as an artifact.

        PDF/UA asks every piece of page content to be one or the other. Content in
        neither state is skipped by readers that navigate the tag tree, which looks
        like the right outcome when the content is decorative and is silent data loss
        when it is not. Either way it is a defect, because nothing declared the
        intent.
        """
        if not self.stats["tagged"]:
            return
        referenced = set()
        seen = set()

        def walk(node, depth=0):
            try:
                node = node.get_object()
            except Exception:
                return
            if not isinstance(node, dict) or id(node) in seen or depth > 60:
                return
            seen.add(id(node))
            kids = node.get("/K")
            if kids is None:
                return
            try:
                kids = kids.get_object()
            except Exception:
                pass
            for child in (kids if isinstance(kids, list) else [kids]):
                if isinstance(child, int):
                    referenced.add(child)
                else:
                    walk(child, depth + 1)

        tree = self.catalog().get("/StructTreeRoot")
        if tree is None:
            return
        walk(tree)

        drawn, artifacts = set(), set()
        for page in self.reader.pages:
            try:
                data = page.get_contents().get_data().decode("latin-1", "replace")
            except Exception:
                continue
            drawn |= {int(n) for n in
                      re.findall(r"<<\s*/MCID\s+(\d+)\s*>>\s*BDC", data)}
            artifacts |= {int(m.group(1)) for m in re.finditer(
                r"/Artifact\s*<<\s*/MCID\s+(\d+)\s*>>\s*BDC", data)}

        orphans = sorted((drawn - referenced) - artifacts)
        self.stats["untagged_content"] = len(orphans)
        if not orphans:
            return
        listed = ", ".join(str(o) for o in orphans[:10])
        more = f" and {len(orphans) - 10} more" if len(orphans) > 10 else ""
        self.add("1.3.1", "Info and Relationships", "A", "medium",
                 f"{self.path} (marked content {listed}{more})",
                 f"{len(orphans)} piece(s) of page content are neither referenced by "
                 "the structure tree nor marked as an artifact.",
                 "Readers that navigate the tag tree skip this content entirely. That is "
                 "the right outcome if it is decorative and silent data loss if it is "
                 "not, and nothing in the file says which.",
                 "Mark decorative items as artifacts in the authoring tool, and tag "
                 "anything that carries information so it joins the structure tree.",
                 "Re-run this check and confirm every drawn item is either tagged or "
                 "artifacted.",
                 confidence="needs-review", matterhorn="01-006")

    def check_artifacted_text(self):
        """Flag pages where a large share of the visible text is inside artifacts.

        Marking content as an artifact tells assistive technology to skip it, which
        is right for page numbers and running heads and wrong for anything a reader
        needs. No tool can judge which is which, but the proportion is a strong
        signal: a page whose text is mostly artifacts is either heavily decorated or
        has had real content hidden, and both are worth a human look. Exporters do
        this to text boxes and drawing labels, so the content most often lost is
        exactly the labels that say what a diagram or a blank means.
        """
        if not self.stats["tagged"]:
            return
        tagged_total = artifact_total = 0
        flagged = []
        for number, page in enumerate(self.reader.pages, 1):
            try:
                data = page.get_contents().get_data().decode("latin-1", "replace")
            except Exception:
                continue
            tagged_chars, artifact_chars, samples = 0, 0, []
            # Each entry is the kind of marked content we are inside: "tagged" for a
            # BDC carrying an MCID, "artifact" for an Artifact marker, "other" for
            # anything else. Text outside every marker is neither tagged nor
            # artifacted; check_untagged_content already reports that case, and
            # counting it here would flag any page that simply uses no markers.
            stack = []
            token = re.compile(
                r"/(\w+)\s*<<[^>]*?/MCID\s+\d+[^>]*?>>\s*BDC|/(\w+)\s*<<[^>]*?>>\s*BDC|"
                r"/(\w+)\s*BMC|\bEMC\b|"
                r"\[((?:[^\]\\]|\\.)*)\]\s*TJ|\(((?:[^()\\]|\\.)*)\)\s*Tj")
            for match in token.finditer(data):
                piece = match.group(0)
                if piece.endswith("BDC") and match.group(1):
                    stack.append("artifact" if match.group(1) == "Artifact" else "tagged")
                elif piece.endswith("BDC"):
                    stack.append("artifact" if match.group(2) == "Artifact" else "other")
                elif piece.endswith("BMC"):
                    stack.append("artifact" if match.group(3) == "Artifact" else "other")
                elif piece == "EMC":
                    if stack:
                        stack.pop()
                else:
                    raw = match.group(5)
                    if raw is None:
                        raw = "".join(re.findall(r"\(((?:[^()\\]|\\.)*)\)",
                                                match.group(4) or ""))
                    text = re.sub(r"\\([()\\])", r"\1", raw).strip()
                    if not text or not stack:
                        continue
                    if stack[-1] == "tagged":
                        tagged_chars += len(text)
                    elif stack[-1] == "artifact":
                        artifact_chars += len(text)
                        if len(samples) < 6:
                            samples.append(text[:24])
            tagged_total += tagged_chars
            artifact_total += artifact_chars
            visible = tagged_chars + artifact_chars
            if visible and artifact_chars > 60 and artifact_chars / visible > 0.25:
                flagged.append((number, round(100 * artifact_chars / visible), samples))

        visible_total = tagged_total + artifact_total
        if visible_total:
            self.stats["artifact_text_share"] = round(
                100 * artifact_total / visible_total, 1)
        if not flagged:
            return
        pages = ", ".join(f"page {n} ({pct}%)" for n, pct, _ in flagged[:8])
        more = f" and {len(flagged) - 8} more" if len(flagged) > 8 else ""
        sample = "; ".join(flagged[0][2][:5])
        self.add("1.3.1", "Info and Relationships", "A", "high",
                 f"{self.path} ({pages}{more})",
                 f"{len(flagged)} page(s) carry more than a quarter of their visible "
                 "text inside artifacts, which assistive technology skips. On "
                 f"page {flagged[0][0]} the skipped text includes: {sample}.",
                 "Anything a reader needs that is marked as an artifact is invisible to "
                 "them, and no error is raised. If those strings carry data or label "
                 "something, the document cannot be used by a screen reader for its "
                 "purpose, however well the rest of it is tagged.",
                 "Read the skipped text. Artifact only what is genuinely decorative, "
                 "and tag the rest as content in the authoring tool.",
                 "Confirm every string a reader needs is reachable through the "
                 "structure tree.",
                 confidence="needs-review", matterhorn="01-003")

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
        self.collect_tables()
        self.check_tables()
        self.check_untagged_content()
        self.check_artifacted_text()
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
    "Table complexity: where the script reports missing /Headers on a two-axis table, "
    "confirm against the visual grid which headers each cell actually needs. (1.3.1)",
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
    if stats["header_cells"]:
        print(f"  header cells       {stats['header_cells']} "
              f"({stats['header_cells_with_scope']} with scope)")
        print(f"  data cells assoc.  {stats['data_cells_with_headers']} "
              f"of {stats['table_cells'] - stats['header_cells']} carry /Headers")
        print(f"  cells with spans   {stats['cells_with_spans']}")
    if stats.get("artifact_text_share"):
        print(f"  text in artifacts  {stats['artifact_text_share']}% of visible text")
    if stats.get("untagged_content"):
        print(f"  untagged content   {stats['untagged_content']} item(s) neither "
              "tagged nor artifacted")
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
