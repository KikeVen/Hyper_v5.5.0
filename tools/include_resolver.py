#!/usr/bin/env python3
"""Simple include resolver for Gulp-style @@include() directives.

Usage:
  python tools/include_resolver.py --input PATH --output PATH

This script will recursively replace occurrences of:
  @@include('./partials/foo.html')
or
  @@include('./partials/foo.html', {"title":"..."})

with the contents of the referenced file. Context objects are ignored (kept for compatibility).
"""
import argparse
import shutil
import os
import re
import json
import sys

INCLUDE_RE = re.compile(r"@@include\(\s*(['\"])(?P<path>.+?)\1(?:\s*,\s*(?P<context>\{.*?\}))?\s*\)")

def resolve_includes(path, seen=None):
    if seen is None:
        seen = set()
    abspath = os.path.abspath(path)
    if abspath in seen:
        raise RuntimeError(f"Circular include detected: {abspath}")
    seen.add(abspath)

    try:
        with open(abspath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception:
        raise

    # Special-case: if this file is a small wrapper that begins by including
    # pages-starter.html (the canonical starter), then treat the remainder of
    # this file as "page content" and merge it into the starter container so
    # pages don't end up duplicated after </html>.
    # Detect if the file starts by including the canonical starter file. If so
    # we'll merge the remainder into the starter instead of appending it after
    # </html>. This handles the common pattern of pages that `@@include` the
    # starter and then provide the page-specific markup.
    starter_include_match = re.match(r"\s*@@include\(\s*(['\"])(?P<inc>.+pages-starter\.html)\1(?:\s*,.*)?\)\s*\n?",
                                      text, flags=re.IGNORECASE)
    if starter_include_match:
        m = starter_include_match
        starter_inc = m.group('inc')
        # resolve the starter include path relative to this file
        if not os.path.isabs(starter_inc):
            starter_abspath = os.path.normpath(os.path.join(os.path.dirname(abspath), starter_inc))
        else:
            starter_abspath = starter_inc

        if os.path.exists(starter_abspath):
            # resolve the starter (and its own includes) first
            starter_content = resolve_includes(starter_abspath, seen=seen.copy())

            # remainder after removing the initial include line entirely
            remainder = text[m.end():]

            # resolve any includes inside the remainder relative to the input file
            remainder_resolved = resolve_text(remainder, os.path.dirname(abspath), seen=seen.copy())

            # If the starter already contains a page-title block, try to avoid
            # inserting a duplicate page-title carried by the remainder. Look
            # for a common page-title snippet in the remainder and remove it.
            if "<h4 class=\"page-title\">" in starter_content:
                # crude but effective removal: remove the first occurrence of
                # the page-title block (breadcrumb + h4) from remainder_resolved
                page_title_pattern = re.compile(r"<!-- start page title -->.*?<!-- end page title -->", re.DOTALL)
                remainder_resolved = page_title_pattern.sub('', remainder_resolved, count=1)

            # Try to inject the remainder into a sensible container inside the
            # starter. Prefer an explicit container comment, then </body>, then
            # append at the end.
            insert_candidates = ["</div> <!-- container -->", "</div><!-- container -->", "</div> <!--container-->", "</div> <!-- container -->\n"]
            final = None
            for insert_before in insert_candidates:
                if insert_before in starter_content:
                    final = starter_content.replace(insert_before, remainder_resolved + "\n" + insert_before, 1)
                    break

            if final is None:
                if "</body>" in starter_content:
                    final = starter_content.replace("</body>", remainder_resolved + "\n</body>", 1)
                else:
                    final = starter_content + "\n" + remainder_resolved

            return final

    def _repl(match):
        inc_path = match.group('path')
        context_str = match.group('context')
        # resolve relative to the current file
        if not os.path.isabs(inc_path):
            inc_abspath = os.path.normpath(os.path.join(os.path.dirname(abspath), inc_path))
        else:
            inc_abspath = inc_path

        if not os.path.exists(inc_abspath):
            print(f"Warning: included file not found: {inc_abspath}", file=sys.stderr)
            return f"<!-- include not found: {inc_path} -->"

        # Recurse into the included file
        included = resolve_includes(inc_abspath, seen=seen.copy())

        # If the include had a JSON-like context object, try to parse it and
        # substitute simple @@key tokens inside the included content. This is
        # intentionally minimal (no expression language) and exists to support
        # common patterns like passing a title to a partial.
        if context_str:
            try:
                ctx = json.loads(context_str)
                if isinstance(ctx, dict):
                    for k, v in ctx.items():
                        token = f"@@{k}"
                        included = included.replace(token, str(v))
            except Exception:
                # ignore parse errors and keep original included content
                pass

        return included

    result = INCLUDE_RE.sub(_repl, text)
    return result

def resolve_text(text, base_dir, seen=None):
    """Resolve includes found inside a text blob. Relative paths are resolved
    against base_dir."""
    if seen is None:
        seen = set()

    def _repl(match):
        inc_path = match.group('path')
        context_str = match.group('context')
        if not os.path.isabs(inc_path):
            inc_abspath = os.path.normpath(os.path.join(base_dir, inc_path))
        else:
            inc_abspath = inc_path

        if not os.path.exists(inc_abspath):
            print(f"Warning: included file not found: {inc_abspath}", file=sys.stderr)
            return f"<!-- include not found: {inc_path} -->"

        included = resolve_includes(inc_abspath, seen=seen.copy())
        if context_str:
            try:
                ctx = json.loads(context_str)
                if isinstance(ctx, dict):
                    for k, v in ctx.items():
                        token = f"@@{k}"
                        included = included.replace(token, str(v))
            except Exception:
                pass
        return included

    return INCLUDE_RE.sub(_repl, text)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', required=True)
    p.add_argument('--output', '-o', required=True)
    p.add_argument('--asset-prefix', help="Optional prefix to rewrite asset paths (e.g. ../src/assets/)")
    p.add_argument('--copy-assets', action='store_true', help='Copy the source assets directory into the output directory as assets/')
    p.add_argument('--validate', action='store_true', help='Validate output: check single <html>/<head>/<body> and that referenced assets exist')
    args = p.parse_args()

    src = args.input
    out = args.output
    content = resolve_includes(src)

    # If the caller didn't supply an explicit --asset-prefix, and the output
    # is inside Admin/dist while the source assets live under Admin/src/assets,
    # compute a sensible relative prefix so the flattened file can reference
    # the original assets folder for local preview.
    asset_prefix = args.asset_prefix
    if not asset_prefix:
        try:
            # candidate assets folder relative to the source file
            src_assets = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(src)), 'assets'))
            out_dir = os.path.dirname(os.path.abspath(out))
            if os.path.exists(src_assets):
                # compute relative path from output dir to the assets dir
                rel = os.path.relpath(src_assets, out_dir)
                # ensure trailing slash
                asset_prefix = rel.replace('\\', '/') + '/'
        except Exception:
            asset_prefix = None

    # If requested, copy the source assets into the output directory so the
    # flattened file can be served directly from the output dir. This will
    # also set the asset_prefix to 'assets/'.
    if args.copy_assets:
        try:
            src_assets = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(src)), 'assets'))
            out_dir = os.path.dirname(os.path.abspath(out))
            dest_assets = os.path.join(out_dir, 'assets')
            if os.path.exists(src_assets):
                if os.path.exists(dest_assets):
                    shutil.rmtree(dest_assets)
                shutil.copytree(src_assets, dest_assets)
                asset_prefix = 'assets/'
        except Exception as e:
            print(f"Warning: failed to copy assets: {e}", file=sys.stderr)

    if asset_prefix:
        # Replace occurrences like href="assets/..." or src='assets/...' -> use the computed prefix
        # Also handle url(assets/...) in inline styles.
        # Use several simple regex replacements rather than attempting full HTML parsing.
        content = re.sub(r"(?P<attr>(?:href|src)\s*=\s*[\"'])(assets/)", r"\g<attr>" + asset_prefix, content)
        content = re.sub(r"url\(\s*(['\"]?)(assets/)", lambda m: f"url({m.group(1)}{asset_prefix}", content)

    # Final cleanup: strip any leftover @@tokens (e.g. @@title) to avoid
    # leaving template artifacts in the flattened output. We warn about what
    # we removed so authors can fix missing contexts if needed.
    leftover_tokens = re.findall(r"@@[A-Za-z0-9_-]+", content)
    if leftover_tokens:
        unique = sorted(set(leftover_tokens))
        print(f"Warning: removed {len(unique)} unresolved @@ tokens: {', '.join(unique[:10])}{'...' if len(unique)>10 else ''}", file=sys.stderr)
        content = re.sub(r"@@[A-Za-z0-9_-]+", "", content)

    # Validation: optionally verify that the flattened output looks sane and
    # that referenced assets exist. This is intentionally conservative and
    # only runs when the user requested --validate.
    if args.validate:
        errors = []

        def _count_tag(tag):
            return len(re.findall(fr"<\s*{tag}\b", content, flags=re.IGNORECASE))

        html_open = _count_tag('html')
        html_close = len(re.findall(r"</\s*html\s*>", content, flags=re.IGNORECASE))
        head_open = _count_tag('head')
        head_close = len(re.findall(r"</\s*head\s*>", content, flags=re.IGNORECASE))
        body_open = _count_tag('body')
        body_close = len(re.findall(r"</\s*body\s*>", content, flags=re.IGNORECASE))

        if html_open != 1 or html_close != 1:
            errors.append(f"Expected exactly one <html> and </html> pair, found {html_open} opens and {html_close} closes")
        if head_open != 1 or head_close != 1:
            errors.append(f"Expected exactly one <head> and </head> pair, found {head_open} opens and {head_close} closes")
        if body_open != 1 or body_close != 1:
            errors.append(f"Expected exactly one <body> and </body> pair, found {body_open} opens and {body_close} closes")

        # Check for unresolved include markers inserted by the resolver when a
        # referenced include file was missing.
        if '<!-- include not found:' in content:
            errors.append('One or more includes were not found. Look for "<!-- include not found: ... -->" in the output.')

        # Check referenced local assets (href/src and url(...)) and ensure they
        # exist either relative to the output directory or relative to the
        # source directory. Skip obvious external URLs.
        asset_refs = []
        for m in re.findall(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', content, flags=re.IGNORECASE):
            asset_refs.append(m)
        for m in re.findall(r'url\(\s*(["\']?)([^)"\']+)\1\s*\)', content, flags=re.IGNORECASE):
            asset_refs.append(m[1])

        out_dir = os.path.dirname(os.path.abspath(out))
        src_dir = os.path.dirname(os.path.abspath(src))

        # Attempt to locate the Admin/src root folder to resolve project-root
        # relative links. Walk up until a directory named 'Admin' is found.
        admin_src_root = None
        probe = os.path.dirname(os.path.abspath(src))
        while True:
            parent = os.path.dirname(probe)
            if parent == probe:
                break
            if os.path.basename(parent).lower() == 'admin':
                admin_src_root = os.path.normpath(os.path.join(parent, 'src'))
                break
            probe = parent

        missing_assets = []
        for ref in set(asset_refs):
            ref_clean = ref.split('?', 1)[0].split('#', 1)[0]
            if not ref_clean or ref_clean.lower().startswith(('http://', 'https://', '//', 'javascript:', 'data:', 'mailto:', 'tel:')):
                continue
            if ref_clean.startswith('#'):
                continue
            # Skip internal page links (html files); validation focuses on
            # assets like css/js/images. HTML links are not considered missing
            # assets here.
            if ref_clean.lower().endswith('.html'):
                continue

            # Try resolving relative to the output directory first
            candidate = os.path.normpath(os.path.join(out_dir, ref_clean))
            if os.path.exists(candidate):
                continue

            # Then try resolving relative to the source directory
            candidate2 = os.path.normpath(os.path.join(src_dir, ref_clean))
            if os.path.exists(candidate2):
                continue

            # As a last attempt, if asset_prefix was provided and ref starts
            # with the asset_prefix, try mapping it back into the source dir.
            if asset_prefix and ref_clean.startswith(asset_prefix):
                suffix = ref_clean[len(asset_prefix):]
                candidate3 = os.path.normpath(os.path.join(src_dir, suffix))
                if os.path.exists(candidate3):
                    continue

            # If we found an Admin/src root, try resolving relative to it.
            if admin_src_root:
                candidate4 = os.path.normpath(os.path.join(admin_src_root, ref_clean))
                if os.path.exists(candidate4):
                    continue

            missing_assets.append(ref_clean)

        if missing_assets:
            errors.append(f"Missing asset files referenced in output (checked relative to output and source dirs): {', '.join(sorted(missing_assets)[:10])}{'...' if len(missing_assets)>10 else ''}")

        if errors:
            print('\nValidation errors:', file=sys.stderr)
            for e in errors:
                print(' - ' + e, file=sys.stderr)
            print('\nHint: run without --validate to skip these checks, or run with --copy-assets to copy referenced assets into the output folder.', file=sys.stderr)
            sys.exit(2)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Wrote flattened HTML to {out}")


if __name__ == '__main__':
    main()
