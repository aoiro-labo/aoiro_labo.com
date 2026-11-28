#!/usr/bin/env python3
"""Bake BudouX phrase segmentation (ZWSP) into built HTML files.

Usage: python3 tools/budoux_postprocess.py [output_dir]   (default: public)

Runs after `hugo`. For each .html file, the first <h1> and the
<article class="... prose ..."> body are passed through BudouX, which
inserts zero-width spaces at Japanese phrase boundaries. Everything
outside those fragments is left byte-identical (doctype, scripts and
head metadata are never re-serialized). Requires the `budoux` package
(pip install budoux). Fail-open: any error leaves the build untouched
and exits 0, so a broken run never blocks a deploy.
"""
import re
import sys

ZWSP = "\u200b"

# html.parser lowercases attribute names; SVG has case-sensitive ones.
SVG_ATTR_RESTORE = {
    "viewbox": "viewBox",
    "preserveaspectratio": "preserveAspectRatio",
    "gradientunits": "gradientUnits",
    "patternunits": "patternUnits",
    "clippathunits": "clipPathUnits",
    "refx": "refX",
    "refy": "refY",
    "markerwidth": "markerWidth",
    "markerheight": "markerHeight",
    "basefrequency": "baseFrequency",
    "pathlength": "pathLength",
}


def restore_svg_attrs(fragment: str) -> str:
    parts = re.split(r"(<[^>]+>)", fragment)
    for i, part in enumerate(parts):
        if part.startswith("<"):
            for low, camel in SVG_ATTR_RESTORE.items():
                part = part.replace(f" {low}=", f" {camel}=")
            parts[i] = part
    return "".join(parts)


def process_file(path, parser) -> bool:
    src = path.read_text(encoding="utf-8")
    if ZWSP in src:
        return False
    out = src

    m = re.search(r"<article[^>]*class=\"[^\"]*prose[^\"]*\"[^>]*>.*?</article>", out, re.S)
    if m:
        frag = parser.translate_html_string(m.group(0), wrap=False)
        out = out[: m.start()] + restore_svg_attrs(frag) + out[m.end():]

    m = re.search(r"<h1[^>]*>.*?</h1>", out, re.S)
    if m and ZWSP not in m.group(0):
        frag = parser.translate_html_string(m.group(0), wrap=False)
        out = out[: m.start()] + restore_svg_attrs(frag) + out[m.end():]

    if out != src:
        path.write_text(out, encoding="utf-8")
        return True
    return False


def main() -> int:
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "public"
    try:
        import budoux
        from pathlib import Path

        parser = budoux.load_default_japanese_parser()
        files = list(Path(out_dir).rglob("*.html"))
        changed = 0
        for f in files:
            try:
                if process_file(f, parser):
                    changed += 1
            except Exception as e:  # per-file: keep going
                print(f"budoux: skip {f}: {e}", file=sys.stderr)
        print(f"budoux: baked segmentation into {changed}/{len(files)} html files")
    except Exception as e:
        print(f"budoux: disabled ({e})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
