/**
 * Scenario compare strip — day-one vs ratio bands + delivery KPI callouts.
 */
(() => {
  const DELIVERY = {
    ftfr_design: 0.85,
    ftfr_label: "FTFR ≥85% design",
    avoidable_dispatch: 0.14,
    util_low: 0.75,
    util_high: 0.85,
    failed_visit_uplift_low: 0.34,
    failed_visit_uplift_high: 0.44,
    tech_bar_hint:
      "Tech-bar / virtual overlay (Deal B pattern) can absorb walk-in + remote deflection — not additive to day-one campus floors.",
  };

  function pct(n) {
    return Math.round(n * 100) + "%";
  }

  function money(n) {
    if (n == null || !Number.isFinite(+n)) return "—";
    return "$" + Math.round(+n).toLocaleString("en-US");
  }

  function techsForRatio(users, ratio, campuses, floor) {
    const camp = Math.max(1, campuses || 1);
    const fl = Math.max(1, floor || 2);
    return Math.max(camp * Math.max(1, fl - 1), Math.ceil(users / ratio));
  }

  function buildScenarios(summary) {
    const users = +(summary?.users || 0) || 0;
    const campuses = +(summary?.campuses || 1) || 1;
    const day1 = +(summary?.day1_techs || 0) || 0;
    const floor = +(summary?.settings_subset?.team_floor || 2);
    const engineScenarios = Array.isArray(summary?.scenarios) ? summary.scenarios : null;

    if (engineScenarios && engineScenarios.length) {
      return engineScenarios
        .filter((s) => s.key === "day1" || s.key === "r750" || s.key === "r1000" || s.key === "r1500" || s.goal)
        .slice(0, 4)
        .map((s) => ({
          key: s.key,
          name: s.name,
          techs: s.techs,
          ratio: s.ratio,
          ratioImplied: s.ratioImplied || (s.techs ? Math.round(users / s.techs) : null),
          total: s.total,
          defl: s.defl,
          zt: s.zt,
        }));
    }

    const day1Techs = Math.max(campuses * floor, Math.round(day1));
    return [
      {
        key: "day1",
        name: "Day one (demand)",
        techs: day1Techs,
        ratio: null,
        ratioImplied: day1Techs ? Math.round(users / day1Techs) : null,
        total: null,
        defl: 0,
        zt: 15,
      },
      {
        key: "r750",
        name: "750:1 goal",
        techs: techsForRatio(users, 750, campuses, floor),
        ratio: 750,
        ratioImplied: null,
        total: null,
        defl: 12,
        zt: 40,
      },
      {
        key: "r1000",
        name: "1000:1 stretch",
        techs: techsForRatio(users, 1000, campuses, floor),
        ratio: 1000,
        ratioImplied: null,
        total: null,
        defl: 20,
        zt: 60,
      },
      {
        key: "r1500",
        name: "1500:1 art of possible",
        techs: techsForRatio(users, 1500, campuses, floor),
        ratio: 1500,
        ratioImplied: null,
        total: null,
        defl: 32,
        zt: 90,
      },
    ].map((s) => ({
      ...s,
      ratioImplied: s.ratioImplied || (s.techs ? Math.round(users / s.techs) : null),
    }));
  }

  function renderStrip(container, summary, opts = {}) {
    if (!container) return;
    const scenarios = buildScenarios(summary || {});
    const role = summary?.role_split || {};
    const overlays = summary?.overlays || {};
    const dealLabel = summary?.deal_label || opts.dealLabel || "Sample";

    container.innerHTML = `
      <div class="ss-scenario-strip" data-no-export="${opts.hideExport ? "0" : "0"}">
        <div class="ss-scenario-head">
          <div>
            <div class="ss-scenario-kicker">Scenario compare</div>
            <h3>Day-one vs ratio-band ladder · ${escapeHtml(dealLabel)}</h3>
            <p class="ss-scenario-sub">Ratios are commercial guardrails. Day-one follows demand + catchment floors. Delivery KPIs are industry-typical design targets (see ops_kpis / field_services_delivery_metrics).</p>
          </div>
          <div class="ss-scenario-meta">
            <span>${summary?.sites ?? "—"} sites</span>
            <span>${summary?.campuses ?? "—"} campuses</span>
            <span>${role.Staffed ?? 0}S / ${role.Local ?? 0}L / ${role.Remote ?? 0}R</span>
          </div>
        </div>
        <div class="ss-scenario-cols">
          ${scenarios
            .map(
              (s) => `
            <div class="ss-scenario-card${s.key === "day1" ? " is-day1" : ""}${s.key === "r750" ? " is-goal" : ""}">
              <div class="ss-scenario-name">${escapeHtml(s.name)}</div>
              <div class="ss-scenario-techs">${s.techs ?? "—"} <small>techs</small></div>
              <div class="ss-scenario-row"><span>Implied ratio</span><b>${s.ratioImplied ? s.ratioImplied + ":1" : "—"}</b></div>
              <div class="ss-scenario-row"><span>Deflect / ZT</span><b>${s.defl ?? 0}% / ${s.zt ?? 0}%</b></div>
              <div class="ss-scenario-row"><span>Annual (if priced)</span><b>${money(s.total)}</b></div>
            </div>`
            )
            .join("")}
        </div>
        <div class="ss-kpi-row">
          <div class="ss-kpi"><b>${pct(DELIVERY.ftfr_design)}</b><span>FTFR design floor</span></div>
          <div class="ss-kpi"><b>~${pct(DELIVERY.avoidable_dispatch)}</b><span>Avoidable dispatch (median)</span></div>
          <div class="ss-kpi"><b>${pct(DELIVERY.util_low)}–${pct(DELIVERY.util_high)}</b><span>Utilization band</span></div>
          <div class="ss-kpi"><b>+${pct(DELIVERY.failed_visit_uplift_low)}–${pct(DELIVERY.failed_visit_uplift_high)}</b><span>Failed-visit cost uplift</span></div>
        </div>
        <div class="ss-techbar-hint">
          <strong>Tech-bar hint</strong> — ${escapeHtml(DELIVERY.tech_bar_hint)}
          Overlays in summary: field ${overlays.field_techs ?? "—"} · bars ${overlays.tech_bars ?? 0} · virtual ${overlays.virtual_techs ?? 0}.
        </div>
      </div>
    `;
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function stripCss() {
    return `
.ss-scenario-strip{margin:16px 0;padding:16px 18px;border:1px solid var(--doc-line,#E4E8F0);border-radius:14px;background:linear-gradient(165deg,#fff 0%,#f4f6fb 55%,#fff6f1 100%);box-shadow:0 3px 12px rgba(133,149,176,.12)}
.ss-scenario-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap;margin-bottom:12px}
.ss-scenario-kicker{color:var(--acc,#D86A44);font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:11px}
.ss-scenario-strip h3{margin:4px 0;font-family:Cambria,Georgia,var(--font-display,serif);color:var(--navy,#13294B);font-size:18px}
.ss-scenario-sub{margin:0;color:var(--mute,#8A93A6);font-size:12.5px;max-width:62ch}
.ss-scenario-meta{display:flex;flex-wrap:wrap;gap:8px}
.ss-scenario-meta span{font-size:11.5px;font-weight:700;color:var(--slate,#54607A);background:#fff;border:1px solid var(--doc-line,#E4E8F0);border-radius:999px;padding:4px 10px}
.ss-scenario-cols{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
@media(max-width:900px){.ss-scenario-cols{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.ss-scenario-cols{grid-template-columns:1fr}}
.ss-scenario-card{background:#fff;border:1px solid var(--doc-line,#E4E8F0);border-radius:12px;padding:12px 14px}
.ss-scenario-card.is-day1{border-color:#2fd6c2;box-shadow:0 0 0 2px rgba(47,214,194,.16)}
.ss-scenario-card.is-goal{border-color:#F0CDBB;background:#fffaf7}
.ss-scenario-name{font-size:12.5px;font-weight:700;color:var(--navy,#13294B);margin-bottom:6px}
.ss-scenario-techs{font-family:Cambria,Georgia,serif;font-size:28px;color:var(--navy,#13294B);line-height:1;margin-bottom:8px}
.ss-scenario-techs small{font-size:12px;color:var(--mute,#8A93A6);font-family:inherit;font-weight:600}
.ss-scenario-row{display:flex;justify-content:space-between;gap:8px;font-size:12px;padding:3px 0;border-top:1px dashed var(--doc-line,#E4E8F0);color:var(--slate,#54607A)}
.ss-scenario-row b{color:var(--navy,#13294B)}
.ss-kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}
@media(max-width:900px){.ss-kpi-row{grid-template-columns:1fr 1fr}}
.ss-kpi{background:#13294B;color:#fff;border-radius:12px;padding:12px 14px}
.ss-kpi b{display:block;font-family:Cambria,Georgia,serif;font-size:22px;margin-bottom:2px}
.ss-kpi span{font-size:11px;opacity:.78;text-transform:uppercase;letter-spacing:.04em;font-weight:600}
.ss-techbar-hint{margin-top:12px;font-size:12.5px;color:var(--slate,#54607A);padding:10px 12px;border-radius:10px;background:rgba(47,214,194,.1);border:1px solid rgba(47,214,194,.28)}
.ss-techbar-hint strong{color:var(--navy,#13294B)}
`;
  }

  function injectStyles() {
    if (document.getElementById("ss-scenario-strip-css")) return;
    const style = document.createElement("style");
    style.id = "ss-scenario-strip-css";
    style.textContent = stripCss();
    document.head.appendChild(style);
  }

  window.SSScenarioStrip = {
    DELIVERY,
    buildScenarios,
    renderStrip,
    injectStyles,
  };
})();
