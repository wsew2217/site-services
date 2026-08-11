Site Services · Full suite offline mirror
Built: 2026-08-11

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
