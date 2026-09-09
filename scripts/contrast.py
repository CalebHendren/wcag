#!/usr/bin/env python3
"""WCAG contrast ratios for text and non-text content.

Checks a foreground/background pair against WCAG 2.2 success criteria
1.4.3 Contrast (Minimum), 1.4.6 Contrast (Enhanced) and 1.4.11 Non-text Contrast.

Accepts hex (#rgb, #rrggbb, #rrggbbaa), rgb()/rgba(), hsl()/hsla() and the
CSS named colors. Semi-transparent foregrounds are composited over the
background before the ratio is computed, which is what a browser does and what
eyeballing a swatch gets wrong.

Usage:
  contrast.py "#767676" "#ffffff"
  contrast.py "rgba(0,0,0,0.54)" "white" --size 18pt --bold
  contrast.py --batch pairs.json --json

Batch input is a JSON list of objects with "fg", "bg" and optional "label",
"size" (e.g. "14pt", "24px", "1.5rem") and "bold".

Exit status is 1 when any checked pair fails the level requested with --level
(default AA), so this can gate a build.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# The 148 CSS named colors, from the CSS Color Module.
NAMED = {
    "aliceblue": "#f0f8ff", "antiquewhite": "#faebd7", "aqua": "#00ffff",
    "aquamarine": "#7fffd4", "azure": "#f0ffff", "beige": "#f5f5dc",
    "bisque": "#ffe4c4", "black": "#000000", "blanchedalmond": "#ffebcd",
    "blue": "#0000ff", "blueviolet": "#8a2be2", "brown": "#a52a2a",
    "burlywood": "#deb887", "cadetblue": "#5f9ea0", "chartreuse": "#7fff00",
    "chocolate": "#d2691e", "coral": "#ff7f50", "cornflowerblue": "#6495ed",
    "cornsilk": "#fff8dc", "crimson": "#dc143c", "cyan": "#00ffff",
    "darkblue": "#00008b", "darkcyan": "#008b8b", "darkgoldenrod": "#b8860b",
    "darkgray": "#a9a9a9", "darkgrey": "#a9a9a9", "darkgreen": "#006400",
    "darkkhaki": "#bdb76b", "darkmagenta": "#8b008b", "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00", "darkorchid": "#9932cc", "darkred": "#8b0000",
    "darksalmon": "#e9967a", "darkseagreen": "#8fbc8f", "darkslateblue": "#483d8b",
    "darkslategray": "#2f4f4f", "darkslategrey": "#2f4f4f", "darkturquoise": "#00ced1",
    "darkviolet": "#9400d3", "deeppink": "#ff1493", "deepskyblue": "#00bfff",
    "dimgray": "#696969", "dimgrey": "#696969", "dodgerblue": "#1e90ff",
    "firebrick": "#b22222", "floralwhite": "#fffaf0", "forestgreen": "#228b22",
    "fuchsia": "#ff00ff", "gainsboro": "#dcdcdc", "ghostwhite": "#f8f8ff",
    "gold": "#ffd700", "goldenrod": "#daa520", "gray": "#808080",
    "grey": "#808080", "green": "#008000", "greenyellow": "#adff2f",
    "honeydew": "#f0fff0", "hotpink": "#ff69b4", "indianred": "#cd5c5c",
    "indigo": "#4b0082", "ivory": "#fffff0", "khaki": "#f0e68c",
    "lavender": "#e6e6fa", "lavenderblush": "#fff0f5", "lawngreen": "#7cfc00",
    "lemonchiffon": "#fffacd", "lightblue": "#add8e6", "lightcoral": "#f08080",
    "lightcyan": "#e0ffff", "lightgoldenrodyellow": "#fafad2", "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3", "lightgreen": "#90ee90", "lightpink": "#ffb6c1",
    "lightsalmon": "#ffa07a", "lightseagreen": "#20b2aa", "lightskyblue": "#87cefa",
    "lightslategray": "#778899", "lightslategrey": "#778899", "lightsteelblue": "#b0c4de",
    "lightyellow": "#ffffe0", "lime": "#00ff00", "limegreen": "#32cd32",
    "linen": "#faf0e6", "magenta": "#ff00ff", "maroon": "#800000",
    "mediumaquamarine": "#66cdaa", "mediumblue": "#0000cd", "mediumorchid": "#ba55d3",
    "mediumpurple": "#9370db", "mediumseagreen": "#3cb371", "mediumslateblue": "#7b68ee",
    "mediumspringgreen": "#00fa9a", "mediumturquoise": "#48d1cc",
    "mediumvioletred": "#c71585", "midnightblue": "#191970", "mintcream": "#f5fffa",
    "mistyrose": "#ffe4e1", "moccasin": "#ffe4b5", "navajowhite": "#ffdead",
    "navy": "#000080", "oldlace": "#fdf5e6", "olive": "#808000",
    "olivedrab": "#6b8e23", "orange": "#ffa500", "orangered": "#ff4500",
    "orchid": "#da70d6", "palegoldenrod": "#eee8aa", "palegreen": "#98fb98",
    "paleturquoise": "#afeeee", "palevioletred": "#db7093", "papayawhip": "#ffefd5",
    "peachpuff": "#ffdab9", "peru": "#cd853f", "pink": "#ffc0cb",
    "plum": "#dda0dd", "powderblue": "#b0e0e6", "purple": "#800080",
    "rebeccapurple": "#663399", "red": "#ff0000", "rosybrown": "#bc8f8f",
    "royalblue": "#4169e1", "saddlebrown": "#8b4513", "salmon": "#fa8072",
    "sandybrown": "#f4a460", "seagreen": "#2e8b57", "seashell": "#fff5ee",
    "sienna": "#a0522d", "silver": "#c0c0c0", "skyblue": "#87ceeb",
    "slateblue": "#6a5acd", "slategray": "#708090", "slategrey": "#708090",
    "snow": "#fffafa", "springgreen": "#00ff7f", "steelblue": "#4682b4",
    "tan": "#d2b48c", "teal": "#008080", "thistle": "#d8bfd8",
    "tomato": "#ff6347", "turquoise": "#40e0d0", "violet": "#ee82ee",
    "wheat": "#f5deb3", "white": "#ffffff", "whitesmoke": "#f5f5f5",
    "yellow": "#ffff00", "yellowgreen": "#9acd32", "transparent": "#00000000",
}


class ColorError(ValueError):
    """Raised when a color string cannot be parsed."""


def _clamp(value: float, low: float = 0.0, high: float = 255.0) -> float:
    return max(low, min(high, value))


def _hsl_to_rgb(h: float, s: float, lightness: float) -> tuple[float, float, float]:
    h = h % 360 / 360.0
    if s == 0:
        v = lightness * 255
        return v, v, v
    q = lightness * (1 + s) if lightness < 0.5 else lightness + s - lightness * s
    p = 2 * lightness - q

    def channel(t: float) -> float:
        t = t % 1.0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    return (channel(h + 1 / 3) * 255, channel(h) * 255, channel(h - 1 / 3) * 255)


def parse_color(value: str) -> tuple[float, float, float, float]:
    """Return (r, g, b, alpha) with channels 0-255 and alpha 0-1."""
    if value is None:
        raise ColorError("no color given")
    text = str(value).strip().lower()
    if not text:
        raise ColorError("empty color")

    if text in NAMED:
        text = NAMED[text]

    if text.startswith("#"):
        digits = text[1:]
        if len(digits) in (3, 4):
            digits = "".join(c * 2 for c in digits)
        if len(digits) not in (6, 8) or not re.fullmatch(r"[0-9a-f]+", digits):
            raise ColorError(f"cannot parse hex color {value!r}")
        r, g, b = (int(digits[i:i + 2], 16) for i in (0, 2, 4))
        a = int(digits[6:8], 16) / 255 if len(digits) == 8 else 1.0
        return float(r), float(g), float(b), a

    match = re.fullmatch(r"(rgba?|hsla?)\(([^)]*)\)", text)
    if not match:
        raise ColorError(f"cannot parse color {value!r}")
    kind, body = match.group(1), match.group(2)
    parts = [p.strip() for p in re.split(r"[,\s/]+", body) if p.strip()]
    if len(parts) < 3:
        raise ColorError(f"cannot parse color {value!r}")

    def number(token: str, scale: float) -> float:
        if token.endswith("%"):
            return float(token[:-1]) / 100 * scale
        return float(token)

    alpha = 1.0
    if len(parts) >= 4:
        alpha = number(parts[3], 1.0)
        alpha = max(0.0, min(1.0, alpha))

    if kind.startswith("rgb"):
        rgb = tuple(_clamp(number(p, 255.0)) for p in parts[:3])
    else:
        hue_token = parts[0]
        for unit in ("deg", "grad", "rad", "turn"):
            if hue_token.endswith(unit):
                hue_token = hue_token[: -len(unit)]
                break
        hue = float(hue_token)
        sat = number(parts[1], 1.0) if parts[1].endswith("%") else float(parts[1])
        light = number(parts[2], 1.0) if parts[2].endswith("%") else float(parts[2])
        rgb = _hsl_to_rgb(hue, max(0.0, min(1.0, sat)), max(0.0, min(1.0, light)))
    return rgb[0], rgb[1], rgb[2], alpha


def composite(fg: tuple[float, float, float, float],
              bg: tuple[float, float, float, float]) -> tuple[float, float, float]:
    """Flatten a semi-transparent foreground onto an opaque background."""
    alpha = fg[3]
    return tuple(fg[i] * alpha + bg[i] * (1 - alpha) for i in range(3))


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    """WCAG relative luminance, per the definition in the specification."""
    channels = []
    for value in rgb:
        c = value / 255.0
        channels.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(fg: str, bg: str) -> float:
    bg_rgba = parse_color(bg)
    if bg_rgba[3] < 1.0:
        # A translucent background has no defined ratio on its own. Assume it sits
        # on white, and say so in the caller, rather than silently guessing.
        bg_rgba = (*composite(bg_rgba, (255.0, 255.0, 255.0, 1.0)), 1.0)
    fg_rgb = composite(parse_color(fg), bg_rgba)
    l1, l2 = relative_luminance(fg_rgb), relative_luminance(bg_rgba[:3])
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def to_px(size: str | float | None) -> float | None:
    """Normalize a CSS font size to px. Returns None when unknown."""
    if size is None:
        return None
    if isinstance(size, (int, float)):
        return float(size)
    text = str(size).strip().lower()
    match = re.fullmatch(r"([\d.]+)\s*(px|pt|rem|em)?", text)
    if not match:
        return None
    number = float(match.group(1))
    unit = match.group(2) or "px"
    return {"px": number, "pt": number * 4 / 3, "rem": number * 16, "em": number * 16}[unit]


def is_large_text(size: str | float | None, bold: bool) -> bool:
    """WCAG large text: 18pt (24px), or 14pt (18.66px) when bold."""
    px = to_px(size)
    if px is None:
        return False
    return px >= 18.66 if bold else px >= 24.0


def evaluate(fg: str, bg: str, size=None, bold: bool = False,
             label: str | None = None) -> dict:
    ratio = contrast_ratio(fg, bg)
    large = is_large_text(size, bold)
    aa_text = 3.0 if large else 4.5
    aaa_text = 4.5 if large else 7.0
    return {
        "label": label,
        "foreground": fg,
        "background": bg,
        "size": size,
        "bold": bold,
        "large_text": large,
        "ratio": round(ratio, 2),
        "sc_1_4_3_aa_text": {"required": aa_text, "passes": ratio >= aa_text},
        "sc_1_4_6_aaa_text": {"required": aaa_text, "passes": ratio >= aaa_text},
        "sc_1_4_11_aa_non_text": {"required": 3.0, "passes": ratio >= 3.0},
    }


def format_row(result: dict) -> str:
    mark = "PASS" if result["sc_1_4_3_aa_text"]["passes"] else "FAIL"
    kind = "large text" if result["large_text"] else "normal text"
    name = f"{result['label']}: " if result.get("label") else ""
    lines = [
        f"{name}{result['foreground']} on {result['background']}",
        f"  ratio           {result['ratio']}:1  ({kind})",
        f"  1.4.3  AA  text     {mark} (needs {result['sc_1_4_3_aa_text']['required']}:1)",
        "  1.4.6  AAA text     "
        + ("PASS" if result["sc_1_4_6_aaa_text"]["passes"] else "FAIL")
        + f" (needs {result['sc_1_4_6_aaa_text']['required']}:1)",
        "  1.4.11 AA  non-text "
        + ("PASS" if result["sc_1_4_11_aa_non_text"]["passes"] else "FAIL")
        + " (needs 3.0:1)",
    ]
    if result["size"] is None:
        lines.append("  note: no font size given, treated as normal text. "
                     "Pass --size to check the large-text threshold.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="WCAG 2.2 contrast ratios for SC 1.4.3, 1.4.6 and 1.4.11.")
    parser.add_argument("foreground", nargs="?", help="foreground color")
    parser.add_argument("background", nargs="?", help="background color")
    parser.add_argument("--size", help="font size, e.g. 14pt, 24px, 1.5rem")
    parser.add_argument("--bold", action="store_true", help="text is bold (600+)")
    parser.add_argument("--batch", help="JSON file of {fg,bg,label,size,bold} objects")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit JSON instead of text")
    parser.add_argument("--level", choices=["AA", "AAA", "non-text"], default="AA",
                        help="which requirement decides the exit status")
    args = parser.parse_args(argv)

    pairs = []
    if args.batch:
        with open(args.batch, encoding="utf-8") as handle:
            for entry in json.load(handle):
                pairs.append((entry["fg"], entry["bg"], entry.get("size"),
                              bool(entry.get("bold")), entry.get("label")))
    elif args.foreground and args.background:
        pairs.append((args.foreground, args.background, args.size, args.bold, None))
    else:
        parser.error("give a foreground and background, or --batch FILE")

    results, failures = [], 0
    key = {"AA": "sc_1_4_3_aa_text", "AAA": "sc_1_4_6_aaa_text",
           "non-text": "sc_1_4_11_aa_non_text"}[args.level]
    for fg, bg, size, bold, label in pairs:
        try:
            result = evaluate(fg, bg, size, bold, label)
        except ColorError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        results.append(result)
        if not result[key]["passes"]:
            failures += 1

    if args.as_json:
        print(json.dumps({"level_checked": args.level, "failures": failures,
                          "results": results}, indent=2))
    else:
        print("\n\n".join(format_row(r) for r in results))
        if len(results) > 1:
            print(f"\n{failures} of {len(results)} pairs fail at {args.level}.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
