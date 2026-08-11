/**
 * Proposal export pack — offline HTML + PPT outline + Cost_Model_Load CSV + engine JSON.
 * Uses JSZip when available; otherwise multi-download fallback.
 */
(() => {
  function stamp() {
    return new Date().toISOString().slice(0, 19).replace(/[:T]/g, (c) => (c === "T" ? "_" : "-"));
  }

  function sanitizeLabel(label) {
    if (window.SSSandbox?.sanitizeDealLabel) return window.SSSandbox.sanitizeDealLabel(label);
    return String(label || "Sample")
      .replace(/[<>:"/\\|?*\x00-\x1f]/g, "")
      .trim()
      .slice(0, 48) || "Sample";
  }

  function packBasename(dealLabel) {
    return `Site_Services_Proposal_Pack_${sanitizeLabel(dealLabel).replace(/\s+/g, "_")}_${stamp()}`;
  }

  function downloadBlob(blob, filename) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }

  function pptOutline(pack) {
    const s = pack.summary || {};
    const role = s.role_split || {};
    const sites = pack.sites || [];
    const label = pack.dealLabel || "Sample";
    return `# Site Services proposal outline — ${label}

Generic solutioning narrative. No customer PII unless typed in the deal label field.

## Slide 1 — Title
- Site Services · Virtual campus solutioning
- Deal label: ${label}
- Generated: ${pack.createdAt || new Date().toISOString()}
- Source: browser sandbox (catchment bridge) — not a full engine commercial quote

## Slide 2 — Estate snapshot
- Sites: ${s.sites ?? sites.length}
- Users / seats: ${s.users ?? "—"}
- Tickets / yr: ${s.tickets_yr ?? "—"}
- Tickets per user: ${s.tpu ?? "—"}
- Virtual campuses: ${s.campuses ?? "—"}
- Day-one field techs (hint): ${s.day1_techs ?? "—"}

## Slide 3 — Catchment rules (v1)
- Local range: ≤25 mi OR ≤60 min drive proxy @ 40 mph
- Near a Staffed campus → always Local
- Remote only if far AND tickets/day < 1.2
- Far AND ≥1.2 tpd → Staffed campus

## Slide 4 — Role split
- Staffed: ${role.Staffed ?? 0}
- Local: ${role.Local ?? 0}
- Remote: ${role.Remote ?? 0}

## Slide 5 — Site map story
- Show Staffed (hub) / Local / Remote pins
- Call out any far high-volume promotions and no-coord exceptions
- Fallback: table if coordinates missing

## Slide 6 — Scenario ladder
- Day one (demand + floors) vs 750:1 / 1000:1 / 1500:1 ratio guardrails
- Ratios do not invent campus count
- Prefer loading summary into /cost-model for priced scenarios

## Slide 7 — Delivery design KPIs
- FTFR design floor ≥85%
- Avoidable dispatch industry median ~14%
- Utilization band 75–85% (design 85%)
- Failed first visit → resolution cost +34–44%

## Slide 8 — Tech-bar / remote overlay hint
- Walk-in bars + virtual tech are overlays on the same FMO ladder (Deal B pattern)
- Do not confuse with Deal A campus estate defaults

## Slide 9 — What is / is not in this pack
- Included: mapped roles, Cost_Model_Load CSV, bridge JSON, offline HTML snapshot
- Gap vs \`python -m engine run\`: full demand/dispatch/cost cash ladder, OEM/shipment unit economics, workbook workbook sheets
- Next step: bridge Sites → optional engine run → upload Deal_Output.json on /cost-model

## Slide 10 — Ask / next steps
- Confirm geocode quality and Exceptions
- Refresh labor / logistics rates for the deal
- Decide whether tech-bar / virtual overlays apply
`;
  }

  function offlineHtml(pack) {
    const s = pack.summary || {};
    const role = s.role_split || {};
    const sites = pack.sites || [];
    const label = pack.dealLabel || "Sample";
    const rows = sites
      .map(
        (r) =>
          `<tr><td>${esc(r.site_id)}</td><td>${esc(r.site_name)}</td><td>${esc(r.city)}</td><td>${esc(r.country)}</td><td>${esc(r.mapped_role)}</td><td>${r.tickets_per_day ?? ""}</td><td>${r.users ?? ""}</td><td>${r.latitude ?? ""}</td><td>${r.longitude ?? ""}</td></tr>`
      )
      .join("");
    return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Site Services proposal · ${esc(label)}</title>
<style>
:root{--navy:#13294B;--acc:#D86A44;--tint:#F4F6FB;--line:#E4E8F0;--ink:#232A35;--mute:#8A93A6}
*{box-sizing:border-box}body{margin:0;font-family:Calibri,'Segoe UI',system-ui,sans-serif;color:var(--ink);background:#fff;font-size:14px;line-height:1.45}
.wrap{max-width:960px;margin:0 auto;padding:24px 18px 48px}
.banner{background:#fff6f1;border-left:4px solid var(--acc);padding:10px 12px;border-radius:0 10px 10px 0;margin-bottom:18px;font-size:13px}
h1,h2,h3{font-family:Cambria,Georgia,serif;color:var(--navy)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:14px 0}
.kpi{border:1px solid var(--line);border-radius:10px;padding:12px;background:var(--tint)}
.kpi b{display:block;font-size:22px;font-family:Cambria,Georgia,serif;color:var(--navy)}
.kpi span{font-size:11px;color:var(--mute);text-transform:uppercase;letter-spacing:.04em}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin:10px 0}
th{background:var(--navy);color:#fff;text-align:left;padding:7px 8px}td{border:1px solid var(--line);padding:6px 8px}
.mute{color:var(--mute);font-size:12.5px}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700}
.staffed{background:#e8faf7;color:#149887}.local{background:#eef3ff;color:#3b6ea5}.remote{background:#fff1ec;color:#c45c38}
</style>
</head>
<body>
<div class="wrap">
<div class="banner"><b>Offline proposal snapshot</b> · ${esc(pack.createdAt || "")} · Deal label “${esc(label)}”. Browser catchment bridge — not a full engine commercial quote. No customer deal data shipped on the live suite by default.</div>
<h1>Site Services · ${esc(label)}</h1>
<p class="mute">Staffed / Local / Remote from catchment rules (25 mi OR ~60 min @ 40 mph; far+&lt;1.2tpd→Remote; far+≥1.2→Staffed).</p>
<div class="kpis">
  <div class="kpi"><b>${s.sites ?? sites.length}</b><span>Sites</span></div>
  <div class="kpi"><b>${s.campuses ?? "—"}</b><span>Campuses</span></div>
  <div class="kpi"><b>${s.day1_techs ?? "—"}</b><span>Day-one techs (hint)</span></div>
  <div class="kpi"><b>${role.Staffed ?? 0}/${role.Local ?? 0}/${role.Remote ?? 0}</b><span>S / L / R</span></div>
</div>
<h2>Map summary</h2>
<p>Pins: <span class="pill staffed">Staffed ${role.Staffed ?? 0}</span>
<span class="pill local">Local ${role.Local ?? 0}</span>
<span class="pill remote">Remote ${role.Remote ?? 0}</span>.
Coords present on ${sites.filter((r) => r.latitude != null && r.longitude != null).length} of ${sites.length} sites.</p>
<h2>Scenario strip (design)</h2>
<ul>
<li><b>Day one</b> — ${s.day1_techs ?? "—"} field techs (mapper hint / floors)</li>
<li><b>750:1 / 1000:1 / 1500:1</b> — ratio guardrails only; load /cost-model for priced ladder</li>
<li><b>Delivery KPIs</b> — FTFR ≥85% design · avoidable dispatch ~14% · util 75–85% · failed-visit cost +34–44%</li>
</ul>
<h2>Sites</h2>
<table>
<thead><tr><th>ID</th><th>Name</th><th>City</th><th>Country</th><th>Role</th><th>TPD</th><th>Users</th><th>Lat</th><th>Lon</th></tr></thead>
<tbody>${rows}</tbody>
</table>
<p class="mute">Gap vs python -m engine run: ${(s.gap_vs_engine || []).join(" · ") || "see suite docs"}</p>
</div>
</body>
</html>`;
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function exportPack(pack, opts = {}) {
    if (!pack) throw new Error("No sandbox deal to export");
    const label = sanitizeLabel(opts.dealLabel || pack.dealLabel || "Sample");
    const base = packBasename(label);
    const summaryJson = JSON.stringify(pack.summary || {}, null, 2);
    const fullJson = JSON.stringify(pack, null, 2);
    const csv =
      (window.SSSandbox && window.SSSandbox.costModelLoadCsv(pack)) ||
      "Site,mapped_role\n";
    const md = pptOutline({ ...pack, dealLabel: label });
    const html = offlineHtml({ ...pack, dealLabel: label });

    if (typeof JSZip !== "undefined") {
      const zip = new JSZip();
      const folder = zip.folder(base);
      folder.file("Offline_Proposal_Snapshot.html", html);
      folder.file("PPT_Outline.md", md);
      folder.file("Cost_Model_Load.csv", csv);
      folder.file("engine_summary.json", summaryJson);
      folder.file("sandbox_deal_full.json", fullJson);
      folder.file(
        "README.txt",
        `Site Services proposal pack\nDeal label: ${label}\nGenerated: ${new Date().toISOString()}\n\nContents:\n- Offline_Proposal_Snapshot.html\n- PPT_Outline.md\n- Cost_Model_Load.csv\n- engine_summary.json (bridge-shaped)\n- sandbox_deal_full.json (sites + summary)\n\nThis is a browser catchment bridge, not a full python -m engine run.\n`
      );
      const blob = await zip.generateAsync({ type: "blob" });
      downloadBlob(blob, `${base}.zip`);
      return { mode: "zip", filename: `${base}.zip` };
    }

    downloadBlob(new Blob([html], { type: "text/html" }), `${base}_Offline.html`);
    await delay(200);
    downloadBlob(new Blob([md], { type: "text/markdown" }), `${base}_PPT_Outline.md`);
    await delay(200);
    downloadBlob(new Blob([csv], { type: "text/csv" }), `${base}_Cost_Model_Load.csv`);
    await delay(200);
    downloadBlob(new Blob([summaryJson], { type: "application/json" }), `${base}_engine_summary.json`);
    return { mode: "multi", filename: base };
  }

  function delay(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  window.SSProposalExport = { exportPack, pptOutline, offlineHtml, packBasename };
})();
