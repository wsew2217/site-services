#!/usr/bin/env python3
"""Build a static offline mirror of the Site Services documentation suite.

Outputs:
  assets/offline-site/index.html          Offline hub (how to run locally + page list)
  assets/offline-site/README.txt          Short local-server instructions
  assets/site-services-full-offline.zip   Full suite for localhost (absolute /assets paths)

Usage:
  python3 scripts/build-offline-site.py
"""

from __future__ import annotations

import shutil
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "offline-site"
ZIP_PATH = ROOT / "assets" / "site-services-full-offline.zip"
STAGING_NAME = "offline-site"

# Suite HTML pages to mirror (paths relative to repo root).
PAGES: list[tuple[str, str]] = [
    ("how-to/index.html", "How to use this site"),
    ("index.html", "Home"),
    ("structure/index.html", "Structure & Methodology"),
    ("coverage/index.html", "Coverage"),
    ("coverage-deal-a/index.html", "Campus Coverage Map (Deal A)"),
    ("cost-model/index.html", "Cost Model (Generic)"),
    ("cost-model-deal-a/index.html", "Cost Model (Deal A)"),
    ("cost-model-deal-b/index.html", "Cost Model (Deal B)"),
    ("vc-kit/index.html", "VC Kit Overview"),
    ("vc-kit/template/index.html", "Template Pack"),
    ("vc-kit/mapper/index.html", "Mapper & Rules"),
    ("vc-kit/agent/index.html", "SalesChat Agent Pack"),
    ("vc-kit/runbook/index.html", "Pilot Runbook"),
    ("vc-kit/chat/index.html", "Kit Chat"),
    ("sandbox/index.html", "Deal Sandbox"),
    ("sandbox/map/index.html", "Deal Map"),
    ("methodology/index.html", "Deal A Methodology"),
    ("summary/index.html", "Executive Summary"),
    ("changes/index.html", "What Changed"),
    ("story/index.html", "Build Story"),
    ("how-we-built/index.html", "How We Built"),
    ("deal-b/index.html", "Tech Bar Pattern (Deal B)"),
    ("deck/index.html", "Customer Deck"),
    ("deck-internal/index.html", "Internal Deck"),
    ("workbook/index.html", "Customer Workbook"),
    ("workbook-internal/index.html", "Internal Workbook"),
]

# Asset trees / files copied under staging/assets/ (keep absolute /assets/... paths).
ASSET_COPY: list[str] = [
    "site.css",
    "site.js",
    "capability-atlas.json",
    "engine-summary.json",
    "engine-summary-deal-a.json",
    "engine-demo.json",
    "deal-b-tech-bar-summary.json",
    "maps",
    "sandbox",
    "vc-kit",
]

# Never ship these inside the full offline zip (self-inclusion / optional noise).
ZIP_ASSET_SKIP_NAMES = {
    "site-services-full-offline.zip",
}


def copy_assets(staging_assets: Path) -> None:
    src_assets = ROOT / "assets"
    staging_assets.mkdir(parents=True, exist_ok=True)
    for name in ASSET_COPY:
        src = src_assets / name
        dst = staging_assets / name
        if not src.exists():
            raise SystemExit(f"Missing asset: {src}")
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(
                src,
                dst,
                ignore=shutil.ignore_patterns(
                    ".DS_Store",
                    *ZIP_ASSET_SKIP_NAMES,
                    "offline-site",  # hub written separately into staging
                ),
            )
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def copy_pages(staging: Path) -> list[tuple[str, str]]:
    included: list[tuple[str, str]] = []
    for rel, title in PAGES:
        src = ROOT / rel
        if not src.exists():
            print(f"skip missing page: {rel}")
            continue
        dst = staging / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        # URL path for hub links (cleanUrls style).
        url = "/" if rel == "index.html" else "/" + rel.replace("/index.html", "").rstrip("/")
        included.append((url, title))
    return included


def write_readme(path: Path) -> None:
    path.write_text(
        f"""Site Services · Full suite offline mirror
Built: {date.today().isoformat()}

HOW TO OPEN LOCALLY (recommended)
---------------------------------
Keep absolute /assets/... paths working:

  cd offline-site
  python3 -m http.server 8765

Then open:
  http://localhost:8765/                 Home
  http://localhost:8765/how-to/          How to use this site
  http://localhost:8765/assets/offline-site/   This offline hub

Do not open HTML via file:// — fetch() for JSON/maps and /assets links need a local server.

CONTENTS
--------
Suite HTML pages (home, how-to, structure, coverage, cost models, vc-kit, sandbox, methodology, summary, decks, workbooks, …)
plus assets (site.css, site.js, maps, capability atlas, engine summaries, sandbox JS, vc-kit downloads).

Generic samples only — no customer PII / address-request pilots.

KIT-ONLY ZIP (secondary)
------------------------
For mapper docs alone (not the full suite), use assets/vc-kit/site-services-offline.zip on the live site.
""",
        encoding="utf-8",
    )


def write_hub(path: Path, pages: list[tuple[str, str]]) -> None:
    rows = "\n".join(
        f'      <tr><td><a href="{url}">{title}</a></td><td><code>{url}</code></td></tr>'
        for url, title in pages
    )
    path.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Site Services · Full site offline hub</title>
<link rel="stylesheet" href="/assets/site.css">
<style>
.offline-hero {{
  background: #13294B;
  color: #fff;
  border-radius: 16px;
  padding: 28px 26px 22px;
  margin-bottom: 22px;
}}
.offline-hero .k {{ color: #D86A44; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; font-size: 11px; }}
.offline-hero h1 {{ font-family: Cambria, Georgia, serif; font-size: 28px; margin: 8px 0 6px; }}
.offline-hero .s {{ color: #C9D2E4; font-size: 14px; margin: 0; }}
.start-card {{
  border: 2px solid #2fd6c2;
  box-shadow: 0 0 0 2px rgba(47,214,194,.16);
  border-radius: 12px;
  padding: 16px 18px;
  margin: 0 0 20px;
  background: #fff;
}}
.start-card a.primary {{
  display: inline-block;
  margin-top: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #13294B;
  color: #fff !important;
  text-decoration: none;
  font-weight: 700;
}}
pre.run {{
  background: #F4F6FB;
  border: 1px solid var(--doc-line, #E4E8F0);
  border-radius: 10px;
  padding: 12px 14px;
  overflow-x: auto;
  font-size: 13px;
}}
table.page-list {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
table.page-list th {{ text-align: left; background: #13294B; color: #fff; padding: 8px 10px; }}
table.page-list td {{ border: 1px solid var(--doc-line, #E4E8F0); padding: 8px 10px; }}
.wrap {{ max-width: 920px; margin: 0 auto; padding: 28px 20px 64px; }}
</style>
</head>
<body class="suite-app suite-doc" data-page="offline-hub" data-mode="shell">
<div data-suite-content>
  <div class="suite-doc-frame">
<div class="page wrap">
  <div class="offline-hero">
    <div class="k">Offline · Full documentation suite</div>
    <h1>Site Services offline hub</h1>
    <p class="s">Static mirror for local use. Serve with a tiny HTTP server so <code>/assets/…</code> paths keep working. Generic samples only — no customer PII.</p>
  </div>

  <div class="start-card" role="note">
    <b>Start here: How to use this site</b>
    <p style="margin:8px 0 0">Tooltips (?), sidebar navigation, recommended path (kit → sandbox → cost model), and what each area is for.</p>
    <a class="primary" href="/how-to/">Open How to use this site →</a>
  </div>

  <h2>How to run locally</h2>
  <p>Unzip <code>site-services-full-offline.zip</code>, then:</p>
  <pre class="run">cd offline-site
python3 -m http.server 8765</pre>
  <p>Open <a href="http://localhost:8765/"><code>http://localhost:8765/</code></a> (home) or <a href="http://localhost:8765/how-to/"><code>/how-to/</code></a>.</p>
  <p class="mute">Avoid <code>file://</code> — JSON fetches and absolute asset paths need localhost.</p>

  <h2>Downloads on the live site</h2>
  <ul>
    <li><a href="/assets/site-services-full-offline.zip" download><b>Full site offline (.zip)</b></a> — this package</li>
    <li><a href="/assets/vc-kit/site-services-offline.zip" download>VC kit only (.zip)</a> — mapper docs / kit hub (secondary)</li>
  </ul>

  <h2>Included pages</h2>
  <table class="page-list">
    <thead><tr><th>Page</th><th>Path</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>

  <p class="mute" style="margin-top:24px">Built {date.today().isoformat()} · Field Services Solution Design</p>
</div>
  </div>
</div>
<script src="/assets/site.js"></script>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_zip(staging: Path) -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging.rglob("*")):
            if path.is_dir():
                continue
            if path.name in ZIP_ASSET_SKIP_NAMES:
                continue
            arc = Path(STAGING_NAME) / path.relative_to(staging)
            zf.write(path, arcname=str(arc))


def main() -> None:
    staging = ROOT / ".offline-build"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    pages = copy_pages(staging)
    if not any(u == "/how-to" for u, _ in pages):
        raise SystemExit("how-to page missing — create how-to/index.html before packaging")

    # Put how-to first in the hub list for prominence.
    pages.sort(key=lambda item: (0 if item[0] == "/how-to" else 1 if item[0] == "/" else 2, item[1]))

    copy_assets(staging / "assets")
    write_readme(staging / "README.txt")

    hub_dir = staging / "assets" / "offline-site"
    hub_dir.mkdir(parents=True, exist_ok=True)
    write_hub(hub_dir / "index.html", pages)
    write_readme(hub_dir / "README.txt")

    # Publish hub + README to the live assets tree (not the full HTML duplicate).
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(hub_dir / "index.html", OUT_DIR / "index.html")
    shutil.copy2(hub_dir / "README.txt", OUT_DIR / "README.txt")

    write_zip(staging)
    shutil.rmtree(staging)

    size_kb = ZIP_PATH.stat().st_size / 1024
    print(f"hub  → {OUT_DIR / 'index.html'}")
    print(f"zip  → {ZIP_PATH} ({size_kb:.0f} KiB)")
    print(f"pages: {len(pages)}")


if __name__ == "__main__":
    main()
