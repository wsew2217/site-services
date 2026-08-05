#!/usr/bin/env python3
"""Wrap legacy HTML pages into the shared Site Services suite chrome."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_PAGES = {
    "summary": "Deal A v2 Executive Summary",
    "changes": "Deal A v2 Change Summary",
    "story": "How We Built It · Executive Story",
    "methodology": "Virtual Campus Methodology",
    "how-we-built": "How We Built the Staffing Model",
}

TOOL_PAGES = {
    "cost-model": ("Site Services Cost Model", "suite-tool"),
    "deck": ("Virtual Campus Model · Deck (CUSTOMER)", "suite-tool suite-dark-tool"),
    "deck-internal": ("Virtual Campus Model · Deck (INTERNAL)", "suite-tool suite-dark-tool"),
    "workbook": ("Staffing Model Workbook · CUSTOMER", "suite-tool"),
    "workbook-internal": ("Staffing Model Workbook · INTERNAL", "suite-tool"),
}

HEAD_LINKS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
""".strip()


def extract_title(html: str, fallback: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    return m.group(1).strip() if m else fallback


def extract_body(html: str, strip_scripts: bool = False) -> str:
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.I | re.S)
    if not m:
        raise SystemExit("Could not find body")
    body = m.group(1).strip()
    if strip_scripts:
        body = re.sub(r"<script\b.*?</script>", "", body, flags=re.I | re.S).strip()
    return body


def extract_scripts(html: str) -> str:
    return "\n".join(re.findall(r"<script\b.*?</script>", html, flags=re.I | re.S))


def extract_style(html: str) -> str:
    m = re.search(r"<style\b[^>]*>(.*?)</style>", html, re.I | re.S)
    return m.group(1) if m else ""


def wrap_doc(page_id: str, src: Path) -> None:
    html = src.read_text(encoding="utf-8")
    title = extract_title(html, DOC_PAGES[page_id])
    page = re.search(r'(<div class="page">.*?</div>\s*)(?:</body>|$)', html, re.I | re.S)
    if page:
        body = page.group(1).strip()
    else:
        body = extract_body(html, strip_scripts=True)
        body = re.sub(
            r'^<div data-suite-content>\s*<div class="suite-doc-frame">|</div>\s*</div>\s*$',
            "",
            body,
            flags=re.I | re.S,
        ).strip()
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{HEAD_LINKS}
</head>
<body class="suite-app suite-doc" data-page="{page_id}" data-mode="shell">
<div data-suite-content>
  <div class="suite-doc-frame">
{body}
  </div>
</div>
<script src="/assets/site.js"></script>
</body>
</html>
"""
    src.write_text(out, encoding="utf-8")
    print(f"doc  {page_id}")


def wrap_tool(page_id: str, src: Path, body_class: str) -> None:
    html = src.read_text(encoding="utf-8")
    # Already wrapped?
    if 'data-mode="tool"' in html or "data-mode='tool'" in html:
        print(f"skip {page_id} (already tool)")
        return

    title = extract_title(html, TOOL_PAGES[page_id][0])
    style = extract_style(html)
    body = extract_body(html, strip_scripts=True)
    scripts = extract_scripts(html)

    # Scope legacy styles so they don't fight the suite chrome hard.
    scoped = style
    if page_id.startswith("workbook"):
        scoped += "\n.tabs{top:52px}\n"
    if page_id == "cost-model":
        scoped += "\n.toolbar{top:52px}\n"
    if page_id.startswith("deck"):
        scoped += "\n.deck{padding-top:18px}\n"

    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{HEAD_LINKS}
<style>
{scoped}
</style>
</head>
<body class="suite-app {body_class}" data-page="{page_id}" data-mode="tool">
{body}
<script src="/assets/site.js"></script>
{scripts}
</body>
</html>
"""
    src.write_text(out, encoding="utf-8")
    print(f"tool {page_id}")


def main() -> None:
    for page_id in DOC_PAGES:
        wrap_doc(page_id, ROOT / page_id / "index.html")
    for page_id, (_, body_class) in TOOL_PAGES.items():
        wrap_tool(page_id, ROOT / page_id / "index.html", body_class)


if __name__ == "__main__":
    main()
