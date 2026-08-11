/**
 * VC Kit chat client — live AI Gateway when /api/chat is available, else offline FAQ.
 */
(() => {
  const FAQ = [
    {
      q: /catchment|local range|25\s*mi|1\.2|remote|staffed|hub/i,
      a: `Catchment rules (v1):\n• Local range = ≤25 miles OR ≤60 minutes drive proxy @ 40 mph (inclusive OR).\n• Near any Staffed campus → always Local (never Remote).\n• Remote only if far AND tickets/day < 1.2.\n• Far AND ≥1.2 tpd → promote to Staffed campus.\n• Hub priority: tickets_per_day → users → seat_count; hub threshold 3.0 tpd.`,
    },
    {
      q: /pipeline|mapper|template|cost.?model.?load|bridge|engine run/i,
      a: `Preferred pipeline:\n1) Fill VC_Site_Input_Template in vc_template_pack_v1_0.xlsx\n2) Run python vc_mapper.py (or use /sandbox browser catchment)\n3) Review VC_Mapped_Sites / Exceptions / Summary\n4) Cost_Model_Load → bridge JSON or Sites intake\n5) Load summary on /cost-model\n\npython -m engine run is the older/parallel full staffing path — richer cost ladder, not required to start mapping.`,
    },
    {
      q: /sandbox|upload|excel|one.?click/i,
      a: `One-click deal sandbox (/sandbox):\n• Upload VC template or address-request-like sheets (SheetJS in browser).\n• Runs catchment + builds engine-summary-shaped JSON.\n• Saves to sessionStorage and can open /cost-model with data applied.\n• Map at /sandbox/map (Leaflet + OSM).\n• Gap: not a full python -m engine run (no full cash/OEM workbook).`,
    },
    {
      q: /export|proposal|zip|ppt|download/i,
      a: `Proposal export pack (from sandbox results):\n• Offline HTML snapshot\n• PPT outline (.md)\n• Cost_Model_Load.csv\n• engine_summary.json\nNamed Site_Services_Proposal_Pack_<timestamp> — deal label only if you typed one (sanitized). No customer names in default samples.`,
    },
    {
      q: /ftfr|utilization|avoidable|kpi|delivery|failed.?visit/i,
      a: `Delivery design KPIs (industry-typical, not customer truth):\n• FTFR / first-visit resolution design ≥85%\n• Avoidable dispatch median ~14%\n• Technician utilization band 75–85% (design 85%)\n• Failed first visit → resolution cost +34–44%\nSee engine/defaults/ops_kpis.json and field_services_delivery_metrics.md.`,
    },
    {
      q: /deal a|deal b|tech.?bar|reference/i,
      a: `Reference deals are labeled examples only:\n• Deal A — global virtual-campus footprint example (not universal defaults).\n• Deal B — tech-bar walk-in + virtual overlay pattern (~1500:1–2000:1 band).\nGeneric Site Services = methodology + engine + atlas + sandbox — not one account’s campus count.`,
    },
    {
      q: /file|inventory|download|yaml|offline/i,
      a: `Key kit files under /assets/vc-kit/:\n• vc_template_pack_v1_0.xlsx + mapped sample\n• default_rules.yaml · column_aliases.yaml\n• vc_mapper.py · cost_model_bridge.py · vc_mapper_package.zip\n• AI_REBUILD_PROMPT.txt · offline hub · site-services-offline.zip\n• SalesChat text pack (UI publish remains manual)`,
    },
    {
      q: /role lane|primary|secondary|fmo|process/i,
      a: `FMO ladder: Intake → Misroute/QA → Remote? → Contact & schedule → Tower work → Logistics → Finalize.\nPrimary role lanes are home-queue splits (Desktop-Incident, Desktop-Requests, Remote-Desktop, Staging, Site-Lead, Telecom, Network-VDI, Projects). Secondary/Tertiary are flex labels — not additive FTE.`,
    },
  ];

  const SYSTEM_BLURB = `You are the Site Services VC Kit assistant. Help solutioners with catchment rules, pipeline steps, file inventory, sandbox, cost-model bridge, and delivery KPIs. Never invent customer names, ticket volumes, or headcount. Cost_Model_Load is a bridge, not a priced proposal. Prefer mapper path; engine run is optional full staffing. Sanitize: Reference Deal A/B only.`;

  function offlineAnswer(message) {
    const text = String(message || "").trim();
    if (!text) return "Ask about catchment, pipeline, sandbox, export, KPIs, or kit files.";
    for (const item of FAQ) {
      if (item.q.test(text)) return item.a;
    }
    return (
      "Offline assistant (no live LLM key detected for this session).\n\n" +
      "I can help with: catchment rules, VC pipeline, /sandbox upload, map, scenario strip, proposal export, delivery KPIs, Deal A vs B, and kit file inventory.\n\n" +
      "Try: “What are the catchment rules?” or “How do I load sandbox into cost-model?”\n\n" +
      SYSTEM_BLURB
    );
  }

  async function detectMode() {
    try {
      const r = await fetch("/api/chat-status", { cache: "no-store" });
      if (!r.ok) return { mode: "offline", reason: "status " + r.status };
      const j = await r.json();
      return j;
    } catch (e) {
      return { mode: "offline", reason: e.message || "unreachable" };
    }
  }

  async function ask(message, history = []) {
    const status = await detectMode();
    if (status.mode !== "live") {
      return { mode: "offline", text: offlineAnswer(message) };
    }
    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history: history.slice(-8) }),
      });
      if (!r.ok) {
        const err = await r.text();
        return {
          mode: "offline",
          text: offlineAnswer(message) + "\n\n(Live chat unavailable: HTTP " + r.status + " — " + err.slice(0, 120) + ")",
        };
      }
      const j = await r.json();
      return { mode: "live", text: j.text || j.reply || "(empty response)" };
    } catch (e) {
      return { mode: "offline", text: offlineAnswer(message) + "\n\n(Live chat error: " + e.message + ")" };
    }
  }

  window.SSKitChat = { ask, detectMode, offlineAnswer, SYSTEM_BLURB, FAQ };
})();
