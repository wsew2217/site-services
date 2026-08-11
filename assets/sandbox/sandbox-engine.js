/**
 * Browser VC sandbox engine — catchment + Cost_Model_Load bridge.
 * Port of tools/vc_mapper rules (not a full python -m engine run).
 */
(() => {
  const STORAGE_KEY = "ss_sandbox_v1";
  const EARTH_KM = 6371;
  const MILES_PER_KM = 0.621371192;

  const DEFAULT_RULES = {
    working_days_per_year: 252,
    months_per_year: 12,
    hub_threshold_tickets_per_day: 3.0,
    remote_threshold_tickets_per_day: 1.2,
    cluster_radius_miles: 25.0,
    max_drive_minutes: 60.0,
    avg_drive_speed_mph: 40.0,
    enable_dispatch_override: true,
    hub_selection_priority: ["tickets_per_day", "users", "seat_count"],
    rules_version: "1.0.0",
  };

  const ALIASES = {
    site_id: ["site id", "location id", "customer site id"],
    site_name: ["site name", "location name", "location", "site"],
    address_full: ["address", "full address", "street address"],
    city: ["city"],
    state_province: ["state", "province", "state_province"],
    postal_code: ["zip", "zipcode", "postal code", "postalcode"],
    country: ["country"],
    users: ["users", "user count", "end users"],
    seat_count: ["seats", "seat count", "seats"],
    tickets_per_day: ["calls/day", "tickets/day", "tickets per day", "tpd"],
    tickets_per_month: ["calls/month", "tickets/month", "tickets per month", "tpm"],
    tickets_per_year: ["calls/year", "tickets/year", "tickets per year", "ticketsyr", "tickets_yr"],
    region: ["region"],
    district: ["district"],
    customer_site_type: ["site type", "customer_site_type"],
    notes: ["notes", "comments"],
    latitude: ["lat", "latitude"],
    longitude: ["lon", "lng", "longitude"],
    mapped_role: ["mapped role", "role", "coverage role"],
  };

  const ROLE_LANES = [
    "Desktop-Incident",
    "Desktop-Requests",
    "Remote-Desktop",
    "Staging",
    "Site-Lead",
    "Telecom",
    "Network-VDI",
    "Projects",
  ];
  const ROLE_MIX = {
    "Desktop-Incident": 0.28,
    "Desktop-Requests": 0.22,
    "Remote-Desktop": 0.12,
    Staging: 0.1,
    "Site-Lead": 0.08,
    Telecom: 0.08,
    "Network-VDI": 0.06,
    Projects: 0.06,
  };

  function normHeader(s) {
    return String(s || "")
      .trim()
      .toLowerCase()
      .replace(/_/g, " ")
      .replace(/-/g, " ");
  }

  function buildAliasLookup() {
    const lookup = {};
    for (const [canonical, alist] of Object.entries(ALIASES)) {
      lookup[normHeader(canonical)] = canonical;
      for (const a of alist) lookup[normHeader(a)] = canonical;
    }
    // Engine Sites headers
    lookup["ticketsyr"] = "tickets_per_year";
    lookup["tickets yr"] = "tickets_per_year";
    lookup["postalcode"] = "postal_code";
    lookup["coveraclass"] = "coverage_class";
    lookup["coverageclass"] = "coverage_class";
    return lookup;
  }

  const ALIAS_LOOKUP = buildAliasLookup();

  function toFloat(val, def = 0) {
    if (val == null || val === "") return def;
    if (typeof val === "number") return Number.isFinite(val) ? val : def;
    const n = parseFloat(String(val).replace(/,/g, ""));
    return Number.isFinite(n) ? n : def;
  }

  function haversineMiles(lat1, lon1, lat2, lon2) {
    if ([lat1, lon1, lat2, lon2].some((x) => x == null || !Number.isFinite(+x))) return 9e9;
    const a = (+lat1 * Math.PI) / 180;
    const b = (+lon1 * Math.PI) / 180;
    const c = (+lat2 * Math.PI) / 180;
    const e = (+lon2 * Math.PI) / 180;
    const km =
      2 *
      EARTH_KM *
      Math.asin(
        Math.sqrt(
          Math.sin((c - a) / 2) ** 2 + Math.cos(a) * Math.cos(c) * Math.sin((e - b) / 2) ** 2
        )
      );
    return km * MILES_PER_KM;
  }

  function estDriveMinutes(miles, speedMph) {
    if (miles >= 9e9 || speedMph <= 0) return 9e9;
    return (miles / speedMph) * 60;
  }

  function withinLocalRange(miles, rules) {
    if (miles >= 9e9) return false;
    const radius = +rules.cluster_radius_miles || 25;
    const maxMin = +rules.max_drive_minutes || 60;
    const speed = +rules.avg_drive_speed_mph || 40;
    const minutes = estDriveMinutes(miles, speed);
    return miles <= radius || minutes <= maxMin;
  }

  function normalizeTickets(row, workingDays, months) {
    const tpd = toFloat(row.tickets_per_day, NaN);
    const tpm = toFloat(row.tickets_per_month, NaN);
    const tpy = toFloat(row.tickets_per_year, NaN);
    let day = 0;
    if (Number.isFinite(tpd) && tpd > 0) day = tpd;
    else if (Number.isFinite(tpm) && tpm > 0) day = (tpm * months) / workingDays;
    else if (Number.isFinite(tpy) && tpy > 0) day = tpy / workingDays;
    const month = months ? (day * workingDays) / months : 0;
    const year = day * workingDays;
    return {
      tickets_per_day: Math.round(day * 1e6) / 1e6,
      tickets_per_month: Math.round(month * 1e4) / 1e4,
      tickets_per_year: Math.round(year * 100) / 100,
    };
  }

  function priorityScore(row, priority) {
    return priority.map((f) => toFloat(row[f], 0));
  }

  function cmpTuple(a, b) {
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      const d = (a[i] || 0) - (b[i] || 0);
      if (d !== 0) return d;
    }
    return 0;
  }

  function day1TechsHint(tpd, role) {
    if (role === "Remote") return 0;
    if (tpd <= 0) return role === "Staffed" ? 1 : 0;
    const raw = tpd / 8;
    if (role === "Staffed") return Math.max(1, Math.round(raw * 100) / 100);
    return Math.round(raw * 100) / 100;
  }

  function allocateRoleLanes(fieldTechs) {
    const weights = ROLE_LANES.map((l) => Math.max(0, ROLE_MIX[l] || 0));
    const totalW = weights.reduce((a, b) => a + b, 0) || 1;
    const norm = weights.map((w) => w / totalW);
    const primary = [];
    let assigned = 0;
    const n = ROLE_LANES.length;
    const ft = Math.max(0, Math.round(fieldTechs));
    for (let i = 0; i < n; i++) {
      let hc;
      if (ft <= 0) hc = 0;
      else if (i < n - 1) {
        hc = Math.round(ft * norm[i]);
        assigned += hc;
      } else hc = Math.max(0, ft - assigned);
      primary.push({
        Lane: ROLE_LANES[i],
        PrimaryHC: hc,
        Share: Math.round(norm[i] * 10000) / 10000,
        Secondary: "Desktop-Requests",
        Tertiary: "Projects",
      });
    }
    const drift = ft - primary.reduce((s, r) => s + r.PrimaryHC, 0);
    if (drift && primary.length) {
      let idx = 0;
      for (let i = 1; i < primary.length; i++) {
        if (primary[i].PrimaryHC > primary[idx].PrimaryHC) idx = i;
      }
      primary[idx].PrimaryHC = Math.max(0, primary[idx].PrimaryHC + drift);
    }
    return {
      note: "Primary HC is a reporting split of sized field techs. Secondary/Tertiary are flex, not additive.",
      primary,
      schedule_lanes: ["M", "TL", "T", "W", "S", "RR"],
      field_techs: ft,
    };
  }

  function renameRow(raw) {
    const out = {};
    for (const [k, v] of Object.entries(raw)) {
      const canon = ALIAS_LOOKUP[normHeader(k)] || null;
      if (canon) out[canon] = v;
      else out[normHeader(k).replace(/\s+/g, "_")] = v;
    }
    return out;
  }

  function sheetToObjects(workbook, preferredSheets) {
    if (typeof XLSX === "undefined") throw new Error("SheetJS (XLSX) not loaded");
    const names = workbook.SheetNames || [];
    let sheetName = null;
    for (const pref of preferredSheets) {
      const hit = names.find((n) => normHeader(n) === normHeader(pref));
      if (hit) {
        sheetName = hit;
        break;
      }
    }
    if (!sheetName) {
      // Prefer sheets with site-like headers
      for (const n of names) {
        const rows = XLSX.utils.sheet_to_json(workbook.Sheets[n], { defval: null, raw: false });
        if (!rows.length) continue;
        const keys = Object.keys(rows[0]).map(normHeader);
        if (keys.some((k) => k.includes("site") || k.includes("city") || k.includes("tickets"))) {
          sheetName = n;
          break;
        }
      }
    }
    if (!sheetName) sheetName = names[0];
    const rows = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName], { defval: null, raw: true });
    return { sheetName, rows: rows.map(renameRow) };
  }

  function assignRoles(sites, rules) {
    const workingDays = +rules.working_days_per_year || 252;
    const months = +rules.months_per_year || 12;
    const hubThreshold = +rules.hub_threshold_tickets_per_day || 3;
    const remoteThreshold = +rules.remote_threshold_tickets_per_day || 1.2;
    const priority = rules.hub_selection_priority || ["tickets_per_day", "users", "seat_count"];
    const enableDispatch = rules.enable_dispatch_override !== false;
    const speed = +rules.avg_drive_speed_mph || 40;

    const work = sites.map((s, i) => {
      const tickets = normalizeTickets(s, workingDays, months);
      const lat = toFloat(s.latitude, NaN);
      const lon = toFloat(s.longitude, NaN);
      return {
        ...s,
        _idx: i,
        site_id: String(s.site_id || s.site_name || `SITE-${i + 1}`),
        site_name: String(s.site_name || s.site_id || `Site ${i + 1}`),
        users: toFloat(s.users, 0),
        seat_count: toFloat(s.seat_count, toFloat(s.users, 0)),
        country: String(s.country || "").trim() || "_GLOBAL_",
        latitude: Number.isFinite(lat) ? lat : null,
        longitude: Number.isFinite(lon) ? lon : null,
        ...tickets,
        mapped_role: "Remote",
        is_hub: false,
        hub_site_id: "",
        hub_site_name: "",
        campus_id: "REMOTE",
        distance_to_hub_miles: null,
        est_drive_minutes: null,
        within_local_range: false,
        catchment_tickets_per_day: 0,
        dispatch_eligible: false,
        exception_flags: "",
        day1_techs_hint: 0,
      };
    });

    // If mapped_role already present on all rows (pre-mapped sample), keep and enrich
    const preMapped = work.every((r) => {
      const role = String(sites[r._idx].mapped_role || "").trim();
      return role === "Staffed" || role === "Local" || role === "Remote";
    });
    if (preMapped && work.length) {
      return work.map((r) => {
        const role = String(sites[r._idx].mapped_role).trim();
        const out = { ...r, mapped_role: role };
        out.is_hub = role === "Staffed";
        out.day1_techs_hint = day1TechsHint(out.tickets_per_day, role);
        out.dispatch_eligible = role === "Remote" && enableDispatch;
        if (role === "Staffed") {
          out.campus_id = out.campus_id && out.campus_id !== "REMOTE" ? out.campus_id : `CAMPUS-${out.site_id}`;
          out.distance_to_hub_miles = 0;
          out.est_drive_minutes = 0;
          out.within_local_range = true;
          out.hub_site_id = out.site_id;
          out.hub_site_name = out.site_name;
        }
        return out;
      });
    }

    let campusCounter = 0;
    const byCountry = new Map();
    work.forEach((r, i) => {
      const key = r.country;
      if (!byCountry.has(key)) byCountry.set(key, []);
      byCountry.get(key).push(i);
    });

    for (const [, idxs] of byCountry) {
      const geoIdx = idxs.filter((i) => work[i].latitude != null && work[i].longitude != null);
      const noGeo = idxs.filter((i) => !geoIdx.includes(i));

      for (const i of noGeo) {
        const tpd = work[i].tickets_per_day;
        if (tpd >= remoteThreshold) {
          work[i].mapped_role = "Staffed";
          work[i].is_hub = tpd >= hubThreshold;
          campusCounter += 1;
          work[i].campus_id = `CAMPUS-${campusCounter}-${work[i].site_id}`;
          work[i].hub_site_id = work[i].site_id;
          work[i].hub_site_name = work[i].site_name;
          work[i].distance_to_hub_miles = 0;
          work[i].est_drive_minutes = 0;
          work[i].exception_flags = "no_coords_promoted_staffed";
        } else {
          work[i].mapped_role = "Remote";
          work[i].dispatch_eligible = enableDispatch;
          work[i].campus_id = "REMOTE";
          work[i].exception_flags = "no_coords_remote";
        }
      }

      if (!geoIdx.length) continue;

      let bestHub = null;
      let bestCatch = -1;
      let bestPri = [];
      const ranked = [...geoIdx].sort((a, b) => {
        const qa = work[a].tickets_per_day >= hubThreshold ? 1 : 0;
        const qb = work[b].tickets_per_day >= hubThreshold ? 1 : 0;
        if (qa !== qb) return qb - qa;
        return cmpTuple(priorityScore(work[b], priority), priorityScore(work[a], priority));
      });

      for (const i of ranked) {
        let catchVol = 0;
        for (const j of geoIdx) {
          const mi = haversineMiles(
            work[i].latitude,
            work[i].longitude,
            work[j].latitude,
            work[j].longitude
          );
          if (withinLocalRange(mi, rules)) catchVol += work[j].tickets_per_day;
        }
        const pri = priorityScore(work[i], priority);
        if (catchVol > bestCatch || (catchVol === bestCatch && cmpTuple(pri, bestPri) > 0)) {
          bestHub = i;
          bestCatch = catchVol;
          bestPri = pri;
        }
      }

      const staffed = new Set();
      if (bestHub != null) {
        staffed.add(bestHub);
        work[bestHub].catchment_tickets_per_day = bestCatch;
      }

      const candidates = [...geoIdx]
        .filter((i) => !staffed.has(i))
        .sort((a, b) => cmpTuple(priorityScore(work[b], priority), priorityScore(work[a], priority)));

      let changed = true;
      while (changed) {
        changed = false;
        for (const i of candidates) {
          if (staffed.has(i)) continue;
          const near = [...staffed].some((s) =>
            withinLocalRange(
              haversineMiles(
                work[i].latitude,
                work[i].longitude,
                work[s].latitude,
                work[s].longitude
              ),
              rules
            )
          );
          if (near) continue;
          if (work[i].tickets_per_day >= remoteThreshold) {
            staffed.add(i);
            changed = true;
          }
        }
      }

      const campusForHub = {};
      [...staffed]
        .sort((a, b) => cmpTuple(priorityScore(work[b], priority), priorityScore(work[a], priority)))
        .forEach((s) => {
          campusCounter += 1;
          campusForHub[s] = `CAMPUS-${campusCounter}-${work[s].site_id}`;
        });

      let staffedList = [...staffed];
      for (const i of geoIdx) {
        if (staffed.has(i)) {
          work[i].mapped_role = "Staffed";
          work[i].is_hub = true;
          work[i].hub_site_id = work[i].site_id;
          work[i].hub_site_name = work[i].site_name;
          work[i].campus_id = campusForHub[i];
          work[i].distance_to_hub_miles = 0;
          work[i].est_drive_minutes = 0;
          work[i].within_local_range = true;
          let catchVol = 0;
          for (const j of geoIdx) {
            const mi = haversineMiles(
              work[i].latitude,
              work[i].longitude,
              work[j].latitude,
              work[j].longitude
            );
            if (withinLocalRange(mi, rules)) catchVol += work[j].tickets_per_day;
          }
          work[i].catchment_tickets_per_day = Math.round(catchVol * 10000) / 10000;
          if (work[i].tickets_per_day < hubThreshold) {
            work[i].exception_flags = "staffed_below_hub_threshold";
          }
          continue;
        }

        let bestD = 9e9;
        let bestS = null;
        for (const s of staffedList) {
          const mi = haversineMiles(
            work[i].latitude,
            work[i].longitude,
            work[s].latitude,
            work[s].longitude
          );
          if (mi < bestD) {
            bestD = mi;
            bestS = s;
          }
        }
        work[i].distance_to_hub_miles = bestD < 9e9 ? Math.round(bestD * 100) / 100 : null;
        work[i].est_drive_minutes =
          bestD < 9e9 ? Math.round(estDriveMinutes(bestD, speed) * 10) / 10 : null;
        const local = bestS != null && withinLocalRange(bestD, rules);
        work[i].within_local_range = local;
        const tpd = work[i].tickets_per_day;

        if (local) {
          work[i].mapped_role = "Local";
          work[i].hub_site_id = work[bestS].site_id;
          work[i].hub_site_name = work[bestS].site_name;
          work[i].campus_id = campusForHub[bestS];
          work[i].catchment_tickets_per_day = work[bestS].catchment_tickets_per_day;
        } else if (tpd >= remoteThreshold) {
          work[i].mapped_role = "Staffed";
          work[i].is_hub = true;
          campusCounter += 1;
          work[i].campus_id = `CAMPUS-${campusCounter}-${work[i].site_id}`;
          work[i].hub_site_id = work[i].site_id;
          work[i].hub_site_name = work[i].site_name;
          work[i].distance_to_hub_miles = 0;
          work[i].est_drive_minutes = 0;
          staffed.add(i);
          campusForHub[i] = work[i].campus_id;
          staffedList = [...staffed];
          work[i].exception_flags = "promoted_far_high_volume";
        } else {
          work[i].mapped_role = "Remote";
          work[i].dispatch_eligible = enableDispatch;
          work[i].campus_id = "REMOTE";
          if (bestS != null) {
            work[i].hub_site_id = work[bestS].site_id;
            work[i].hub_site_name = work[bestS].site_name;
          }
          work[i].exception_flags = "remote_dispatch";
        }
      }

      if (!staffed.size && geoIdx.length) {
        for (const i of geoIdx) {
          work[i].mapped_role = "Remote";
          work[i].dispatch_eligible = enableDispatch;
          work[i].campus_id = "REMOTE";
          work[i].exception_flags = "all_remote_low_volume";
        }
      }
    }

    return work.map((r) => {
      r.day1_techs_hint = day1TechsHint(r.tickets_per_day, r.mapped_role);
      return r;
    });
  }

  function buildSummary(mapped, opts = {}) {
    const staffed = mapped.filter((r) => r.mapped_role === "Staffed").length;
    const local = mapped.filter((r) => r.mapped_role === "Local").length;
    const remote = mapped.filter((r) => r.mapped_role === "Remote").length;
    const users = mapped.reduce((s, r) => s + toFloat(r.users, 0), 0);
    const ticketsYr = mapped.reduce((s, r) => s + toFloat(r.tickets_per_year, 0), 0);
    const day1 = mapped.reduce((s, r) => s + toFloat(r.day1_techs_hint, 0), 0);
    const campuses = Math.max(staffed, mapped.length ? 1 : 0);
    const tpu = users ? ticketsYr / users : 0;
    const fieldTechs = Math.round(day1 * 10) / 10;
    const leads = fieldTechs > 0 ? Math.ceil(fieldTechs / 10) : 0;
    const managers = fieldTechs > 0 ? Math.ceil(fieldTechs / 24) : 0;
    const roleBreakdown = allocateRoleLanes(fieldTechs);

    return {
      source: "browser-sandbox-v1",
      version: "1.0.0",
      note:
        "Browser catchment + Cost_Model_Load bridge — not a full python -m engine run. " +
        "Prefer engine run on Sites intake for production staffing / cost JSON.",
      deal_label: opts.dealLabel || "Sample",
      sites: mapped.length,
      users: Math.round(users),
      tickets_yr: Math.round(ticketsYr),
      campuses,
      day1_techs: fieldTechs,
      tpu: Math.round(tpu * 1000) / 1000,
      role_split: { Staffed: staffed, Local: local, Remote: remote },
      role_breakdown: roleBreakdown,
      overlays: {
        field_techs: fieldTechs,
        leads,
        managers,
        tech_bars: 0,
        depot_techs: 0,
        virtual_techs: 0,
        total_people: Math.round((fieldTechs + leads + managers) * 10) / 10,
      },
      settings_subset: {
        working_days: 252,
        utilization: 0.85,
        team_floor: 2,
        physical_touch_share: 0.35,
        day_one_reach: 0.55,
        staging_radius_miles: 25,
        drive_minutes: 60,
        avg_drive_speed_mph: 40,
        remote_max_tpd: 1.2,
      },
      gap_vs_engine: [
        "No full demand/dispatch/cost cash ladder (engine cost.py / workbook).",
        "day1_techs uses mapper hint (tpd/8) not full throughput + campus floors.",
        "No OEM / shipment / depot unit economics from engine defaults.",
        "Geocode only if lat/lon present in file (Nominatim optional on map page).",
      ],
    };
  }

  function buildDealPack(mapped, summary, opts = {}) {
    return {
      dealLabel: sanitizeDealLabel(opts.dealLabel || "Sample"),
      createdAt: new Date().toISOString(),
      source: "browser-sandbox-v1",
      rules_version: DEFAULT_RULES.rules_version,
      sites: mapped.map((r) => ({
        site_id: r.site_id,
        site_name: r.site_name,
        city: r.city || "",
        state_province: r.state_province || "",
        country: r.country === "_GLOBAL_" ? "" : r.country,
        latitude: r.latitude,
        longitude: r.longitude,
        users: r.users,
        seat_count: r.seat_count,
        tickets_per_day: r.tickets_per_day,
        tickets_per_year: r.tickets_per_year,
        mapped_role: r.mapped_role,
        is_hub: r.is_hub,
        campus_id: r.campus_id,
        hub_site_id: r.hub_site_id,
        distance_to_hub_miles: r.distance_to_hub_miles,
        est_drive_minutes: r.est_drive_minutes,
        day1_techs_hint: r.day1_techs_hint,
        exception_flags: r.exception_flags,
      })),
      summary,
    };
  }

  function sanitizeDealLabel(label) {
    const raw = String(label || "Sample")
      .replace(/[<>:"/\\|?*\x00-\x1f]/g, "")
      .trim()
      .slice(0, 48);
    return raw || "Sample";
  }

  function saveDeal(pack) {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(pack));
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(pack));
    } catch (_) {
      /* quota */
    }
    return pack;
  }

  function loadDeal() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY) || localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (_) {
      return null;
    }
  }

  function clearDeal() {
    sessionStorage.removeItem(STORAGE_KEY);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_) {}
  }

  async function parseWorkbookArrayBuffer(buf, opts = {}) {
    const rules = { ...DEFAULT_RULES, ...(opts.rules || {}) };
    const workbook = XLSX.read(buf, { type: "array" });
    const preferred = opts.preferredSheets || [
      "VC_Mapped_Sites",
      "Cost_Model_Load",
      "VC_Site_Input_Template",
      "Sites",
      "sites",
    ];
    const { sheetName, rows } = sheetToObjects(workbook, preferred);
    if (!rows.length) throw new Error("No data rows found in workbook");
    const mapped = assignRoles(rows, rules);
    const summary = buildSummary(mapped, { dealLabel: opts.dealLabel });
    const pack = buildDealPack(mapped, summary, opts);
    pack.sheet_used = sheetName;
    return pack;
  }

  function costModelLoadCsv(pack) {
    const headers = [
      "Site",
      "Country",
      "City",
      "State",
      "Latitude",
      "Longitude",
      "TicketsYr",
      "Users",
      "Seats",
      "mapped_role",
      "campus_id",
      "day1_techs_hint",
    ];
    const esc = (v) => {
      const s = v == null ? "" : String(v);
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const lines = [headers.join(",")];
    for (const r of pack.sites || []) {
      lines.push(
        [
          r.site_name || r.site_id,
          r.country,
          r.city,
          r.state_province,
          r.latitude,
          r.longitude,
          r.tickets_per_year,
          r.users,
          r.seat_count,
          r.mapped_role,
          r.campus_id,
          r.day1_techs_hint,
        ]
          .map(esc)
          .join(",")
      );
    }
    return lines.join("\n");
  }

  /** Built-in sample (matches generic mapped template geography — no customer PII). */
  function sampleSites() {
    return [
      {
        site_id: "RDA-ATL-01",
        site_name: "Reference Deal A — Atlanta HQ",
        city: "Atlanta",
        state_province: "GA",
        country: "USA",
        latitude: 33.759,
        longitude: -84.388,
        users: 420,
        seat_count: 400,
        tickets_per_day: 4.2,
      },
      {
        site_id: "RDA-ATL-02",
        site_name: "Reference Deal A — Midtown Satellite",
        city: "Atlanta",
        state_province: "GA",
        country: "USA",
        latitude: 33.784,
        longitude: -84.39,
        users: 85,
        seat_count: 80,
        tickets_per_day: 0.9,
      },
      {
        site_id: "RDA-CHI-01",
        site_name: "Reference Deal A — Chicago Loop",
        city: "Chicago",
        state_province: "IL",
        country: "USA",
        latitude: 41.8789,
        longitude: -87.6359,
        users: 210,
        seat_count: 200,
        tickets_per_day: 2.5,
      },
      {
        site_id: "RDA-BOI-01",
        site_name: "Reference Deal A — Boise Remote",
        city: "Boise",
        state_province: "ID",
        country: "USA",
        latitude: 43.615,
        longitude: -116.2023,
        users: 18,
        seat_count: 16,
        tickets_per_day: 0.3,
      },
      {
        site_id: "RDA-LON-01",
        site_name: "Reference Deal A — London Docklands",
        city: "London",
        country: "United Kingdom",
        latitude: 51.5048,
        longitude: -0.0195,
        users: 150,
        seat_count: 140,
        tickets_per_month: 55,
      },
    ];
  }

  function runSample(dealLabel) {
    const mapped = assignRoles(sampleSites(), DEFAULT_RULES);
    const summary = buildSummary(mapped, { dealLabel: dealLabel || "Sample" });
    return saveDeal(buildDealPack(mapped, summary, { dealLabel: dealLabel || "Sample" }));
  }

  window.SSSandbox = {
    STORAGE_KEY,
    DEFAULT_RULES,
    haversineMiles,
    withinLocalRange,
    assignRoles,
    buildSummary,
    buildDealPack,
    parseWorkbookArrayBuffer,
    saveDeal,
    loadDeal,
    clearDeal,
    sanitizeDealLabel,
    costModelLoadCsv,
    runSample,
    sampleSites,
    allocateRoleLanes,
  };
})();
