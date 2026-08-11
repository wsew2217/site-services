(() => {
  const NAV = [
    {
      label: "Site Services",
      items: [
        { href: "/", id: "home", title: "Home" },
        { href: "/structure", id: "structure", title: "Structure & Methodology" },
        { href: "/coverage", id: "coverage", title: "Coverage" },
        { href: "/cost-model", id: "cost-model", title: "Cost Model (Generic)" },
      ],
    },
    {
      label: "VC Mapper / Solutioning Kit",
      items: [
        { href: "/vc-kit", id: "vc-kit", title: "Kit Overview" },
        { href: "/sandbox", id: "sandbox", title: "Deal Sandbox" },
        { href: "/sandbox/map", id: "sandbox-map", title: "Deal Map" },
        { href: "/vc-kit/chat", id: "vc-kit-chat", title: "Kit Chat" },
        { href: "/vc-kit/template", id: "vc-kit-template", title: "Template Pack" },
        { href: "/vc-kit/mapper", id: "vc-kit-mapper", title: "Mapper & Rules" },
        { href: "/vc-kit/agent", id: "vc-kit-agent", title: "SalesChat Agent Pack" },
        { href: "/vc-kit/runbook", id: "vc-kit-runbook", title: "Pilot Runbook" },
      ],
    },
    {
      label: "Reference Deal A",
      items: [
        { href: "/summary", id: "summary", title: "Executive Summary" },
        { href: "/changes", id: "changes", title: "What Changed" },
        { href: "/methodology", id: "methodology", title: "Deal A Methodology" },
        { href: "/coverage-deal-a", id: "coverage-deal-a", title: "Campus Coverage Map" },
        { href: "/cost-model-deal-a", id: "cost-model-deal-a", title: "Cost Model (Deal A)" },
        { href: "/story", id: "story", title: "Build Story" },
        { href: "/how-we-built", id: "how-we-built", title: "How We Built" },
        { href: "/deck", id: "deck", title: "Customer Deck" },
        { href: "/deck-internal", id: "deck-internal", title: "Internal Deck" },
        { href: "/workbook", id: "workbook", title: "Customer Workbook" },
        { href: "/workbook-internal", id: "workbook-internal", title: "Internal Workbook" },
      ],
    },
    {
      label: "Reference Deal B",
      items: [
        { href: "/deal-b", id: "deal-b", title: "Tech Bar Pattern" },
        { href: "/cost-model-deal-b", id: "cost-model-deal-b", title: "Cost Model (Deal B)" },
      ],
    },
  ];

  const page = document.body.dataset.page || "home";
  const mode = document.body.dataset.mode || "shell";

  const dealAPages = new Set(
    (NAV.find((g) => g.label === "Reference Deal A") || { items: [] }).items.map((i) => i.id)
  );
  if (dealAPages.has(page)) document.body.classList.add("theme-deal-a");

  function navHtml(compact = false) {
    return NAV.map((group) => {
      const links = group.items
        .map((item) => {
          const active = item.id === page ? " is-active" : "";
          return `<a href="${item.href}" class="${active.trim()}" data-nav="${item.id}"><span class="dot"></span>${item.title}</a>`;
        })
        .join("");
      return `<div class="suite-nav-group"><div class="suite-nav-label">${group.label}</div><nav class="suite-nav">${links}</nav></div>`;
    }).join("");
  }

  function currentTitle() {
    for (const group of NAV) {
      const hit = group.items.find((i) => i.id === page);
      if (hit) return hit.title;
    }
    return "Site Services";
  }

  function buildShell(mainInner) {
    return `
      <div class="suite-backdrop" data-suite-close></div>
      <div class="suite-shell">
        <aside class="suite-sidebar" aria-label="Site">
          <a class="suite-brand" href="/">
            <div class="suite-mark">SS</div>
            <div class="suite-brand-text">
              <strong>Site Services</strong>
              <span>Same process flows as Field Services</span>
            </div>
          </a>
          ${navHtml()}
          <div class="suite-sidebar-foot">
            Persistent navigation across every page.<br>
            Field Services Solution Design · 2026
          </div>
        </aside>
        <div class="suite-main">
          <div class="suite-topbar">
            <button class="suite-menu-btn" type="button" aria-label="Open menu" data-suite-menu>☰</button>
            <div class="suite-topbar-title">${currentTitle()}</div>
          </div>
          ${mainInner}
        </div>
      </div>
    `;
  }

  function buildToolChrome() {
    const toolLinks = [
      { id: "structure", href: "/structure", label: "Structure" },
      { id: "coverage", href: "/coverage", label: "Coverage" },
      { id: "vc-kit", href: "/vc-kit", label: "VC Kit" },
      { id: "sandbox", href: "/sandbox", label: "Sandbox" },
      { id: "vc-kit-chat", href: "/vc-kit/chat", label: "Chat" },
      { id: "coverage-deal-a", href: "/coverage-deal-a", label: "Map A" },
      { id: "deal-b", href: "/deal-b", label: "Deal B" },
      { id: "cost-model", href: "/cost-model", label: "Cost (Generic)" },
      { id: "cost-model-deal-a", href: "/cost-model-deal-a", label: "Cost (Deal A)" },
      { id: "cost-model-deal-b", href: "/cost-model-deal-b", label: "Cost (Deal B)" },
      { id: "deck", href: "/deck", label: "Deck A" },
      { id: "workbook", href: "/workbook", label: "Workbook A" },
    ]
      .map((t) => `<a href="${t.href}" class="${t.id === page ? "is-active" : ""}">${t.label}</a>`)
      .join("");

    return `
      <div class="suite-tool-chrome">
        <a class="back" href="/">← Suite home</a>
        <div class="title">${currentTitle()}</div>
        <div class="links">${toolLinks}</div>
      </div>
    `;
  }

  if (mode === "shell") {
    const existing = document.querySelector("[data-suite-content]");
    const content = existing
      ? existing.outerHTML
      : `<div data-suite-content>${document.body.innerHTML}</div>`;
    document.body.innerHTML = buildShell(content);
  } else if (mode === "tool") {
    document.body.insertAdjacentHTML("afterbegin", buildToolChrome());
  }

  document.body.addEventListener("click", (e) => {
    const menu = e.target.closest("[data-suite-menu]");
    const close = e.target.closest("[data-suite-close]");
    if (menu) document.body.classList.toggle("nav-open");
    if (close) document.body.classList.remove("nav-open");
  });

  document.querySelectorAll(".suite-nav a").forEach((a) => {
    a.addEventListener("click", () => document.body.classList.remove("nav-open"));
  });

  /** Blob-download a printable article snapshot of the current doc page. */
  window.suiteDownloadPageHtml = function suiteDownloadPageHtml(opts) {
    const options = opts || {};
    const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, (c) => (c === "T" ? "_" : "-"));
    const filename = options.filename || `site-services-page_${stamp}.html`;
    const title = options.title || document.title || "Site Services";
    const root =
      document.querySelector("[data-suite-content] .page") ||
      document.querySelector("[data-suite-content]") ||
      document.querySelector(".page") ||
      document.body;
    const clone = root.cloneNode(true);
    clone.querySelectorAll("script,.help-tip,.suite-menu-btn,[data-no-export]").forEach((el) => el.remove());
    const bodyHtml = clone.innerHTML;
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title.replace(/</g, "&lt;")} · Offline export</title>
<style>
:root{--navy:#13294B;--slate:#54607A;--acc:#D86A44;--tint:#F4F6FB;--line:#E4E8F0;--ink:#232A35;--mute:#8A93A6}
*{box-sizing:border-box}body{margin:0;font-family:Calibri,'Segoe UI',system-ui,sans-serif;color:var(--ink);background:#fff;font-size:14.5px;line-height:1.5}
.wrap{max-width:900px;margin:0 auto;padding:24px 18px 48px}
.banner{background:#fff6f1;border-left:4px solid var(--acc);padding:10px 12px;border-radius:0 10px 10px 0;margin-bottom:18px;font-size:13px;color:var(--slate)}
h1,h2,h3{font-family:Cambria,Georgia,serif;color:var(--navy)}
a{color:var(--navy)}table{border-collapse:collapse;width:100%;font-size:13px;margin:10px 0}
th{background:var(--navy);color:#fff;text-align:left;padding:7px 9px}td{border:1px solid var(--line);padding:6px 9px}
.card,.flow-step,.kit-callout{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0;background:var(--tint)}
.mute{color:var(--mute);font-size:12.5px}code{font-size:12.5px}
.kit-dl{display:none}.help-tip{display:none}
@media print{body{background:#fff}}
</style>
</head>
<body>
<div class="wrap">
<div class="banner"><b>Offline export</b> · ${stamp} · Snapshot of “${title.replace(/</g, "&lt;")}”. Live suite links may not work offline. No customer deal data on the live site.</div>
${bodyHtml}
</div>
</body>
</html>`;
    const blob = new Blob([html], { type: "text/html;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1500);
  };
})();
