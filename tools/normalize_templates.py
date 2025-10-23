#!/usr/bin/env python3
"""
Normalize generated Django templates.
- Replace `{% static 'static/...'%}` -> `{% static '...'%}`
- Normalize `{% include 'path' %}` paths (resolve ../ and ./) using POSIX paths

Backs up original files with a `.bak` suffix before changing.

Usage:
  python tools/normalize_templates.py templates
"""
from pathlib import Path, PurePosixPath
import re
import sys

STATIC_DUP_RE = re.compile(r"\{%\s*static\s+['\"]static/([^'\"]+)['\"]\s*%\}")
INCLUDE_RE = re.compile(r"\{%\s*include\s+['\"]([^'\"]+)['\"](\s+with[^%}]*)?%\}")


def normalize_include_path(p: str) -> str:
    # Use PurePosixPath to normalize and keep forward slashes
    pp = PurePosixPath(p)
    # Collapse known leading './'
    norm = pp
    # Remove any leading '/' to keep template-relative
    parts = list(norm.parts)
    # Reconstruct without root
    norm = PurePosixPath(*parts)
    return str(norm)


def process_file(path: Path):
    text = path.read_text(encoding='utf8')
    orig = text
    # Replace static 'static/...' -> '...'
    text, n_static = STATIC_DUP_RE.subn(r"{% static '\1' %}", text)

    # Normalize include paths
    def inc_repl(m):
        p = m.group(1)
        rest = m.group(2) or ''
        newp = normalize_include_path(p)
        return "{% include '" + newp + "'" + rest + "%}"
    text, n_inc = INCLUDE_RE.subn(inc_repl, text)

    if text != orig:
        bak = path.with_suffix(path.suffix + '.bak')
        if not bak.exists():
            path.rename(bak)
            bak.write_text(orig, encoding='utf8')
        # write modified content
        path.write_text(text, encoding='utf8')
    return n_static, n_inc


def main():
    if len(sys.argv) < 2:
        print('Usage: python tools/normalize_templates.py <templates_root>')
        sys.exit(1)
    root = Path(sys.argv[1])
    if not root.exists():
        print('Templates root not found:', root)
        sys.exit(1)
    total_static = 0
    total_inc = 0
    for p in root.rglob('*.html'):
        n_static, n_inc = process_file(p)
        total_static += n_static
        total_inc += n_inc
    print(f'Processed templates in {root} — static fixes: {total_static}, include fixes: {total_inc}')

if __name__ == '__main__':
    main()
