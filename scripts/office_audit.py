#!/usr/bin/env python3
"""Structural accessibility checks on a Word, PowerPoint, or Excel file.

Office files are ZIP archives of XML, so the structure that decides whether a
document works for a screen reader can be read without the authoring
application: which paragraphs are real headings, whether a table declares a
header row, whether an image carries alternative text, whether a slide has a
title, what the document language is.

Every finding carries an `agent_fix` value saying who can actually close it:
`direct` for what an agent can apply itself, `app` for what needs the authoring
application, `recreate` for what cannot be repaired in place at all, `owner` for
content only the author has, and `design` for a decision someone has to make.
An audit that does not separate these is a list of homework.

This is the tool pass, and it is a small part of the audit. It cannot tell you
whether alt text is accurate, whether the reading order matches the meaning, or
whether a heading describes its section. Run the application's own accessibility
checker as well where you can reach it, and see references/builtin-checkers.md.

Standard library only. No network, no Office, no LibreOffice.

Usage:
  office_audit.py report.docx
  office_audit.py deck.pptx --json > findings.json
  office_audit.py report.docx --dump-outline     # headings, slide or sheet names
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

# A part larger than this is refused rather than parsed. Real documents do not
# reach it, and a decompression bomb should not take the machine down.
MAX_PART_BYTES = 64 * 1024 * 1024

OLE_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

KIND_BY_SUFFIX = {
    ".docx": "docx", ".docm": "docx", ".dotx": "docx", ".dotm": "docx",
    ".pptx": "pptx", ".pptm": "pptx", ".potx": "pptx", ".ppsx": "pptx",
    ".xlsx": "xlsx", ".xlsm": "xlsx", ".xltx": "xlsx",
}

LEGACY_BY_SUFFIX = {".doc": "Word", ".ppt": "PowerPoint", ".xls": "Excel"}

GENERIC_LINK_TEXT = {
    "click here", "here", "read more", "more", "link", "this link", "this",
    "learn more", "see more", "details", "download", "continue", "go",
    "click", "info", "more info", "read this",
}

DEFAULT_SHEET_NAME = re.compile(r"^(sheet|blad|hoja|feuil|tabelle|foglio)\s*\d+$", re.I)

MANUAL_LIST_START = re.compile(
    r"^\s*(?:[-*•▪·o]\s+|\(?\d{1,2}[.)]\s+|\(?[a-z][.)]\s+)")

BARE_URL = re.compile(r"^(https?://|www\.)\S*$", re.I)

MANUAL_CHECKS = [
    "Is each alternative text accurate and useful, rather than merely present",
    "Does the reading order match the visual order and the meaning, on every "
    "slide and around every floating object",
    "Do the headings describe the sections they introduce, in a sensible outline",
    "Does the link text say where it goes when read on its own",
    "Is any meaning carried by color alone, in tracked changes, highlighted "
    "rows, or negative figures shown in red",
    "Does the text meet contrast against its actual background, including "
    "themed templates and text over images",
    "Are passages in another language marked with that language",
    "Does the exported PDF keep the tags, the language, and the title",
]


def alt_candidates(container: ET.Element, where: str,
                   found: list | None = None) -> list[tuple[str, str, str | None]]:
    """Objects inside a DrawingML shape tree that need alternative text.

    Pictures and graphic frames need it. Text shapes do not, because their text
    is already text. A table in a graphic frame does not, because its cells
    carry the content. A group carrying its own description is one object; a
    group without one is a container whose children each need their own.
    """
    found = [] if found is None else found
    for child in container:
        name = local(child.tag)
        if name not in ("pic", "graphicFrame", "grpSp", "sp"):
            continue
        properties = next((e for e in child.iter() if local(e.tag) == "cNvPr"), None)
        descr = attr(properties, "descr") if properties is not None else None
        shape_name = (attr(properties, "name") if properties is not None else None) \
            or name
        if name == "grpSp":
            if (descr or "").strip():
                found.append((where, shape_name, descr))
            else:
                alt_candidates(child, where, found)
            continue
        if name == "sp":
            continue
        if name == "graphicFrame" and any(local(e.tag) == "tbl" for e in child.iter()):
            continue
        found.append((where, shape_name, descr))
    return found


class PackageError(Exception):
    """The file cannot be opened for auditing, and why."""

    def __init__(self, reason: str, remedy: str, agent_fix: str):
        super().__init__(reason)
        self.reason = reason
        self.remedy = remedy
        self.agent_fix = agent_fix


def local(tag: str) -> str:
    """The local name of a namespaced ElementTree tag."""
    return tag.rsplit("}", 1)[-1]


def attr(element: ET.Element, name: str) -> str | None:
    """An attribute by local name, whichever namespace prefix carries it."""
    for key, value in element.attrib.items():
        if local(key) == name:
            return value
    return None


def identify(path: pathlib.Path) -> str:
    suffix = path.suffix.lower()
    if suffix in LEGACY_BY_SUFFIX:
        raise PackageError(
            f"{path.name} is a legacy {LEGACY_BY_SUFFIX[suffix]} binary file, which "
            "carries no XML package to read or repair.",
            "Convert it to the modern format first, for example with "
            f"`soffice --headless --convert-to {suffix.lstrip('.')}x`, audit the "
            "converted copy, and say in the report that a conversion happened.",
            "app")
    with path.open("rb") as handle:
        head = handle.read(8)
    if head.startswith(OLE_SIGNATURE):
        raise PackageError(
            f"{path.name} is encrypted or password protected.",
            "Ask the owner for the password and open it in the application, or "
            "ask for an unprotected copy. Nothing can be audited until then.",
            "owner")
    if not zipfile.is_zipfile(path):
        raise PackageError(
            f"{path.name} is not an Office Open XML package.",
            "Check the file is what its extension claims. An ODF file "
            "(.odt, .odp, .ods) is also a ZIP but uses a different XML layout.",
            "app")
    if suffix not in KIND_BY_SUFFIX:
        raise PackageError(
            f"{path.name} has an extension this script does not audit.",
            "Supported: .docx, .pptx, .xlsx and their macro and template variants.",
            "app")
    return KIND_BY_SUFFIX[suffix]


class OfficeAudit:
    def __init__(self, path: str):
        self.path = pathlib.Path(path)
        self.kind = identify(self.path)
        self.archive = zipfile.ZipFile(self.path)
        self.names = set(self.archive.namelist())
        self.findings: list[dict] = []
        self.outline: list[str] = []
        self.stats: dict = {"kind": self.kind, "parts": len(self.names)}
        self.container: dict = {}

    # ------------------------------------------------------------- plumbing

    def part(self, name: str) -> ET.Element | None:
        if name not in self.names:
            return None
        info = self.archive.getinfo(name)
        if info.file_size > MAX_PART_BYTES:
            self.note_problem(f"{name} is {info.file_size} bytes uncompressed and was "
                              "not parsed.")
            return None
        try:
            return ET.fromstring(self.archive.read(name))
        except ET.ParseError as error:
            self.note_problem(f"{name} is not well formed XML: {error}")
            return None

    def note_problem(self, message: str) -> None:
        problems = self.stats.setdefault("unreadable_parts", [])
        if message not in problems:      # a part may be read more than once
            problems.append(message)

    def matching(self, pattern: str) -> list[str]:
        return sorted(n for n in self.names if re.fullmatch(pattern, n))

    def add(self, sc, sc_title, level, severity, location, issue, impact, fix,
            verification, agent_fix, confidence="confirmed", evidence=None) -> None:
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
            "evidence": evidence,
            "fix": fix,
            "verification": verification,
            "source": "tool",
            "confidence": confidence,
            "agent_fix": agent_fix,
        })

    @staticmethod
    def sample(locations: list[str], limit: int = 5) -> str:
        shown = ", ".join(locations[:limit])
        if len(locations) > limit:
            shown += f", and {len(locations) - limit} more"
        return shown

    # ------------------------------------------------------- shared checks

    def read_container(self) -> None:
        """What the package holds that a rebuild would lose, or a tool would drop."""
        flags = {
            "macros": any(n.startswith(("word/vbaProject", "ppt/vbaProject",
                                        "xl/vbaProject")) for n in self.names),
            "digital_signature": any(n.startswith("_xmlsignatures/")
                                     for n in self.names),
            "comments": any(re.search(r"/comments\d*\.xml$", n) for n in self.names),
            "charts": len([n for n in self.names if "/charts/chart" in n]),
            "smartart": len([n for n in self.names if "/diagrams/" in n]),
            "embedded_objects": len([n for n in self.names if "/embeddings/" in n]),
            "images": len([n for n in self.names if "/media/" in n]),
            "custom_xml": any(n.startswith("customXml/") for n in self.names),
        }
        document = self.part("word/document.xml")
        if document is not None:
            flags["tracked_changes"] = any(
                local(e.tag) in ("ins", "del") for e in document.iter())
        self.container = flags

        lost = []
        if flags["macros"]:
            lost.append("macros")
        if flags["digital_signature"]:
            lost.append("a digital signature")
        if flags["smartart"]:
            lost.append(f"{flags['smartart']} SmartArt graphic(s)")
        if flags["embedded_objects"]:
            lost.append(f"{flags['embedded_objects']} embedded object(s)")
        if flags.get("tracked_changes"):
            lost.append("tracked changes")
        if flags["comments"]:
            lost.append("comments")
        self.container["at_risk_in_a_rebuild"] = lost

    def check_core_properties(self, fallback_title: str | None) -> None:
        core = self.part("docProps/core.xml")
        title = ""
        if core is not None:
            for element in core.iter():
                if local(element.tag) == "title" and element.text:
                    title = element.text.strip()
        self.stats["title"] = title
        if title:
            return
        if fallback_title:
            fix = (f"Set the document title in the file properties to the document's "
                   f"own heading, {fallback_title!r}, or to a title the author "
                   f"prefers. In the application: File, Info, Title.")
            agent_fix = "direct"
        else:
            fix = ("Set the document title in the file properties. The document "
                   "carries no heading or slide title to take it from, so ask the "
                   "author what it should be.")
            agent_fix = "owner"
        self.add("2.4.2", "Page Titled", "A", "medium",
                 f"{self.path.name} file properties",
                 "The document has no title in its properties.",
                 "The title is what a screen reader announces when the document "
                 "opens, what appears in a window list, and what carries into the "
                 "PDF title on export. Without it the reader hears a file name.",
                 fix,
                 "Reopen the file properties and confirm the title is set, then "
                 "export to PDF and confirm the PDF title matches.",
                 agent_fix)

    def check_alt_text(self, entries: list[tuple[str, str, str | None]]) -> None:
        """entries: (location, shape name, descr or None)."""
        missing = [(where, name) for where, name, descr in entries
                   if not (descr or "").strip()]
        useless = [(where, name) for where, name, descr in entries
                   if (descr or "").strip()
                   and (descr.strip().lower() in {"image", "picture", "graphic",
                                                  "chart", "photo", "logo", "figure"}
                        or re.fullmatch(r"[\w-]+\.(png|jpe?g|gif|bmp|svg|emf|wmf)",
                                        descr.strip(), re.I)
                        or descr.strip() == name)]
        self.stats["images_and_shapes"] = len(entries)
        self.stats["without_alt_text"] = len(missing)
        if missing:
            self.add("1.1.1", "Non-text Content", "A", "high",
                     self.sample([f"{w} ({n})" for w, n in missing]),
                     f"{len(missing)} image or shape has no alternative text."
                     if len(missing) == 1 else
                     f"{len(missing)} images or shapes have no alternative text.",
                     "A screen reader announces the object as a picture with no "
                     "description, or skips it. Anything the image was carrying is "
                     "lost, and a chart that holds the document's evidence is lost "
                     "completely.",
                     "Add alternative text that serves the same purpose as the "
                     "image, or mark the image decorative if it carries nothing. If "
                     "you can view the image, draft the text and have the author "
                     "confirm it, marking the finding needs-review rather than "
                     "closed. If you cannot view it, ask the author. Never write "
                     "alt text you cannot support: it looks fixed and tells the "
                     "reader nothing.",
                     "Reopen the alt text pane for each object and read what is "
                     "there against what the image shows.",
                     "owner")
        if useless:
            self.add("1.1.1", "Non-text Content", "A", "high",
                     self.sample([f"{w} ({n})" for w, n in useless]),
                     "Alternative text repeats the file name or a generic word "
                     "such as image or chart.",
                     "The checker sees an attribute and the reader gets nothing. "
                     "This is worse than an empty value, because every automated "
                     "check now reports the document as fixed.",
                     "Replace it with text that says what the image conveys in "
                     "this document, or mark the image decorative.",
                     "Read the alt text on its own and ask whether it could stand "
                     "in for the image.",
                     "owner")

    def check_links(self, entries: list[tuple[str, str]]) -> None:
        """entries: (location, visible text)."""
        generic, bare = [], []
        for where, text in entries:
            stripped = text.strip()
            if not stripped:
                continue
            if stripped.lower().strip(" .!:") in GENERIC_LINK_TEXT:
                generic.append((where, stripped))
            elif BARE_URL.match(stripped):
                bare.append((where, stripped))
        self.stats["links"] = len(entries)
        if generic:
            self.add("2.4.4", "Link Purpose (In Context)", "A", "medium",
                     self.sample([w for w, _ in generic]),
                     "Link text does not say where the link goes: "
                     + self.sample([repr(t) for _, t in generic]),
                     "Screen reader users list the links on a page to navigate. A "
                     "list of entries reading 'click here' identifies nothing, and "
                     "voice control users have no distinct name to speak.",
                     "Replace the text with the destination it describes. The right "
                     "wording depends on what is at the other end, so confirm it "
                     "with the author rather than guessing from the URL.",
                     "List the links and read them out of context. Each should "
                     "identify its destination.",
                     "owner")
        if bare:
            self.add("2.4.4", "Link Purpose (In Context)", "A", "advisory",
                     self.sample([w for w, _ in bare]),
                     "Link text is a bare URL: "
                     + self.sample([repr(t) for _, t in bare], 3),
                     "A screen reader reads the URL character group by character "
                     "group, which is slow and hard to follow. The link is usually "
                     "identifiable, so this is a usability problem rather than a "
                     "clear failure.",
                     "Replace the URL with a description of the destination, "
                     "keeping the URL in print-facing documents where the reader "
                     "may need to type it.",
                     "Read the link aloud and ask whether it identifies the "
                     "destination faster than the URL does.",
                     "owner", confidence="needs-review")

    # --------------------------------------------------------------- Word

    def heading_styles(self) -> dict[str, int]:
        styles = self.part("word/styles.xml")
        levels: dict[str, int] = {}
        if styles is None:
            return levels
        for style in styles.iter():
            if local(style.tag) != "style":
                continue
            style_id = attr(style, "styleId") or ""
            name = ""
            outline = None
            for child in style.iter():
                if local(child.tag) == "name":
                    name = (attr(child, "val") or "").strip().lower()
                elif local(child.tag) == "outlineLvl":
                    try:
                        outline = int(attr(child, "val") or "")
                    except ValueError:
                        outline = None
            match = re.fullmatch(r"heading\s*(\d)", name) or \
                re.fullmatch(r"Heading(\d)", style_id)
            if match:
                levels[style_id] = int(match.group(1))
            elif outline is not None and 0 <= outline <= 8:
                levels[style_id] = outline + 1
        return levels

    def default_font_size(self) -> int:
        styles = self.part("word/styles.xml")
        if styles is None:
            return 22
        for element in styles.iter():
            if local(element.tag) == "rPrDefault":
                for child in element.iter():
                    if local(child.tag) == "sz":
                        try:
                            return int(attr(child, "val") or 22)
                        except ValueError:
                            return 22
        return 22

    def document_language(self) -> str | None:
        styles = self.part("word/styles.xml")
        if styles is None:
            return None
        for element in styles.iter():
            if local(element.tag) == "rPrDefault":
                for child in element.iter():
                    if local(child.tag) == "lang":
                        return attr(child, "val")
        return None

    def audit_word(self) -> None:
        document = self.part("word/document.xml")
        if document is None:
            raise PackageError(
                "word/document.xml is missing or unreadable. "
                + "; ".join(self.stats.get("unreadable_parts", [])),
                "The package is damaged. Ask for another copy, or open and resave "
                "it in Word.", "recreate")

        levels = self.heading_styles()
        default_size = self.default_font_size()
        body = next((e for e in document.iter() if local(e.tag) == "body"), document)

        paragraphs, headings = [], []
        faux, manual_lists = [], []
        images, links = [], []
        anchored = 0
        index = 0

        for element in body.iter():
            name = local(element.tag)
            if name == "p":
                index += 1
                text = "".join(t.text or "" for t in element.iter()
                               if local(t.tag) == "t").strip()
                style, numbered, outline = None, False, None
                bold, sizes = [], []
                for child in element.iter():
                    child_name = local(child.tag)
                    if child_name == "pStyle":
                        style = attr(child, "val")
                    elif child_name == "numPr":
                        numbered = True
                    elif child_name == "outlineLvl":
                        try:
                            outline = int(attr(child, "val") or "")
                        except ValueError:
                            outline = None
                    elif child_name == "b":
                        bold.append(attr(child, "val") not in ("0", "false"))
                    elif child_name == "sz":
                        try:
                            sizes.append(int(attr(child, "val") or 0))
                        except ValueError:
                            pass
                level = levels.get(style or "")
                if level is None and outline is not None and 0 <= outline <= 8:
                    level = outline + 1
                paragraphs.append(text)
                where = f"word/document.xml paragraph {index}"
                if level is not None and text:
                    headings.append((level, text, where))
                elif text:
                    looks_like = (len(text) <= 120
                                  and (bold and all(bold)
                                       or (sizes and max(sizes) >= default_size + 4)))
                    if looks_like and not numbered:
                        faux.append((where, text))
                    if MANUAL_LIST_START.match(text) and not numbered:
                        manual_lists.append(where)
            elif name == "docPr":
                images.append((f"word/document.xml {attr(element, 'name') or 'object'}",
                               attr(element, "name") or "object",
                               attr(element, "descr")))
            elif name == "anchor":
                anchored += 1
            elif name == "hyperlink":
                text = "".join(t.text or "" for t in element.iter()
                               if local(t.tag) == "t").strip()
                links.append((f"word/document.xml hyperlink {len(links) + 1}", text))

        self.stats["paragraphs"] = len(paragraphs)
        self.stats["headings"] = len(headings)
        self.stats["floating_objects"] = anchored
        self.outline = [f"{'  ' * (level - 1)}H{level} {text}"
                        for level, text, _ in headings]

        body_paragraphs = [p for p in paragraphs if p]
        if not headings and len(body_paragraphs) >= 6:
            if faux:
                fix = ("Apply the built-in Heading styles to the paragraphs that are "
                       "acting as headings. Applying a style changes how they look, "
                       "so either match the style definition to the existing "
                       "formatting or agree the change with the owner first.")
                agent_fix = "direct"
            else:
                fix = ("The document has no headings and nothing that reads as one, "
                       "so its structure has to be established rather than "
                       "corrected. Rebuild it with real heading styles, keeping the "
                       "text as it is.")
                agent_fix = "recreate"
            self.add("1.3.1", "Info and Relationships", "A", "high",
                     f"{self.path.name}, {len(body_paragraphs)} paragraphs",
                     "The document uses no heading styles at all.",
                     "Screen reader users navigate a document by its headings. "
                     "Without them the only way through is to read every paragraph "
                     "in order, and the PDF export produces no tag structure and no "
                     "bookmarks.",
                     fix,
                     "Open the navigation pane and confirm the outline shows the "
                     "document's sections.",
                     agent_fix)
        elif faux:
            self.add("1.3.1", "Info and Relationships", "A", "high",
                     self.sample([w for w, _ in faux]),
                     f"{len(faux)} paragraph(s) are formatted to look like headings "
                     "with bold or a larger size, but carry no heading style: "
                     + self.sample([repr(t) for _, t in faux], 3),
                     "Formatting is invisible to assistive technology. These read as "
                     "ordinary paragraphs, so they do not appear in the navigation "
                     "pane, do not become headings in the PDF export, and do not "
                     "let a reader skip between sections.",
                     "Apply the matching built-in Heading style. Check each one "
                     "first: a bold line is not always a heading.",
                     "Open the navigation pane and confirm the outline matches the "
                     "document's sections.",
                     "direct", confidence="needs-review")

        skips = []
        previous = None
        for level, text, where in headings:
            if previous is not None and level > previous + 1:
                skips.append(f"{where} (H{previous} to H{level})")
            previous = level
        if skips:
            self.add("1.3.1", "Info and Relationships", "A", "medium",
                     self.sample(skips),
                     f"The heading outline skips a level {len(skips)} time(s).",
                     "A screen reader user navigating by level hears a gap and "
                     "cannot tell whether a section was missed.",
                     "Change the heading style so each level follows the one above "
                     "it. Where the level was chosen for its appearance, adjust the "
                     "style definition instead of the level.",
                     "Read the outline in the navigation pane from top to bottom.",
                     "direct")

        if manual_lists:
            self.add("1.3.1", "Info and Relationships", "A", "medium",
                     self.sample(manual_lists),
                     f"{len(manual_lists)} paragraph(s) start with a typed bullet or "
                     "number instead of using the list feature.",
                     "A screen reader announces a real list with its item count and "
                     "lets the user skip it. Typed hyphens are read as punctuation "
                     "in a run of separate paragraphs.",
                     "Rebuild them with the list feature so the structure is real.",
                     "Confirm the paragraphs carry list formatting, and that the "
                     "PDF export produces L and LI tags.",
                     "direct")

        tables = [e for e in body.iter() if local(e.tag) == "tbl"]
        self.stats["tables"] = len(tables)
        no_header, merged = [], []
        for number, table in enumerate(tables, start=1):
            rows = [e for e in table.iter() if local(e.tag) == "tr"]
            if not rows:
                continue
            repeats = any(local(e.tag) == "tblHeader" for e in rows[0].iter())
            look = next((e for e in table.iter() if local(e.tag) == "tblLook"), None)
            first_row = attr(look, "firstRow") in ("1", "true") if look is not None \
                else False
            if not repeats and not first_row:
                no_header.append(f"table {number}")
            if any(local(e.tag) in ("gridSpan", "vMerge") for e in table.iter()):
                merged.append(f"table {number}")
        if no_header:
            self.add("1.3.1", "Info and Relationships", "A", "high",
                     f"word/document.xml {self.sample(no_header)}",
                     f"{len(no_header)} table(s) declare no header row. Neither the "
                     "repeat header row setting nor the header row style option is "
                     "set on the first row.",
                     "A screen reader reads the cells without saying which column "
                     "they belong to, so a user hears '12' with no idea what it "
                     "counts. On export the table produces no TH cells.",
                     "Mark the first row as a header row in the table style "
                     "options, and turn on repeat header rows so the association "
                     "survives the PDF export. Check the first row really is the "
                     "header before setting it.",
                     "Export to PDF and confirm the header cells are tagged TH, or "
                     "read the table with a screen reader in table navigation mode.",
                     "direct")
        if merged:
            self.add("1.3.1", "Info and Relationships", "A", "medium",
                     f"word/document.xml {self.sample(merged)}",
                     f"{len(merged)} table(s) contain merged cells.",
                     "Merged cells break screen reader table navigation and are the "
                     "part of a table that survives a PDF export worst. A dropped "
                     "merge shifts every later cell into the wrong column, so the "
                     "reader is told a value belongs somewhere it does not.",
                     "Restructure the table so each cell sits in one row and one "
                     "column, splitting it into separate tables if the merges carry "
                     "grouping. This changes how the data is presented, so agree it "
                     "with the owner.",
                     "Read the table cell by cell with a screen reader and confirm "
                     "each value is announced with the right headers.",
                     "owner")

        if anchored:
            self.add("1.3.2", "Meaningful Sequence", "A", "medium",
                     f"word/document.xml, {anchored} floating object(s)",
                     f"{anchored} object(s) float rather than sitting in line with "
                     "the text.",
                     "A floating object has no fixed place in the reading order, so "
                     "a screen reader may announce it far from the text it belongs "
                     "to, or not at all.",
                     "Set the object to be in line with text. That changes the page "
                     "layout, so confirm the result with whoever owns the design.",
                     "Read the document in order with a screen reader and confirm "
                     "each object arrives where it belongs.",
                     "design")

        language = self.document_language()
        self.stats["language"] = language
        if not language:
            self.add("3.1.1", "Language of Page", "A", "high",
                     f"{self.path.name} default style",
                     "The document sets no default language.",
                     "A screen reader reads the text with whatever voice and "
                     "pronunciation rules it defaults to, which makes a document in "
                     "one language read as gibberish in another.",
                     "Set the document language on the default style, and mark any "
                     "passage in another language with its own language.",
                     "Confirm the language shows in the status bar, and that the "
                     "exported PDF carries a /Lang value.",
                     "direct")

        self.check_alt_text(images)
        self.check_links(links)
        # The title falls back to whichever heading comes first in the document,
        # real or formatted to look like one, because that is what the author
        # already wrote at the top of the page.
        candidates = [(int(where.rsplit(" ", 1)[1]), text)
                      for _level, text, where in headings]
        candidates += [(int(where.rsplit(" ", 1)[1]), text) for where, text in faux]
        candidates.sort()
        self.stats["title_candidate"] = candidates[0][1] if candidates else None
        self.check_core_properties(self.stats["title_candidate"])

    # --------------------------------------------------------- PowerPoint

    def audit_powerpoint(self) -> None:
        slides = sorted(self.matching(r"ppt/slides/slide\d+\.xml"),
                        key=lambda n: int(re.search(r"(\d+)", n).group(1)))
        if not slides:
            raise PackageError(
                "The package holds no slides.",
                "Check the file is a presentation and not a template with its "
                "slides stripped.", "app")
        self.stats["slides"] = len(slides)

        titles, untitled, images, links = [], [], [], []
        loose_text = []
        for number, name in enumerate(slides, start=1):
            slide = self.part(name)
            if slide is None:
                continue
            title = None
            free_shapes = 0
            tree = next((e for e in slide.iter() if local(e.tag) == "spTree"), slide)
            for shape in tree.iter():
                shape_name = local(shape.tag)
                if shape_name == "sp":
                    placeholder = next((e for e in shape.iter()
                                        if local(e.tag) == "ph"), None)
                    text = "".join(t.text or "" for t in shape.iter()
                                   if local(t.tag) == "t").strip()
                    if placeholder is not None and \
                            (attr(placeholder, "type") or "body") in ("title",
                                                                     "ctrTitle"):
                        title = text
                    elif placeholder is None and text:
                        free_shapes += 1
                elif shape_name == "r":
                    # A hyperlink in DrawingML hangs off the run's properties,
                    # so the visible text is the run's own a:t.
                    if any(local(e.tag) == "hlinkClick" for e in shape.iter()):
                        text = "".join(e.text or "" for e in shape.iter()
                                       if local(e.tag) == "t").strip()
                        links.append((f"slide {number} link {len(links) + 1}", text))
            images.extend(alt_candidates(tree, f"slide {number}"))
            if title:
                titles.append((number, title))
            else:
                untitled.append(f"slide {number}")
            if free_shapes >= 2:
                loose_text.append(f"slide {number} ({free_shapes} loose text boxes)")
            self.outline.append(f"slide {number}: {title or '(no title)'}")

        if untitled:
            self.add("2.4.2", "Page Titled", "A", "high",
                     self.sample(untitled),
                     f"{len(untitled)} slide(s) have no title.",
                     "Slide titles are how screen reader users move through a deck "
                     "and how they know where they are. A slide with no title is "
                     "announced by its number alone.",
                     "Add a title placeholder from the slide layout and put the "
                     "slide's own heading text in it. Where a slide is deliberately "
                     "untitled, a title placeholder moved off the visible area still "
                     "gives the reader the name. This needs the layout, so do it in "
                     "PowerPoint or with a library that can reach the layout's "
                     "placeholders.",
                     "Open the outline view and confirm every slide shows a title.",
                     "app")
        duplicates = {}
        for number, title in titles:
            duplicates.setdefault(title.lower(), []).append(number)
        repeated = {t: n for t, n in duplicates.items() if len(n) > 1}
        if repeated:
            self.add("2.4.2", "Page Titled", "A", "advisory",
                     self.sample([f"slides {', '.join(str(x) for x in n)}"
                                  for n in repeated.values()]),
                     f"{len(repeated)} slide title(s) are repeated across slides.",
                     "A reader moving by title cannot tell repeated slides apart, "
                     "so a deck with four slides called 'Programme update' gives "
                     "them no way to return to the one they wanted.",
                     "Make each title distinct, for example by numbering the "
                     "continuations.",
                     "Read the outline view and confirm every title is unique.",
                     "owner")
        if loose_text:
            self.add("1.3.2", "Meaningful Sequence", "A", "medium",
                     self.sample(loose_text),
                     "Slides carry text in free-floating boxes rather than layout "
                     "placeholders.",
                     "Content outside a placeholder is read in the order the shapes "
                     "were added, which is not the order they appear on screen. A "
                     "slide that looks correct can read its footnote before its "
                     "heading.",
                     "Rebuild the slide on a layout so the placeholders carry the "
                     "order, or set the order explicitly in the reading order pane "
                     "and check it against the visual layout.",
                     "Open the reading order pane and read the slide top to bottom "
                     "in the order it lists.",
                     "app")

        self.check_alt_text(images)
        self.check_links(links)
        self.stats["title_candidate"] = titles[0][1] if titles else None
        self.check_core_properties(self.stats["title_candidate"])

    # -------------------------------------------------------------- Excel

    def audit_excel(self) -> None:
        workbook = self.part("xl/workbook.xml")
        if workbook is None:
            raise PackageError(
                "xl/workbook.xml is missing or unreadable. "
                + "; ".join(self.stats.get("unreadable_parts", [])),
                "The package is damaged. Ask for another copy, or open and resave "
                "it in Excel.", "recreate")
        sheets = [attr(e, "name") or "" for e in workbook.iter()
                  if local(e.tag) == "sheet"]
        self.stats["sheets"] = len(sheets)
        self.outline = [f"sheet: {name}" for name in sheets]

        default_named = [name for name in sheets if DEFAULT_SHEET_NAME.match(name)]
        if default_named:
            self.add("2.4.6", "Headings and Labels", "AA", "low",
                     self.sample(default_named),
                     f"{len(default_named)} sheet(s) keep a default name.",
                     "Sheet names are how a screen reader user identifies where "
                     "they are in a workbook. Sheet1 tells them nothing.",
                     "Rename each sheet after what it holds. Update any formula, "
                     "chart reference, or defined name that refers to the old name "
                     "in the same pass, because a rename breaks them silently.",
                     "Move between sheets with a screen reader and confirm each is "
                     "announced by a name that says what it holds.",
                     "direct", confidence="needs-review")

        merged_sheets, blank_rows = [], []
        for name in self.matching(r"xl/worksheets/sheet\d+\.xml"):
            sheet = self.part(name)
            if sheet is None:
                continue
            merges = [attr(e, "ref") for e in sheet.iter()
                      if local(e.tag) == "mergeCell"]
            if merges:
                merged_sheets.append(f"{name} ({len(merges)} merged range(s))")
            rows = [e for e in sheet.iter() if local(e.tag) == "row"]
            numbers = []
            for row in rows:
                text = "".join(t.text or "" for t in row.iter()
                               if local(t.tag) == "t").strip()
                try:
                    numbers.append((int(attr(row, "r") or 0), bool(text)))
                except ValueError:
                    continue
            filled = [n for n, has_text in numbers if has_text]
            empty_inside = [n for n, has_text in numbers
                            if not has_text and filled and min(filled) < n < max(filled)]
            if empty_inside:
                blank_rows.append(f"{name} row(s) "
                                  f"{', '.join(str(n) for n in empty_inside[:5])}")

        if merged_sheets:
            self.add("1.3.1", "Info and Relationships", "A", "medium",
                     self.sample(merged_sheets),
                     "Merged cells sit inside the data.",
                     "Merged cells break the row and column navigation a screen "
                     "reader user relies on to move through a table, and they stop "
                     "the header association working.",
                     "Unmerge them and repeat the value, or move the merged title "
                     "outside the data range. This changes the layout, so agree it "
                     "with the owner.",
                     "Navigate the range cell by cell with a screen reader and "
                     "confirm each value is announced with its row and column "
                     "headers.",
                     "owner")
        if blank_rows:
            self.add("1.3.1", "Info and Relationships", "A", "low",
                     self.sample(blank_rows),
                     "Blank rows sit inside the data range.",
                     "A blank row reads as the end of the table, so a screen reader "
                     "user stops there and never reaches the rest of the data.",
                     "Remove the blank rows and use cell formatting for the spacing "
                     "they were providing.",
                     "Select the range and confirm it reads as one continuous "
                     "table.",
                     "owner")

        tables = self.matching(r"xl/tables/table\d+\.xml")
        self.stats["defined_tables"] = len(tables)
        if not tables and self.stats["sheets"]:
            self.add("1.3.1", "Info and Relationships", "A", "medium",
                     f"{self.path.name}, {len(sheets)} sheet(s)",
                     "No range in the workbook is defined as a table, so no header "
                     "row is associated with its data.",
                     "Without a defined table the header row is only text in the "
                     "first row. A screen reader has nothing to announce with each "
                     "cell, so the user hears values with no idea what they "
                     "measure.",
                     "Select each data range and format it as a table with the "
                     "header row option, or set a defined name for the header row. "
                     "Check which row really is the header first.",
                     "Move through the data with a screen reader and confirm each "
                     "cell is announced with its column header.",
                     "direct", confidence="needs-review")

        images = []
        for name in self.matching(r"xl/drawings/drawing\d+\.xml"):
            drawing = self.part(name)
            if drawing is None:
                continue
            for anchor in drawing:
                images.extend(alt_candidates(anchor, name))
        self.check_alt_text(images)
        named = [s for s in sheets if s and not DEFAULT_SHEET_NAME.match(s)]
        self.stats["title_candidate"] = named[0] if named else None
        self.check_core_properties(self.stats["title_candidate"])

        if self.container.get("charts"):
            self.stats["round_trip_warning"] = (
                f"The workbook holds {self.container['charts']} chart(s). openpyxl "
                "drops charts and images when it saves, so edit this file through "
                "its XML parts or in Excel, not by loading and saving it with "
                "openpyxl.")

    # ----------------------------------------------------------------- run

    def run(self) -> list[dict]:
        self.read_container()
        if self.kind == "docx":
            self.audit_word()
        elif self.kind == "pptx":
            self.audit_powerpoint()
        else:
            self.audit_excel()
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "advisory": 4}
        self.findings.sort(key=lambda f: order.get(f["severity"], 5))
        for position, finding in enumerate(self.findings, start=1):
            finding["id"] = f"F-{position:03d}"
        return self.findings


def blocked_finding(error: PackageError, path: str) -> dict:
    return {
        "id": "F-001", "sc": "n/a", "sc_title": "Not assessed", "level": "n/a",
        "severity": "critical", "location": path, "selector": None,
        "issue": error.reason,
        "impact": "Nothing in the document could be assessed, so no criterion has "
                  "a result and the audit cannot say whether it is accessible.",
        "evidence": None, "fix": error.remedy,
        "verification": "Reopen the file once the blocker is cleared and run the "
                        "audit again.",
        "source": "tool", "confidence": "confirmed", "agent_fix": error.agent_fix,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Structural accessibility checks on a Word, PowerPoint, or "
                    "Excel file (WCAG 2.2 through WCAG2ICT).")
    parser.add_argument("path", help="a .docx, .pptx, or .xlsx file")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--dump-outline", action="store_true",
                        help="print the heading outline, slide titles, or sheet "
                             "names instead of findings")
    args = parser.parse_args(argv)

    try:
        audit = OfficeAudit(args.path)
        findings = audit.run()
    except PackageError as error:
        if args.as_json:
            print(json.dumps({
                "tool": "office_audit.py", "standard": "WCAG 2.2 through WCAG2ICT",
                "file": args.path, "stats": {"assessed": False},
                "findings": [blocked_finding(error, args.path)],
                "manual_checks_required": MANUAL_CHECKS,
            }, indent=2))
            return 2
        print(f"{args.path}\n  cannot audit: {error.reason}\n  {error.remedy}",
              file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"{args.path}: no such file", file=sys.stderr)
        return 2

    if args.dump_outline:
        if not audit.outline:
            print("No headings, slide titles, or sheet names to show.")
            return 0
        for line in audit.outline:
            print(line)
        return 0

    if args.as_json:
        print(json.dumps({
            "tool": "office_audit.py",
            "standard": "WCAG 2.2 through WCAG2ICT",
            "file": args.path,
            "stats": audit.stats,
            "container": audit.container,
            "findings": findings,
            "manual_checks_required": MANUAL_CHECKS,
        }, indent=2))
        return 0

    print(args.path)
    for key, value in audit.stats.items():
        if isinstance(value, list):
            value = f"{len(value)} item(s)"
        print(f"  {key:22} {value}")
    lost = audit.container.get("at_risk_in_a_rebuild") or []
    if lost:
        print(f"  {'at risk in a rebuild':22} {', '.join(lost)}")
    print()

    if not findings:
        print("No structural findings.")
    for finding in findings:
        print(f"[{finding['severity'].upper():8}] {finding['sc']} "
              f"{finding['sc_title']} ({finding['level']})  "
              f"fix: {finding['agent_fix']}")
        print(f"           {finding['location']}")
        print(f"           {finding['issue']}")
        print(f"           Fix: {finding['fix']}\n")

    not_direct = [f for f in findings if f["agent_fix"] != "direct"]
    if not_direct:
        print(f"{len(not_direct)} finding(s) an agent cannot close on its own:")
        for finding in not_direct:
            print(f"  - {finding['id']} {finding['sc']} needs {finding['agent_fix']}")
        print()

    print("Still to check by hand, because no tool can judge these:")
    for check in MANUAL_CHECKS:
        print(f"  - {check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
