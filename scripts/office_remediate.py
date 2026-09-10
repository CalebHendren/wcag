#!/usr/bin/env python3
"""Apply the derivable accessibility fixes to a Word, PowerPoint, or Excel file.

This is the direct remediation path for an agent working on documents rather
than on source code. It edits the XML parts inside the Office package and copies
every other part across byte for byte, so nothing the script does not understand
can be lost. That is the reason it does string surgery on the XML rather than
reparsing and rewriting it: a round trip through a serializer renames namespace
prefixes and reorders attributes across the whole file, and a diff that touches
everything cannot be reviewed.

It applies only fixes whose correct value is derivable, which is the same line
`skills/wcag-remediate/SKILL.md` draws. It will not write alternative text it was
not given, will not restructure a table, and will not decide a heading level.

The original is never modified. Output goes to a new file beside it.

Exit codes matter, because they drive what the agent does next:
  0  every requested fix was applied, or was already satisfied
  1  at least one requested fix failed, which is the signal to stop and
     consider recreating the document instead of patching it further
  2  the file could not be opened at all

Standard library only.

Usage:
  office_remediate.py report.docx --title auto --language en-GB --table-headers
  office_remediate.py deck.pptx --alt-text alt.json --dry-run
  office_remediate.py report.docx --title "Annual report" -o fixed.docx --json

The alt text map is {"shape name": "the alternative text"}, keyed by the name
office_audit.py reports for each object.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from office_audit import (  # noqa: E402
    OfficeAudit, PackageError, attr, local,
)

CORE_PART = "docProps/core.xml"

CORE_TEMPLATE = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                 '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/'
                 'package/2006/metadata/core-properties" xmlns:dc="http://purl.org/'
                 'dc/elements/1.1/"><dc:title>{title}</dc:title></cp:coreProperties>')

# The order CT_TrPr allows. tblHeader has to go before any of these.
TRPR_AFTER = ("tblCellSpacing", "jc", "hidden", "ins", "del", "trPrChange")


def escape(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def prefix_for(xml: str, namespace: str, fallback: str) -> str:
    """The prefix bound to a namespace in this document, or the usual one.

    Office writes w:, p: and xdr: in practice, but a file produced by another
    tool may bind them differently, and rewriting with the wrong prefix
    produces a document the application refuses to open.
    """
    match = re.search(r'xmlns:([A-Za-z0-9_.-]+)="' + re.escape(namespace) + '"', xml)
    return match.group(1) if match else fallback


class Result:
    def __init__(self):
        self.applied: list[str] = []
        self.already: list[str] = []
        self.failed: list[dict] = []
        self.parts: dict[str, str] = {}

    def apply(self, name: str, message: str) -> None:
        self.applied.append(f"{name}: {message}")

    def satisfied(self, name: str, message: str) -> None:
        self.already.append(f"{name}: {message}")

    def fail(self, name: str, reason: str, instead: str) -> None:
        self.failed.append({"fix": name, "reason": reason, "instead": instead})


class Remediator:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.audit = OfficeAudit(str(path))
        self.kind = self.audit.kind
        self.archive = self.audit.archive
        self.names = self.audit.archive.namelist()
        self.result = Result()

    # ------------------------------------------------------------- plumbing

    def read(self, part: str) -> str | None:
        if part in self.result.parts:
            return self.result.parts[part]
        if part not in self.names:
            return None
        return self.archive.read(part).decode("utf-8", errors="replace")

    def stage(self, part: str, xml: str, fix: str) -> bool:
        """Hold a rewritten part, refusing it if it stopped being well formed."""
        try:
            ET.fromstring(xml)
        except ET.ParseError as error:
            self.result.fail(fix, f"the edit left {part} malformed: {error}",
                             "Nothing was written. Make this change in the "
                             "application instead, or recreate the document.")
            return False
        self.result.parts[part] = xml
        return True

    # ---------------------------------------------------------------- fixes

    def set_title(self, title: str) -> None:
        fix = "document title"
        if title == "auto":
            derived = self.derive_title()
            if not derived:
                self.result.fail(
                    fix, "the document carries no heading, slide title, or named "
                         "sheet to take a title from.",
                    "Ask the author what the document should be called, then pass "
                    "it with --title.")
                return
            title = derived
        current = (self.audit.stats.get("title") or "").strip()
        if current == title:
            self.result.satisfied(fix, f"already {title!r}")
            return
        core = self.read(CORE_PART)
        if core is None:
            self.result.parts[CORE_PART] = CORE_TEMPLATE.format(title=escape(title))
            self.result.apply(fix, f"set to {title!r} in a new core properties part")
            return
        if re.search(r"<([A-Za-z0-9_.-]+:)?title\s*/>", core):
            updated = re.sub(r"<([A-Za-z0-9_.-]+:)?title\s*/>",
                             lambda m: f"<{m.group(1) or ''}title>{escape(title)}"
                                       f"</{m.group(1) or ''}title>", core, count=1)
        elif re.search(r"<([A-Za-z0-9_.-]+:)?title>.*?</([A-Za-z0-9_.-]+:)?title>",
                       core, re.S):
            updated = re.sub(
                r"<([A-Za-z0-9_.-]+:)?title>.*?</([A-Za-z0-9_.-]+:)?title>",
                lambda m: f"<{m.group(1) or ''}title>{escape(title)}"
                          f"</{m.group(2) or ''}title>", core, count=1, flags=re.S)
        else:
            updated = re.sub(r"(<([A-Za-z0-9_.-]+:)?coreProperties[^>]*>)",
                             lambda m: f"{m.group(1)}<dc:title>{escape(title)}"
                                       f"</dc:title>", core, count=1)
            if updated == core:
                self.result.fail(fix, "docProps/core.xml has no coreProperties "
                                      "element to write into.",
                                 "Set the title in the application under File, "
                                 "Info, Title.")
                return
        if self.stage(CORE_PART, updated, fix):
            self.result.apply(fix, f"set to {title!r}")

    def derive_title(self) -> str | None:
        """The heading, slide title, or sheet name the audit picked as a title.

        Both scripts use the same candidate, so what the audit proposed in its
        finding is what the fix writes.
        """
        return self.audit.stats.get("title_candidate")

    def set_language(self, tag: str) -> None:
        fix = "document language"
        if self.kind == "xlsx":
            self.result.fail(
                fix, "a workbook carries no document language setting.",
                "Set the language on the text where it matters, or state in the "
                "report that the format has nowhere to record it.")
            return
        if self.kind == "docx":
            styles = self.read("word/styles.xml")
            if styles is None:
                self.result.fail(fix, "word/styles.xml is missing.",
                                 "Set the language in Word under Review, Language, "
                                 "Set Proofing Language, and apply it to the "
                                 "default style.")
                return
            w = prefix_for(styles, "http://schemas.openxmlformats.org/"
                                   "wordprocessingml/2006/main", "w")
            if self.audit.stats.get("language") == tag:
                self.result.satisfied(fix, f"already {tag}")
                return
            element = f'<{w}:lang {w}:val="{escape(tag)}"/>'
            if re.search(rf"<{w}:lang\b[^>]*/>", styles):
                updated = re.sub(rf"<{w}:lang\b[^>]*/>", element, styles, count=1)
            elif re.search(rf"<{w}:rPrDefault>\s*<{w}:rPr>", styles):
                updated = re.sub(rf"(<{w}:rPrDefault>\s*<{w}:rPr>)",
                                 lambda m: m.group(1) + element, styles, count=1)
            elif f"<{w}:rPrDefault/>" in styles:
                updated = styles.replace(
                    f"<{w}:rPrDefault/>",
                    f"<{w}:rPrDefault><{w}:rPr>{element}</{w}:rPr></{w}:rPrDefault>", 1)
            elif re.search(rf"<{w}:docDefaults>", styles):
                updated = re.sub(
                    rf"(<{w}:docDefaults>)",
                    lambda m: m.group(1) + f"<{w}:rPrDefault><{w}:rPr>{element}"
                                           f"</{w}:rPr></{w}:rPrDefault>",
                    styles, count=1)
            else:
                self.result.fail(fix, "word/styles.xml has no docDefaults to write "
                                      "the language into.",
                                 "Set the language in Word and resave, or recreate "
                                 "the document.")
                return
            if self.stage("word/styles.xml", updated, fix):
                self.result.apply(fix, f"default style set to {tag}")
            return

        # PowerPoint keeps the language on each run rather than on the document.
        changed = 0
        for part in sorted(n for n in self.names
                           if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)):
            xml = self.read(part)
            if xml is None:
                continue
            updated, count = re.subn(r'(<a:(?:rPr|endParaRPr|defRPr)\b[^>]*?)\blang="'
                                     r'[^"]*"', rf'\1lang="{escape(tag)}"', xml)
            if count and self.stage(part, updated, fix):
                changed += count
        if changed:
            self.result.apply(fix, f"{changed} text run(s) set to {tag}")
        else:
            self.result.fail(
                fix, "no text runs declare a language attribute to update.",
                "Set the language in PowerPoint under Review, Language, and check "
                "it applied to every text box.")

    def set_table_headers(self) -> None:
        fix = "table header rows"
        if self.kind != "docx":
            self.result.fail(
                fix, f"this fix is implemented for Word only, not {self.kind}.",
                "In PowerPoint use the header row option in table design. In Excel "
                "format the range as a table with a header row.")
            return
        part = "word/document.xml"
        xml = self.read(part)
        if xml is None:
            self.result.fail(fix, "word/document.xml is missing.",
                             "The package is damaged. Recreate the document.")
            return
        w = prefix_for(xml, "http://schemas.openxmlformats.org/"
                            "wordprocessingml/2006/main", "w")
        tables = list(re.finditer(rf"<{w}:tbl>", xml))
        if not tables:
            self.result.satisfied(fix, "the document has no tables")
            return
        pieces, cursor, changed = [], 0, 0
        for match in tables:
            end = xml.find(f"</{w}:tbl>", match.end())
            if end == -1:
                continue
            body = xml[match.start():end]
            new_body, done = self.mark_first_row(body, w)
            if done:
                changed += 1
                pieces.append(xml[cursor:match.start()])
                pieces.append(new_body)
                cursor = end
        if not changed:
            self.result.satisfied(fix, f"all {len(tables)} table(s) already declare "
                                       "a header row")
            return
        pieces.append(xml[cursor:])
        if self.stage(part, "".join(pieces), fix):
            self.result.apply(fix, f"{changed} table(s) now repeat their first row "
                                   "as a header")

    @staticmethod
    def mark_first_row(table: str, w: str) -> tuple[str, bool]:
        row = re.search(rf"<{w}:tr\b[^>]*>", table)
        if not row:
            return table, False
        row_end = table.find(f"</{w}:tr>", row.end())
        if row_end == -1:
            return table, False
        first_row = table[row.start():row_end]
        changed = False
        if f"<{w}:tblHeader" not in first_row:
            header = f"<{w}:tblHeader/>"
            trpr = re.search(rf"<{w}:trPr>", first_row)
            if trpr:
                closing = first_row.find(f"</{w}:trPr>", trpr.end())
                inner = first_row[trpr.end():closing]
                position = len(inner)
                for name in TRPR_AFTER:
                    found = inner.find(f"<{w}:{name}")
                    if found != -1:
                        position = min(position, found)
                inner = inner[:position] + header + inner[position:]
                first_row = (first_row[:trpr.end()] + inner + first_row[closing:])
            elif f"<{w}:trPr/>" in first_row:
                first_row = first_row.replace(
                    f"<{w}:trPr/>", f"<{w}:trPr>{header}</{w}:trPr>", 1)
            else:
                first_row = (first_row[:row.end() - row.start()]
                             + f"<{w}:trPr>{header}</{w}:trPr>"
                             + first_row[row.end() - row.start():])
            changed = True
        table = table[:row.start()] + first_row + table[row_end:]

        look = re.search(rf"<{w}:tblLook\b[^>]*/>", table)
        if look:
            if not re.search(rf'{w}:firstRow="(1|true)"', look.group(0)):
                replacement = re.sub(rf'\s*{w}:firstRow="[^"]*"', "", look.group(0))
                replacement = replacement.replace(
                    "/>", f' {w}:firstRow="1"/>')
                table = table[:look.start()] + replacement + table[look.end():]
                changed = True
        else:
            tblpr = re.search(rf"</{w}:tblPr>", table)
            entry = (f'<{w}:tblLook {w}:firstRow="1" {w}:lastRow="0" '
                     f'{w}:firstColumn="0" {w}:lastColumn="0" {w}:noHBand="0" '
                     f'{w}:noVBand="1"/>')
            if tblpr:
                table = table[:tblpr.start()] + entry + table[tblpr.start():]
                changed = True
        return table, changed

    def set_alt_text(self, mapping: dict[str, str]) -> None:
        fix = "alternative text"
        if not mapping:
            self.result.fail(fix, "the alt text map is empty.",
                             "Supply {\"shape name\": \"text\"} for each object, or "
                             "ask the author for the descriptions.")
            return
        targets = {"docx": ["word/document.xml"],
                   "pptx": sorted(n for n in self.names
                                  if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                   "xlsx": sorted(n for n in self.names
                                  if re.fullmatch(r"xl/drawings/drawing\d+\.xml", n)),
                   }[self.kind]
        done: set[str] = set()
        for part in targets:
            xml = self.read(part)
            if xml is None:
                continue
            updated = xml
            for name, text in mapping.items():
                pattern = re.compile(
                    r'<((?:[A-Za-z0-9_.-]+:)?(?:docPr|cNvPr))\b([^>]*?)\bname="'
                    + re.escape(name) + r'"([^>]*?)(/?)>')

                def rewrite(match: re.Match) -> str:
                    head = f'<{match.group(1)}{match.group(2)}name="{escape(name)}"'
                    tail = re.sub(r'\s*descr="[^"]*"', "", match.group(3))
                    done.add(name)
                    return f'{head}{tail} descr="{escape(text)}"{match.group(4)}>'

                updated = pattern.sub(rewrite, updated)
            if updated != xml and self.stage(part, updated, fix):
                pass
        missing = sorted(set(mapping) - done)
        if done:
            self.result.apply(fix, f"set on {len(done)} object(s): "
                                   f"{', '.join(sorted(done))}")
        if missing:
            self.result.fail(
                fix, f"no object named {', '.join(missing)} was found in the file.",
                "Run office_audit.py --json and use the shape names it reports as "
                "the keys.")

    # ----------------------------------------------------------------- save

    def write(self, output: pathlib.Path) -> None:
        with zipfile.ZipFile(output, "w") as out:
            for info in self.archive.infolist():
                if info.filename in self.result.parts:
                    data = self.result.parts[info.filename].encode("utf-8")
                else:
                    data = self.archive.read(info.filename)
                new_info = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                new_info.compress_type = info.compress_type
                new_info.external_attr = info.external_attr
                out.writestr(new_info, data)
            for name, xml in self.result.parts.items():
                if name not in self.archive.namelist():
                    out.writestr(name, xml.encode("utf-8"))


def default_output(path: pathlib.Path) -> pathlib.Path:
    return path.with_name(f"{path.stem}-remediated{path.suffix}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply the derivable accessibility fixes to a Word, "
                    "PowerPoint, or Excel file. Writes a new file and never "
                    "modifies the original.")
    parser.add_argument("path", help="a .docx, .pptx, or .xlsx file")
    parser.add_argument("-o", "--output", help="where to write the fixed copy")
    parser.add_argument("--title", help="document title, or 'auto' to take it from "
                                        "the first heading, slide title, or sheet "
                                        "name")
    parser.add_argument("--language", help="language tag for the document, "
                                           "for example en-GB")
    parser.add_argument("--table-headers", action="store_true",
                        help="mark the first row of every Word table as a repeating "
                             "header row")
    parser.add_argument("--alt-text", help="JSON file mapping shape name to "
                                           "alternative text")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change and write nothing")
    parser.add_argument("--force", action="store_true",
                        help="overwrite the output file if it exists")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    requested = [args.title, args.language, args.table_headers, args.alt_text]
    if not any(requested):
        parser.error("no fix requested. Choose from --title, --language, "
                     "--table-headers, --alt-text.")

    path = pathlib.Path(args.path)
    try:
        remediator = Remediator(path)
        remediator.audit.run()
    except PackageError as error:
        print(f"{path}: cannot remediate: {error.reason}\n  {error.remedy}",
              file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"{path}: no such file", file=sys.stderr)
        return 2

    if args.title:
        remediator.set_title(args.title)
    if args.language:
        remediator.set_language(args.language)
    if args.table_headers:
        remediator.set_table_headers()
    if args.alt_text:
        try:
            mapping = json.loads(pathlib.Path(args.alt_text).read_text("utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"{args.alt_text}: {error}", file=sys.stderr)
            return 2
        remediator.set_alt_text(mapping)

    result = remediator.result
    output = pathlib.Path(args.output) if args.output else default_output(path)
    wrote = None
    if not args.dry_run and result.parts:
        if output.exists() and not args.force:
            print(f"{output} exists. Pass --force to overwrite, or choose another "
                  "path with -o.", file=sys.stderr)
            return 2
        temporary = output.with_suffix(output.suffix + ".partial")
        remediator.write(temporary)
        shutil.move(str(temporary), str(output))
        wrote = str(output)

    payload = {
        "tool": "office_remediate.py",
        "file": str(path),
        "output": wrote,
        "dry_run": args.dry_run,
        "applied": result.applied,
        "already_satisfied": result.already,
        "failed": result.failed,
        "parts_rewritten": sorted(result.parts),
    }
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(path)
        for line in result.applied:
            print(f"  applied   {line}")
        for line in result.already:
            print(f"  already   {line}")
        for entry in result.failed:
            print(f"  FAILED    {entry['fix']}: {entry['reason']}")
            print(f"            Instead: {entry['instead']}")
        if wrote:
            print(f"\nWrote {wrote}. The original is unchanged.")
            print("Re-run office_audit.py on the new file, and open it in the "
                  "application to confirm it still looks right.")
        elif args.dry_run:
            print("\nDry run. Nothing was written.")
        elif not result.parts:
            print("\nNothing to change.")
    if result.failed:
        if not args.as_json:
            print(f"\n{len(result.failed)} fix(es) failed. Stop here rather than "
                  "patching further: report what could not be applied, and offer "
                  "to recreate the document instead.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
