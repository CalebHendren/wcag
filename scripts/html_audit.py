#!/usr/bin/env python3
"""Static WCAG checks on HTML source. No browser, no network, no dependencies.

This covers the structural failures that are visible in markup alone: missing
names, unlabelled inputs, broken ARIA references, heading structure, table
headers, iframe titles, viewport zoom locks, autoplay, and generic link text.

It deliberately does NOT try to be axe-core. Anything that needs computed style,
layout, or a rendered accessibility tree (contrast, reflow, target size, focus
visibility, focus order) is out of reach here. Use scripts/axe_scan.py against a
live page for those, and your own inspection for the criteria no tool can judge.

Usage:
  html_audit.py page.html
  html_audit.py src/**/*.html --json > findings.json
  html_audit.py page.html --min-severity high

Exit status is 1 when any finding at or above --fail-on severity is reported.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from html.parser import HTMLParser

SEVERITY_ORDER = ["advisory", "low", "medium", "high", "critical"]

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}

INTERACTIVE = {"a", "button", "input", "select", "textarea", "summary", "details"}

GENERIC_LINK_TEXT = {
    "click here", "here", "read more", "more", "learn more", "link",
    "this link", "click", "details", "continue", "go", "download",
    "read this", "see more", "view", "more info", "more information",
}

BAD_ALT = {
    "image", "img", "photo", "picture", "graphic", "icon", "logo", "spacer",
    "photo of", "image of", "picture of", "graphic of",
}

# Inputs that take no visible label because they carry their own or need none.
UNLABELLED_OK_TYPES = {"hidden", "submit", "reset", "button", "image"}


class Element:
    __slots__ = ("tag", "attrs", "line", "col", "text", "children", "parent", "index")

    def __init__(self, tag, attrs, line, col, parent=None, index=0):
        self.tag = tag
        self.attrs = attrs
        self.line = line
        self.col = col
        self.text = ""
        self.children = []
        self.parent = parent
        self.index = index

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def has(self, name):
        return name in self.attrs

    def inner_text(self):
        parts = [self.text]
        for child in self.children:
            if child.tag not in ("script", "style"):
                parts.append(child.inner_text())
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def snippet(self):
        rendered = " ".join(
            f'{k}="{v}"' if v is not None else k for k, v in self.attrs.items())
        opening = f"<{self.tag}{' ' + rendered if rendered else ''}>"
        return opening[:200]


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("#document", {}, 0, 0)
        self.stack = [self.root]
        self.elements = []
        self.counter = 0

    def handle_starttag(self, tag, attrs):
        parent = self.stack[-1]
        self.counter += 1
        node = Element(tag, {k: (v if v is not None else "") for k, v in attrs},
                       self.getpos()[0], self.getpos()[1], parent, self.counter)
        parent.children.append(node)
        self.elements.append(node)
        if tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        parent = self.stack[-1]
        self.counter += 1
        node = Element(tag, {k: (v if v is not None else "") for k, v in attrs},
                       self.getpos()[0], self.getpos()[1], parent, self.counter)
        parent.children.append(node)
        self.elements.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].text += data


class Audit:
    def __init__(self, path, source):
        self.path = path
        self.source = source
        self.findings = []
        self.counter = 0
        parser = DocumentParser()
        parser.feed(source)
        parser.close()
        self.doc = parser.root
        self.elements = parser.elements
        self.by_tag = {}
        for node in self.elements:
            self.by_tag.setdefault(node.tag, []).append(node)
        self.ids = {}
        for node in self.elements:
            node_id = node.get("id")
            if node_id:
                self.ids.setdefault(node_id, []).append(node)

    def add(self, sc, sc_title, level, severity, node, issue, impact, fix,
            verification, confidence="confirmed"):
        self.counter += 1
        line = node.line if node is not None else 0
        self.findings.append({
            "id": f"F-{self.counter:03d}",
            "sc": sc,
            "sc_title": sc_title,
            "level": level,
            "severity": severity,
            "location": f"{self.path}:{line}" if line else self.path,
            "selector": describe(node) if node is not None else None,
            "issue": issue,
            "impact": impact,
            "evidence": node.snippet() if node is not None else None,
            "fix": fix,
            "verification": verification,
            "source": "tool",
            "confidence": confidence,
        })

    # Each check below maps to one or more success criteria.

    def check_document(self):
        html_nodes = self.by_tag.get("html", [])
        if html_nodes:
            lang = html_nodes[0].get("lang", "").strip()
            if not lang:
                self.add("3.1.1", "Language of Page", "A", "high", html_nodes[0],
                         "The html element has no lang attribute.",
                         "Screen readers fall back to the user's default voice, so the "
                         "page may be read with the wrong pronunciation rules.",
                         'Add lang with a valid BCP 47 tag, for example <html lang="en">.',
                         "Check the html element has lang set to the page's language.")
            elif not re.fullmatch(r"[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*", lang):
                self.add("3.1.1", "Language of Page", "A", "medium", html_nodes[0],
                         f'The lang value "{lang}" is not a valid BCP 47 language tag.',
                         "An unrecognised tag is ignored, leaving the page with no "
                         "declared language.",
                         'Use a valid tag such as "en", "en-GB" or "fr-CA".',
                         "Validate the tag against BCP 47.")

        titles = [n for n in self.by_tag.get("title", [])
                  if n.parent is not None and n.parent.tag != "svg"]
        if not titles or not titles[0].inner_text():
            self.add("2.4.2", "Page Titled", "A", "high", titles[0] if titles else None,
                     "The page has no title element, or the title is empty.",
                     "Screen reader users hear the title first and use it to tell tabs "
                     "and windows apart. Without it they hear the URL.",
                     "Add a title that names this page and then the site.",
                     "Confirm the browser tab shows a descriptive title.")

        for meta in self.by_tag.get("meta", []):
            if meta.get("name", "").lower() != "viewport":
                continue
            content = meta.get("content", "").lower()
            if "user-scalable=no" in content.replace(" ", "") or \
               "user-scalable=0" in content.replace(" ", ""):
                self.add("1.4.4", "Resize Text", "AA", "high", meta,
                         "The viewport meta tag disables pinch zoom with user-scalable=no.",
                         "Users who need to magnify text cannot zoom the page at all.",
                         "Remove user-scalable=no from the viewport content.",
                         "Pinch zoom the page on a touch device.")
            max_scale = re.search(r"maximum-scale\s*=\s*([\d.]+)", content)
            if max_scale and float(max_scale.group(1)) < 2:
                self.add("1.4.4", "Resize Text", "AA", "high", meta,
                         f"The viewport caps zoom at {max_scale.group(1)}x.",
                         "Text cannot reach 200 percent, which the criterion requires.",
                         "Remove maximum-scale, or set it to 5 or higher.",
                         "Zoom to 200 percent and confirm no content is lost.")

    def check_images(self):
        for img in self.by_tag.get("img", []):
            role = img.get("role", "").lower()
            hidden = img.get("aria-hidden", "").lower() == "true"
            alt = img.get("alt")
            has_aria_name = bool(img.get("aria-label") or img.get("aria-labelledby"))
            if alt is None and not has_aria_name and not hidden and role != "presentation":
                self.add("1.1.1", "Non-text Content", "A", "high", img,
                         "The img element has no alt attribute.",
                         "Screen readers announce the filename or nothing at all, so the "
                         "image's information is lost.",
                         'Add alt with a text alternative, or alt="" if the image is '
                         "purely decorative.",
                         "Confirm the image is announced with meaningful text, or skipped "
                         "if decorative.")
                continue
            if alt is None:
                continue
            value = alt.strip().lower()
            if not value:
                continue
            base = re.sub(r"\.(png|jpe?g|gif|svg|webp|avif|bmp)$", "", value)
            if base in BAD_ALT or value in BAD_ALT:
                self.add("1.1.1", "Non-text Content", "A", "medium", img,
                         f'The alt text "{alt.strip()}" describes the medium, not the '
                         "content.",
                         "A screen reader user learns that an image exists but not what "
                         "it conveys.",
                         "Replace it with what the image tells the reader, or use "
                         'alt="" if it adds nothing.',
                         "Read the alt aloud with the image hidden and check it still "
                         "makes sense.")
            elif re.fullmatch(r"[\w\-. ]+\.(png|jpe?g|gif|svg|webp|avif)", value):
                self.add("1.1.1", "Non-text Content", "A", "medium", img,
                         f'The alt text is a filename: "{alt.strip()}".',
                         "The filename is read out character by character in some cases "
                         "and carries no meaning.",
                         "Replace it with a description of the image's purpose.",
                         "Read the alt aloud and check it conveys the image's point.")
            elif value.startswith(("image of", "picture of", "graphic of", "photo of")):
                self.add("1.1.1", "Non-text Content", "A", "low", img,
                         f'The alt text starts with "{value.split(" of")[0]} of".',
                         "Screen readers already announce the element as an image, so "
                         "the prefix is repeated.",
                         "Remove the prefix and start with the content.",
                         "Listen to the announcement and confirm it is not redundant.")

        for area in self.by_tag.get("area", []):
            if not (area.has("alt") or area.get("aria-label") or area.get("aria-labelledby")):
                self.add("1.1.1", "Non-text Content", "A", "high", area,
                         "An image map area has no alt text.",
                         "The clickable region has no name, so it cannot be identified "
                         "or operated by name.",
                         "Add alt describing the link destination.",
                         "Tab to the area and confirm it announces a destination.")

        for svg in self.by_tag.get("svg", []):
            if svg.get("aria-hidden", "").lower() == "true":
                continue
            role = svg.get("role", "").lower()
            interactive_parent = any(
                a.tag in ("a", "button") for a in svg.ancestors())
            named = bool(svg.get("aria-label") or svg.get("aria-labelledby")
                         or any(c.tag == "title" for c in svg.children))
            if role in ("img", "graphics-document") and not named:
                self.add("1.1.1", "Non-text Content", "A", "medium", svg,
                         'The svg has role="img" but no accessible name.',
                         "The graphic is exposed to assistive technology with nothing to "
                         "announce.",
                         "Add aria-label, or a <title> as the first child referenced by "
                         "aria-labelledby.",
                         "Check the accessibility tree shows a name for the graphic.")
            elif not role and not named and not interactive_parent:
                self.add("1.1.1", "Non-text Content", "A", "advisory", svg,
                         "The svg has no role and no accessible name.",
                         "Support varies: some screen readers announce the element, "
                         "others skip it, so the outcome is unpredictable.",
                         'Add aria-hidden="true" if decorative, or role="img" with '
                         "aria-label if it carries information.",
                         "Decide whether the graphic is decorative and mark it either way.")

    def accessible_name(self, node):
        """Approximate the accessible name from markup alone."""
        if node.get("aria-label", "").strip():
            return node.get("aria-label").strip()
        labelledby = node.get("aria-labelledby", "").strip()
        if labelledby:
            parts = []
            for ref in labelledby.split():
                for target in self.ids.get(ref, []):
                    parts.append(target.inner_text())
            if any(parts):
                return " ".join(p for p in parts if p)
        text = node.inner_text()
        if text:
            return text
        for child in node.children:
            if child.tag == "img":
                alt = child.get("alt", "").strip()
                if alt:
                    return alt
            if child.tag == "svg":
                for sub in child.children:
                    if sub.tag == "title" and sub.inner_text():
                        return sub.inner_text()
                if child.get("aria-label", "").strip():
                    return child.get("aria-label").strip()
        if node.get("title", "").strip():
            return node.get("title").strip()
        if node.tag == "input":
            if node.get("type", "").lower() == "image":
                return node.get("alt", "").strip()
            if node.get("type", "").lower() in ("submit", "reset", "button"):
                return node.get("value", "").strip()
        return ""

    def check_controls(self):
        labels_for = {}
        for label in self.by_tag.get("label", []):
            target = label.get("for")
            if target:
                labels_for.setdefault(target, []).append(label)

        for tag in ("input", "select", "textarea"):
            for field in self.by_tag.get(tag, []):
                field_type = field.get("type", "text").lower() if tag == "input" else tag
                if field_type in UNLABELLED_OK_TYPES and tag == "input":
                    if field_type == "image" and not field.get("alt", "").strip():
                        self.add("1.1.1", "Non-text Content", "A", "high", field,
                                 "An image input has no alt text.",
                                 "The submit control has no name, so it cannot be "
                                 "identified or operated by voice.",
                                 "Add alt describing the action, for example "
                                 'alt="Search".',
                                 "Confirm the control announces its action.")
                    if field_type in ("submit", "reset", "button") and \
                            not field.get("value", "").strip() and \
                            not self.accessible_name(field):
                        self.add("4.1.2", "Name, Role, Value", "A", "critical", field,
                                 "A button input has no value and no accessible name.",
                                 "The control is announced only as 'button', so users "
                                 "cannot tell what it does.",
                                 "Add a value attribute naming the action.",
                                 "Focus the control and confirm it announces its action.")
                    continue
                if field.get("aria-hidden", "").lower() == "true":
                    continue

                field_id = field.get("id")
                wrapped = any(a.tag == "label" for a in field.ancestors())
                named = bool(
                    (field_id and field_id in labels_for) or wrapped
                    or field.get("aria-label", "").strip()
                    or field.get("aria-labelledby", "").strip())
                if not named:
                    placeholder = field.get("placeholder", "").strip()
                    title = field.get("title", "").strip()
                    if placeholder:
                        self.add("3.3.2", "Labels or Instructions", "A", "high", field,
                                 "The field is labelled only by its placeholder.",
                                 "The placeholder disappears as soon as the user types, "
                                 "so they lose the label while filling the field, and "
                                 "some assistive technology never announces it.",
                                 "Add a visible <label for> and keep the placeholder for "
                                 "format hints only.",
                                 "Type in the field and confirm the label is still "
                                 "visible and announced.")
                    elif title:
                        self.add("3.3.2", "Labels or Instructions", "A", "medium", field,
                                 "The field is labelled only by a title attribute.",
                                 "Title text is not shown on touch devices and is not "
                                 "reliably announced.",
                                 "Add a visible <label for> associated with the field.",
                                 "Confirm a visible label is present and associated.")
                    else:
                        self.add("1.3.1", "Info and Relationships", "A", "critical", field,
                                 f"The {tag} element has no associated label.",
                                 "Screen reader users hear the field type and nothing "
                                 "else, so they cannot tell what to enter. Voice control "
                                 "users have no name to speak.",
                                 "Add <label for=\"ID\">, or aria-labelledby pointing at "
                                 "the visible text.",
                                 "Focus the field and confirm it announces its label.")

                autocomplete_needed = field_type in (
                    "email", "tel", "url") or re.search(
                    r"name|email|phone|tel|address|postcode|zip|city|country|"
                    r"cc-|card|birthday|bday", (field.get("name", "") +
                                                field.get("id", "")).lower())
                if tag == "input" and autocomplete_needed:
                    autocomplete = field.get("autocomplete", "").strip().lower()
                    if not autocomplete or autocomplete == "off":
                        self.add("1.3.5", "Identify Input Purpose", "AA", "medium", field,
                                 "A field collecting information about the user has no "
                                 "autocomplete token."
                                 + (" It is set to off." if autocomplete == "off" else ""),
                                 "Users who rely on autofill, including people with motor "
                                 "and cognitive disabilities, must retype the value by "
                                 "hand every time.",
                                 "Add the matching autocomplete token, for example "
                                 'autocomplete="email".',
                                 "Confirm the browser offers to autofill the field.")

        for label in self.by_tag.get("label", []):
            target = label.get("for")
            if target and target not in self.ids:
                self.add("1.3.1", "Info and Relationships", "A", "high", label,
                         f'A label points at id "{target}", which does not exist on '
                         "the page.",
                         "The label is not associated with any field, so the field is "
                         "announced without a name.",
                         "Correct the for value to match the field's id.",
                         "Click the label and confirm focus moves to the field.")
            if not label.inner_text() and not label.get("aria-label"):
                self.add("3.3.2", "Labels or Instructions", "A", "medium", label,
                         "A label element is empty.",
                         "The field it labels is announced with no name.",
                         "Put the field's visible text inside the label.",
                         "Focus the field and confirm it announces a name.")

        for button in self.by_tag.get("button", []):
            if button.get("aria-hidden", "").lower() == "true":
                continue
            if not self.accessible_name(button):
                self.add("4.1.2", "Name, Role, Value", "A", "critical", button,
                         "The button has no accessible name.",
                         "Screen reader users hear only 'button'. Voice control users "
                         "have nothing to say to activate it.",
                         "Add visible text, or aria-label if the button is icon only.",
                         "Focus the button and confirm it announces what it does.")

        radio_groups = {}
        for field in self.by_tag.get("input", []):
            if field.get("type", "").lower() in ("radio", "checkbox"):
                name = field.get("name")
                if name:
                    radio_groups.setdefault(name, []).append(field)
        for name, group in radio_groups.items():
            if len(group) < 2:
                continue
            in_fieldset = any(a.tag == "fieldset" for a in group[0].ancestors())
            grouped = in_fieldset or any(
                a.get("role", "").lower() in ("radiogroup", "group")
                for a in group[0].ancestors())
            if not grouped:
                self.add("1.3.1", "Info and Relationships", "A", "medium", group[0],
                         f'The "{name}" group of {len(group)} inputs is not wrapped in a '
                         "fieldset with a legend.",
                         "Screen reader users hear each option's label but not the "
                         "question the options answer.",
                         "Wrap the group in <fieldset> with a <legend>, or use "
                         'role="radiogroup" with an accessible name.',
                         "Focus an option and confirm the group question is announced.")

    def check_links(self):
        for link in self.by_tag.get("a", []):
            if link.get("aria-hidden", "").lower() == "true":
                continue
            href = link.get("href")
            name = self.accessible_name(link).strip()
            if href is None and not link.get("role"):
                continue
            if not name:
                self.add("2.4.4", "Link Purpose (In Context)", "A", "critical", link,
                         "The link has no accessible name.",
                         "Screen reader users hear 'link' with no destination. An "
                         "unnamed link is unusable.",
                         "Add link text, or aria-label if the link is an icon.",
                         "Tab to the link and confirm it announces its destination.")
                continue
            plain = re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()
            if plain in GENERIC_LINK_TEXT:
                self.add("2.4.4", "Link Purpose (In Context)", "A", "medium", link,
                         f'The link text "{name}" does not say where the link goes.',
                         "Screen reader users often browse a list of links out of "
                         "context, where repeated generic text is indistinguishable.",
                         "Rewrite the link text to name the destination, or extend the "
                         "accessible name with aria-label.",
                         "Read the link text alone and check the destination is clear.")
            if href and href.strip().lower().startswith(("http://", "https://", "www.")) \
                    and name.strip().lower() == href.strip().lower():
                self.add("2.4.4", "Link Purpose (In Context)", "A", "low", link,
                         "The link text is a raw URL.",
                         "Screen readers read URLs character by character, which is slow "
                         "and hard to follow.",
                         "Replace the URL with text naming the destination.",
                         "Confirm the link announces a readable destination.")

        body_links = [n for n in self.by_tag.get("a", []) if n.get("href")]
        if body_links:
            first_five = body_links[:5]
            has_skip = any(
                (n.get("href", "").startswith("#")
                 and re.search(r"skip|jump|main|content",
                               (self.accessible_name(n) + n.get("href", "")).lower()))
                for n in first_five)
            landmark = bool(self.by_tag.get("main")) or any(
                n.get("role", "").lower() == "main" for n in self.elements)
            if not has_skip and not landmark and len(body_links) > 10:
                self.add("2.4.1", "Bypass Blocks", "A", "medium", None,
                         "No skip link and no main landmark were found on a page with "
                         f"{len(body_links)} links.",
                         "Keyboard and screen reader users must move through the whole "
                         "navigation on every page before reaching the content.",
                         "Add a skip link as the first focusable element, and wrap the "
                         "content in <main>.",
                         "Press Tab on a fresh page load and confirm a skip link appears "
                         "and moves focus.")

    def check_headings(self):
        headings = [n for n in self.elements if re.fullmatch(r"h[1-6]", n.tag)]
        h1s = [h for h in headings if h.tag == "h1"]
        if headings and not h1s:
            self.add("1.3.1", "Info and Relationships", "A", "medium", headings[0],
                     "The page has headings but no h1.",
                     "Screen reader users navigate by heading level and lose the "
                     "top-level entry point for the page.",
                     "Make the page's main heading an h1.",
                     "List the page's headings and confirm exactly one h1 opens it.")
        if len(h1s) > 1:
            self.add("1.3.1", "Info and Relationships", "A", "low", h1s[1],
                     f"The page has {len(h1s)} h1 elements.",
                     "More than one top-level heading makes the page structure "
                     "ambiguous when navigating by heading.",
                     "Keep one h1 and demote the others to the level that matches "
                     "their place in the structure.",
                     "Review the heading outline for a single top level.")
        previous = 0
        for heading in headings:
            level = int(heading.tag[1])
            if previous and level > previous + 1:
                self.add("1.3.1", "Info and Relationships", "A", "medium", heading,
                         f"The heading level jumps from h{previous} to h{level}.",
                         "A skipped level makes screen reader users think content is "
                         "missing, and it breaks the document outline.",
                         f"Change this heading to h{previous + 1}, or add the "
                         "intermediate heading the structure implies.",
                         "Read the heading outline and confirm levels descend by one.")
            previous = level
            if not heading.inner_text().strip():
                self.add("2.4.6", "Headings and Labels", "AA", "medium", heading,
                         f"The {heading.tag} element is empty.",
                         "An empty heading appears in the heading list with nothing to "
                         "announce.",
                         "Give the heading text, or remove it if it is styling only.",
                         "Check the heading list contains no blank entries.")

    def check_tables(self):
        for table in self.by_tag.get("table", []):
            role = table.get("role", "").lower()
            if role in ("presentation", "none"):
                continue
            headers = [c for c in walk(table) if c.tag == "th"]
            rows = [c for c in walk(table) if c.tag == "tr"]
            cells = [c for c in walk(table) if c.tag == "td"]
            if len(rows) < 2 or not cells:
                continue
            if not headers:
                self.add("1.3.1", "Info and Relationships", "A", "high", table,
                         "A data table has no th elements.",
                         "Screen reader users hear cell values with no column or row "
                         "headers, so a table of numbers becomes a list of numbers.",
                         "Mark header cells as <th>, and add scope=\"col\" or "
                         'scope="row". If the table is layout only, add '
                         'role="presentation".',
                         "Navigate the table with a screen reader and confirm headers "
                         "are announced with each cell.")
                continue
            without_scope = [h for h in headers
                             if not h.get("scope") and not h.get("id")]
            if without_scope and len(headers) > 2:
                self.add("1.3.1", "Info and Relationships", "A", "medium",
                         without_scope[0],
                         f"{len(without_scope)} of {len(headers)} header cells have no "
                         "scope attribute.",
                         "Without scope, the association between headers and cells is "
                         "guessed by the browser and is often wrong in tables with both "
                         "row and column headers.",
                         'Add scope="col" or scope="row" to each th.',
                         "Confirm each cell announces the right row and column header.")

    def check_frames_and_aria(self):
        for frame in self.by_tag.get("iframe", []) + self.by_tag.get("frame", []):
            if frame.get("aria-hidden", "").lower() == "true":
                continue
            if not (frame.get("title", "").strip()
                    or frame.get("aria-label", "").strip()
                    or frame.get("aria-labelledby", "").strip()):
                self.add("4.1.2", "Name, Role, Value", "A", "medium", frame,
                         "The iframe has no title.",
                         "Screen reader users hear 'frame' with no indication of what it "
                         "contains, so they cannot decide whether to enter it.",
                         'Add title describing the frame content, for example '
                         'title="Payment form".',
                         "Confirm the frame is announced with a meaningful name.")

        for node in self.elements:
            for attr in ("aria-labelledby", "aria-describedby", "aria-controls",
                         "aria-owns", "aria-details", "aria-errormessage"):
                value = node.get(attr, "").strip()
                if not value:
                    continue
                missing = [ref for ref in value.split() if ref not in self.ids]
                if missing:
                    severity = "high" if attr == "aria-labelledby" else "medium"
                    self.add("4.1.2", "Name, Role, Value", "A", severity, node,
                             f'{attr} references id "{" ".join(missing)}", which does not '
                             "exist on the page.",
                             "The reference is dropped, so the element loses the name, "
                             "description, or relationship it was meant to have.",
                             "Correct the id, or remove the attribute if the target was "
                             "deleted.",
                             "Check the accessibility tree shows the intended name or "
                             "description.")

        for id_value, nodes in self.ids.items():
            if len(nodes) < 2:
                continue
            referenced = any(
                id_value in (n.get(a, "") or "").split()
                for n in self.elements
                for a in ("aria-labelledby", "aria-describedby", "aria-controls",
                          "aria-owns", "for", "headers")
            )
            if referenced:
                self.add("1.3.1", "Info and Relationships", "A", "high", nodes[1],
                         f'The id "{id_value}" appears {len(nodes)} times and is used in '
                         "a label or ARIA reference.",
                         "Only the first match resolves, so some elements silently lose "
                         "their label or relationship.",
                         "Make each id unique and update the references.",
                         "Confirm every referencing element resolves to the right target.")

        for node in self.elements:
            if node.get("aria-hidden", "").lower() != "true":
                continue
            focusable = node.tag in INTERACTIVE and node.tag != "a" or \
                (node.tag == "a" and node.has("href")) or \
                (node.has("tabindex") and node.get("tabindex", "") != "-1")
            if focusable:
                self.add("4.1.2", "Name, Role, Value", "A", "high", node,
                         'A focusable element is marked aria-hidden="true".',
                         "Keyboard users still reach the control, but screen reader users "
                         "hear nothing when focus lands on it, which reads as a broken "
                         "or empty stop.",
                         "Remove aria-hidden, or make the element unfocusable with "
                         'tabindex="-1" and the inert attribute.',
                         "Tab through and confirm every focus stop is announced.")

        for node in self.elements:
            tabindex = node.get("tabindex", "").strip()
            if tabindex and re.fullmatch(r"[1-9]\d*", tabindex):
                self.add("2.4.3", "Focus Order", "A", "medium", node,
                         f'The element has a positive tabindex of {tabindex}.',
                         "Positive values pull the element out of the document order and "
                         "put it ahead of everything else, so the tab order stops "
                         "matching the visual order.",
                         'Use tabindex="0" and order the element in the DOM instead.',
                         "Tab through the page and confirm the order follows the layout.")

        for node in self.elements:
            if node.tag in INTERACTIVE or node.tag in ("html", "body"):
                continue
            handlers = [a for a in node.attrs if a.lower() in
                        ("onclick", "onmousedown", "onmouseup")]
            if not handlers:
                continue
            role = node.get("role", "").lower()
            tabindex = node.get("tabindex", "").strip()
            if role in ("", "presentation", "none") or not tabindex:
                self.add("2.1.1", "Keyboard", "A", "high", node,
                         f"A <{node.tag}> has a click handler but "
                         + ("no role" if not role else f'role="{role}"')
                         + (" and no tabindex." if not tabindex else "."),
                         "The control cannot be reached or activated with a keyboard, so "
                         "keyboard and switch users cannot use it at all.",
                         "Use a <button>. If the element must stay, add role=\"button\", "
                         'tabindex="0", and Enter and Space key handlers.',
                         "Tab to the control and activate it with Enter and Space.")

    def check_media(self):
        for tag in ("video", "audio"):
            for node in self.by_tag.get(tag, []):
                if node.has("autoplay") and not node.has("muted"):
                    sc, title, level = ("1.4.2", "Audio Control", "A")
                    self.add(sc, title, level, "high", node,
                             f"The {tag} element autoplays with sound.",
                             "Audio starting on its own drowns out a screen reader and "
                             "can make the page unusable. This criterion applies to the "
                             "whole page under the non-interference requirement.",
                             "Remove autoplay, or start muted with a visible control to "
                             "unmute.",
                             "Load the page and confirm no audio starts by itself.")
                if node.has("autoplay") and tag == "video":
                    # A native player with controls supplies the pause mechanism the
                    # criterion asks for, so reporting it as a failure is wrong. The
                    # residual concern is reduced-motion preference, which is an
                    # advisory rather than a 2.2.2 failure.
                    if node.has("controls"):
                        self.add("2.3.3", "Animation from Interactions", "AAA",
                                 "advisory", node,
                                 "The video autoplays. Controls are present, so 2.2.2 is "
                                 "satisfied, but the motion still starts by itself.",
                                 "Users with vestibular disorders see motion they did not "
                                 "ask for, even though they can now stop it.",
                                 "Respect prefers-reduced-motion, or remove autoplay.",
                                 "Set the reduced-motion preference and confirm the video "
                                 "does not start on its own.")
                    else:
                        self.add("2.2.2", "Pause, Stop, Hide", "A", "medium", node,
                                 "The video autoplays with no controls attribute.",
                                 "Motion that runs for more than five seconds with no "
                                 "pause control distracts users with attention and "
                                 "vestibular disorders, and there is no way to stop it.",
                                 "Add controls, or provide a visible pause control.",
                                 "Confirm the motion can be paused without leaving the "
                                 "page.")
                if not node.has("controls") and not node.get("aria-label"):
                    self.add("2.1.1", "Keyboard", "A", "medium", node,
                             f"The {tag} element has no controls attribute.",
                             "If the custom player is not fully keyboard operable, there "
                             "is no fallback way to play, pause, or adjust volume.",
                             "Add controls, or verify the custom player is operable by "
                             "keyboard and exposes names and states.",
                             "Operate every player control with the keyboard alone.")
            if tag == "video":
                for node in self.by_tag.get("video", []):
                    tracks = [c for c in walk(node) if c.tag == "track"]
                    captions = [t for t in tracks
                                if t.get("kind", "").lower() in ("captions", "subtitles")]
                    if not captions:
                        self.add("1.2.2", "Captions (Prerecorded)", "A", "high", node,
                                 "The video has no captions track.",
                                 "Deaf and hard of hearing users cannot access the "
                                 "spoken content at all.",
                                 'Add <track kind="captions" src="..." srclang="..." '
                                 'label="...">, with human-checked captions.',
                                 "Turn captions on and check they match the audio, "
                                 "including speaker names.",
                                 confidence="needs-review")

    def run(self):
        self.check_document()
        self.check_images()
        self.check_controls()
        self.check_links()
        self.check_headings()
        self.check_tables()
        self.check_frames_and_aria()
        self.check_media()
        self.findings.sort(
            key=lambda f: (-SEVERITY_ORDER.index(f["severity"]), f["sc"]))
        for index, finding in enumerate(self.findings, 1):
            finding["id"] = f"F-{index:03d}"
        return self.findings


def walk(node):
    for child in node.children:
        yield child
        yield from walk(child)


def describe(node):
    if node is None:
        return None
    parts = [node.tag]
    node_id = node.get("id")
    if node_id:
        parts.append(f"#{node_id}")
    classes = node.get("class", "").split()
    if classes:
        parts.append("." + ".".join(classes[:2]))
    name = node.get("name")
    if name and not node_id:
        parts.append(f'[name="{name}"]')
    return "".join(parts)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Static WCAG checks on HTML source, with no browser required.")
    parser.add_argument("paths", nargs="+", help="HTML files or glob patterns")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit findings JSON on stdout")
    parser.add_argument("--min-severity", choices=SEVERITY_ORDER, default="advisory",
                        help="hide findings below this severity")
    parser.add_argument("--fail-on", choices=SEVERITY_ORDER + ["none"], default="none",
                        help="exit 1 when a finding at or above this severity is found")
    args = parser.parse_args(argv)

    files = []
    for pattern in args.paths:
        if os.path.isfile(pattern):
            files.append(pattern)
        else:
            files.extend(sorted(glob.glob(pattern, recursive=True)))
    if not files:
        print("error: no files matched", file=sys.stderr)
        return 2

    floor = SEVERITY_ORDER.index(args.min_severity)
    all_findings = []
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                source = handle.read()
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        for finding in Audit(path, source).run():
            if SEVERITY_ORDER.index(finding["severity"]) >= floor:
                all_findings.append(finding)

    for index, finding in enumerate(all_findings, 1):
        finding["id"] = f"F-{index:03d}"

    if args.as_json:
        print(json.dumps({
            "tool": "html_audit.py",
            "standard": "WCAG 2.2",
            "files": files,
            "coverage_note": "Static markup checks only. Contrast, reflow, target size, "
                             "focus visibility, focus order, and every criterion "
                             "requiring judgement are not covered here.",
            "findings": all_findings,
        }, indent=2))
    else:
        if not all_findings:
            print(f"No static findings in {len(files)} file(s).")
        for finding in all_findings:
            print(f"[{finding['severity'].upper():8}] {finding['sc']} "
                  f"{finding['sc_title']} ({finding['level']})")
            print(f"           {finding['location']}  {finding['selector'] or ''}")
            print(f"           {finding['issue']}")
            print(f"           Fix: {finding['fix']}\n")
        counts = {}
        for finding in all_findings:
            counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
        if all_findings:
            summary = ", ".join(f"{counts[s]} {s}"
                                for s in reversed(SEVERITY_ORDER) if s in counts)
            print(f"{len(all_findings)} findings in {len(files)} file(s): {summary}")
            print("Static checks only. Contrast, reflow, focus order, and the "
                  "judgement-based criteria still need testing.")

    if args.fail_on != "none":
        threshold = SEVERITY_ORDER.index(args.fail_on)
        if any(SEVERITY_ORDER.index(f["severity"]) >= threshold for f in all_findings):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
