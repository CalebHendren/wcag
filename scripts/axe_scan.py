#!/usr/bin/env python3
"""Run axe-core against a live page or a local HTML file, through Playwright.

A rendered page exposes what static markup cannot: computed contrast, the real
accessibility tree, focus order, target sizes, and elements built at runtime.
This script drives a headless browser, injects axe-core, and converts its
results into the finding schema the wcag skills use.

axe-core reports a subset of WCAG failures. Its "incomplete" results are the
ones it cannot decide alone, and those are surfaced here as needs-review
findings rather than dropped, because they are where the real work is.

Setup, once:
  pip install playwright && playwright install chromium
  npm install axe-core          (or let the script fetch it from a CDN)

Usage:
  axe_scan.py https://example.com
  axe_scan.py page.html --json > findings.json
  axe_scan.py https://example.com --tags wcag2a,wcag2aa,wcag22aa
  axe_scan.py https://example.com --viewport 320x800     # check reflow states
  axe_scan.py https://example.com --wait-for "#app" --screenshot out.png
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import sys
import urllib.request

AXE_CDN = "https://cdn.jsdelivr.net/npm/axe-core@4/axe.min.js"

# axe tag sets. wcag22aa is only meaningful with axe-core 4.9 or newer.
DEFAULT_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]

# axe impact -> our severity. axe's "serious" is usually a real blocker in
# context, so it maps up rather than down.
IMPACT_TO_SEVERITY = {
    "critical": "critical",
    "serious": "high",
    "moderate": "medium",
    "minor": "low",
}


def find_axe_source(explicit: str | None) -> tuple[str, str]:
    """Return (javascript source, where it came from)."""
    candidates = []
    if explicit:
        candidates.append(pathlib.Path(explicit))
    here = pathlib.Path(__file__).resolve().parent
    candidates += [
        here / "vendor" / "axe.min.js",
        here.parent / "node_modules" / "axe-core" / "axe.min.js",
        pathlib.Path.cwd() / "node_modules" / "axe-core" / "axe.min.js",
    ]
    for path in candidates:
        if path.is_file():
            return path.read_text(encoding="utf-8"), str(path)
    print("axe-core not found locally, trying the CDN. Many managed environments "
          "block it;\nif this fails, run `npm install axe-core` in this directory.",
          file=sys.stderr)
    try:
        with urllib.request.urlopen(AXE_CDN, timeout=30) as response:
            return response.read().decode("utf-8"), AXE_CDN
    except Exception as exc:
        raise SystemExit(
            f"Could not load axe-core: {exc}\n\n"
            "Fix it with either of these, in order of preference:\n"
            "  npm install axe-core          (then re-run; the script finds it)\n"
            "  --axe-path /path/to/axe.min.js\n\n"
            "Without a browser scan, run scripts/html_audit.py on the source instead. "
            "It covers less, and it says so in its output.")



def find_chromium() -> str | None:
    """Locate a Chromium binary when Playwright's own download is missing.

    Managed environments often ship a browser whose build number does not match
    the Playwright package, which makes the default launch fail with a "run
    playwright install" message even though a working browser is present.
    """
    if os.environ.get("CHROMIUM_PATH"):
        return os.environ["CHROMIUM_PATH"]
    roots = [pathlib.Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")),
             pathlib.Path("/opt/pw-browsers"),
             pathlib.Path.home() / ".cache" / "ms-playwright"]
    for root in roots:
        if not root or not root.is_dir():
            continue
        matches = sorted(root.glob("chromium-*/chrome-linux/chrome"))
        matches += sorted(root.glob("chromium-*/chrome-mac/Chromium.app/Contents/"
                                    "MacOS/Chromium"))
        if matches:
            return str(matches[-1])
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def criterion_from_tags(tags: list[str]) -> str | None:
    """Read the success criterion number out of axe's tag list.

    axe encodes criteria as digits with no separators: "wcag111" is 1.1.1 and
    "wcag1410" is 1.4.10. The criterion number is everything after the principle
    and guideline digits, so a naive fixed-length parse silently drops every
    two-digit criterion, which is most of what WCAG 2.1 and 2.2 added.
    """
    for tag in tags:
        if not tag.startswith("wcag"):
            continue
        digits = tag[4:]
        if not digits.isdigit() or len(digits) < 3:
            continue
        return f"{digits[0]}.{digits[1]}.{int(digits[2:])}"
    return None


def to_finding(rule: dict, node: dict, index: int, needs_review: bool,
               page_url: str) -> dict:
    target = node.get("target") or []
    selector = target[0] if target else None
    if isinstance(selector, list):
        selector = " >>> ".join(selector)
    checks = (node.get("any") or []) + (node.get("all") or []) + \
             (node.get("none") or [])
    detail = "; ".join(c.get("message", "") for c in checks if c.get("message"))
    tags = rule.get("tags", [])
    level = "AA" if any(t.endswith("aa") for t in tags) else \
            "AAA" if any(t.endswith("aaa") for t in tags) else \
            "A" if any(t.endswith(("2a", "21a", "22a")) for t in tags) else "n/a"
    sc = criterion_from_tags(tags)
    severity = IMPACT_TO_SEVERITY.get(node.get("impact") or rule.get("impact"), "medium")
    if needs_review:
        severity = "medium" if severity in ("critical", "high") else severity
    return {
        "id": f"F-{index:03d}",
        "sc": sc or "see rule",
        "sc_title": rule.get("help", rule.get("id")),
        "level": level,
        "severity": severity,
        "location": page_url,
        "selector": selector,
        "issue": rule.get("description", rule.get("help", "")),
        "impact": detail or "See the axe rule documentation for the user impact.",
        "evidence": (node.get("html") or "")[:300],
        "fix": node.get("failureSummary") or
               f"See {rule.get('helpUrl', 'the axe rule documentation')}.",
        "verification": "Re-run the scan and confirm the rule no longer reports "
                        "this element.",
        "source": "tool",
        "confidence": "needs-review" if needs_review else "confirmed",
        "rule": rule.get("id"),
        "help_url": rule.get("helpUrl"),
        "tags": tags,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run axe-core against a rendered page through Playwright.")
    parser.add_argument("target", help="URL, or a path to a local HTML file")
    parser.add_argument("--tags", default=",".join(DEFAULT_TAGS),
                        help="comma separated axe tags to run")
    parser.add_argument("--viewport", default="1280x900",
                        help="viewport as WIDTHxHEIGHT. Use 320x800 to test reflow.")
    parser.add_argument("--wait-for", help="CSS selector to wait for before scanning")
    parser.add_argument("--wait-ms", type=int, default=1500,
                        help="extra settle time in milliseconds")
    parser.add_argument("--axe-path", help="path to axe.min.js")
    parser.add_argument("--screenshot", help="save a full page screenshot here")
    parser.add_argument("--include-incomplete", action="store_true", default=True,
                        help="include axe's incomplete results as needs-review "
                             "findings (on by default)")
    parser.add_argument("--no-incomplete", action="store_false", dest="include_incomplete")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "Playwright is not installed. Install it with:\n"
            "  pip install playwright && playwright install chromium\n"
            "Without a browser, use scripts/html_audit.py on the source instead. "
            "It covers less, and it says so.")

    axe_source, axe_origin = find_axe_source(args.axe_path)
    width, _, height = args.viewport.partition("x")
    url = args.target
    if not url.startswith(("http://", "https://", "file://")):
        url = pathlib.Path(url).resolve().as_uri()

    executable = find_chromium()

    with sync_playwright() as play:
        launch_kwargs = {"headless": True,
                         "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        try:
            browser = play.chromium.launch(**launch_kwargs)
        except Exception:
            if not executable:
                raise
            launch_kwargs["executable_path"] = executable
            browser = play.chromium.launch(**launch_kwargs)
        page = browser.new_page(
            viewport={"width": int(width), "height": int(height or 900)})
        page.goto(url, wait_until="load", timeout=60000)
        if args.wait_for:
            page.wait_for_selector(args.wait_for, timeout=30000)
        page.wait_for_timeout(args.wait_ms)
        if args.screenshot:
            page.screenshot(path=args.screenshot, full_page=True)
        page.add_script_tag(content=axe_source)
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        results = page.evaluate(
            """(tags) => axe.run(document, {
                   runOnly: {type: 'tag', values: tags},
                   resultTypes: ['violations', 'incomplete']
               }).then(r => ({
                   violations: r.violations,
                   incomplete: r.incomplete,
                   passes: r.passes ? r.passes.length : 0,
                   inapplicable: r.inapplicable ? r.inapplicable.length : 0,
                   url: r.url,
                   engine: r.testEngine
               }))""",
            tags)
        title = page.title()
        browser.close()

    findings = []
    for rule in results["violations"]:
        for node in rule.get("nodes", []):
            findings.append(to_finding(rule, node, len(findings) + 1, False,
                                       results.get("url", url)))
    if args.include_incomplete:
        for rule in results.get("incomplete", []):
            for node in rule.get("nodes", []):
                findings.append(to_finding(rule, node, len(findings) + 1, True,
                                           results.get("url", url)))

    order = ["advisory", "low", "medium", "high", "critical"]
    findings.sort(key=lambda f: (-order.index(f["severity"]),
                                 f["confidence"] == "needs-review"))
    for index, finding in enumerate(findings, 1):
        finding["id"] = f"F-{index:03d}"

    payload = {
        "tool": "axe_scan.py",
        "engine": results.get("engine"),
        "axe_source": axe_origin,
        "standard": "WCAG 2.2",
        "url": results.get("url", url),
        "page_title": title,
        "viewport": args.viewport,
        "tags": tags,
        "rules_passed": results.get("passes"),
        "rules_inapplicable": results.get("inapplicable"),
        "coverage_note": "axe-core reports a subset of WCAG failures. Reading order, "
                         "alt text quality, heading meaning, link purpose, error message "
                         "usefulness, caption accuracy, and keyboard operability of "
                         "custom widgets still need a person.",
        "findings": findings,
    }

    if args.as_json:
        print(json.dumps(payload, indent=2))
        return 0

    print(f"{payload['url']}")
    print(f"  title      {title}")
    print(f"  viewport   {args.viewport}")
    print(f"  axe        {axe_origin}")
    print(f"  rules run  {len(tags)} tag sets, {results.get('passes')} rules passed\n")
    confirmed = [f for f in findings if f["confidence"] == "confirmed"]
    review = [f for f in findings if f["confidence"] == "needs-review"]
    for finding in confirmed:
        print(f"[{finding['severity'].upper():8}] {finding['rule']}  "
              f"({finding['sc']} {finding['level']})")
        print(f"           {finding['selector']}")
        print(f"           {finding['issue']}\n")
    if review:
        print(f"{len(review)} result(s) axe could not decide alone. Check these by hand:")
        for finding in review:
            print(f"  - {finding['rule']}: {finding['selector']}")
    print(f"\n{len(confirmed)} confirmed, {len(review)} needing review.")
    print(payload["coverage_note"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
