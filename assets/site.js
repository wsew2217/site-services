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
      { id: "coverage-deal-a", href: "/coverage-deal-a", label: "Map A" },
      { id: "deal-b", href: "/deal-b", label: "Deal B" },
      { id: "cost-model", href: "/cost-model", label: "Cost (Generic)" },
      { id: "cost-model-deal-a", href: "/cost-model-deal-a", label: "Cost (Deal A)" },
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
})();
