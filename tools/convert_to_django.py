#!/usr/bin/env python3
"""
Convert @@include() directives and asset paths to Django template syntax.

Usage:
  python tools/convert_to_django.py --out templates Admin/src Stater-Kit/src
"""
import argparse
import json
import os
import re
from pathlib import Path
from typing import Optional

INCLUDE_RE = re.compile(
    r"@@include\(\s*(['\"])(?P<path>.+?)\1(?:\s*,\s*(?P<context>\{.*?\}))?\s*\)"
)
ASSET_RE = re.compile(r"""(?P<prefix>(?:src|href)\s*=\s*["'])(?P<path>assets/[^"']+)["']""")
DOCTYPE_RE = re.compile(r"^\s*<!doctype html>", re.IGNORECASE | re.MULTILINE)
LOAD_STATIC = "{% load static %}"

def convert_include(match: re.Match, base_dir: Path) -> str:
    inc_path = match.group("path")
    ctx = match.group("context")
    # map './partials/foo.html' -> 'partials/foo.html'
    if inc_path.startswith("./"):
        inc_path = inc_path[2:]
    inc_path = inc_path.replace("\\", "/")
    # only keep path relative to partials/templates root
    # ensure leading path doesn't start with '/'
    inc_path = inc_path.lstrip("/")
    # If include is not from partials, place it under includes/ to keep templates organized
    # Assumption: non-partial includes should be referenced as 'includes/<name>.html'
    first_segment = inc_path.split('/', 1)[0]
    if first_segment != 'partials' and not inc_path.startswith('includes/'):
        inc_path = f"includes/{inc_path}"

    include_tag = f"{{% include '{inc_path}'"
    if ctx:
        try:
            ctx_obj = json.loads(ctx)
            if isinstance(ctx_obj, dict) and ctx_obj:
                parts = []
                for k, v in ctx_obj.items():
                    if isinstance(v, str):
                        val = v.replace("'", "\\'")
                        parts.append(f"{k}='{val}'")
                    elif isinstance(v, bool):
                        parts.append(f"{k}={str(v).lower()}")
                    else:
                        parts.append(f"{k}={json.dumps(v)}")
                include_tag += " with " + " ".join(parts)
        except Exception:
            # if parsing fails, ignore context and keep simple include
            pass
    include_tag += " %}"
    return include_tag

def convert_assets(text: str) -> str:
    def _repl(m: re.Match) -> str:
        prefix = m.group("prefix")
        path = m.group("path")
        # rename assets/... -> static/... in the generated static tag
        static_path = path.replace('assets/', 'static/', 1)
        return f"{prefix}{{% static '{static_path}' %}}\""
    return ASSET_RE.sub(_repl, text)

def ensure_load_static(text: str) -> str:
    # Only add the {% load static %} tag when the template actually uses the {% static %} tag
    if LOAD_STATIC in text:
        return text
    if "{% static" not in text:
        return text
    # Insert after DOCTYPE if present, otherwise at start
    m = DOCTYPE_RE.search(text)
    if m:
        insert_at = m.end()
        # put load static on next line
        return text[:insert_at] + "\n" + LOAD_STATIC + "\n" + text[insert_at:]
    else:
        return LOAD_STATIC + "\n" + text

def convert_file(src_path: Path, dst_path: Path, base_dir: Path):
    text = src_path.read_text(encoding="utf8")
    # convert includes
    def repl_inc(m):
        return convert_include(m, base_dir)
    text = INCLUDE_RE.sub(repl_inc, text)
    # convert assets
    text = convert_assets(text)
    # ensure load static is present
    text = ensure_load_static(text)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(text, encoding="utf8")

def should_process_file(p: Path) -> bool:
    return p.suffix.lower() in (".html", ".htm")

def main():
    parser = argparse.ArgumentParser(description="Convert Hyper @@include to Django includes and static tags.")
    parser.add_argument("src_dirs", nargs="+", help="Source directories (e.g. Admin/src)")
    parser.add_argument("--out", required=True, help="Output templates root (e.g. templates)")
    args = parser.parse_args()

    out_root = Path(args.out)
    for src in args.src_dirs:
        src_root = Path(src)
        if not src_root.exists():
            print(f"skipping missing source: {src_root}")
            continue
        for p in src_root.rglob("*.html"):
            rel = p.relative_to(src_root)
            dst = out_root / rel
            convert_file(p, dst, src_root)
        # also copy partials directory if present (already converted above)
        partials = src_root / "partials"
        if partials.exists():
            for p in partials.rglob("*.html"):
                rel = p.relative_to(src_root)
                dst = out_root / rel
                convert_file(p, dst, src_root)

if __name__ == "__main__":
    main()