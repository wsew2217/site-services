from __future__ import annotations

from math import ceil
from typing import Any, Dict, List

from .config import num


def _ceil(x: float) -> int:
    return int(ceil(x)) if x > 0 else 0


def scenario_ladder(settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {"key": "cur", "name": "Current state", "ratio": None, "defl": 0, "zt": 10, "year": None},
        {"key": "day1", "name": "Day one (demand model)", "ratio": None, "defl": 0, "zt": 15, "year": 0},
        {"key": "r750", "name": "750:1 goal", "ratio": 750, "defl": 12, "zt": 40, "year": 2, "goal": True},
        {"key": "r1000", "name": "1000:1 stretch", "ratio": 1000, "defl": 20, "zt": 60, "year": 4},
        {"key": "r1200", "name": "1200:1", "ratio": 1200, "defl": 26, "zt": 75, "year": 5},
        {"key": "r1500", "name": "1500:1 art of possible", "ratio": 1500, "defl": 32, "zt": 90, "year": 6},
    ]


def compute_cost(
    staffing_summary: Dict[str, Any],
    dispatch_summary: Dict[str, Any],
    settings: Dict[str, Any],
) -> Dict[str, Any]:
    """Estate cost + scenario ladder. Day-one uses throughput; ratios are guardrails only."""
    users = max(float(staffing_summary.get("users") or 0), 1.0)
    tickets_base = float(staffing_summary.get("tickets_yr") or users * num(settings, "estate_tickets_per_user", 1.6))
    camps = max(int(staffing_summary.get("vcs") or 1), 1)
    day1_field = int(staffing_summary["overlays"]["field_techs"])
    days = num(settings, "working_days", 252)
    touch = num(settings, "physical_touch_share", 0.35)
    onrate = (
        num(settings, "onsite_incident_rate", 6) * num(settings, "incident_share", 0.5)
        + num(settings, "onsite_request_rate", 4) * (1 - num(settings, "incident_share", 0.5))
    )
    remrate = num(settings, "remote_rate", 5)
    util = num(settings, "utilization", 0.85)
    floor = num(settings, "team_floor", 2)
    lead_span = num(settings, "lead_span", 10)
    mgr_span = num(settings, "mgr_span", 24)
    burden = 1 + num(settings, "burden_uplift", 0.28)
    leadx = num(settings, "lead_premium", 1.25)
    mgrsal = num(settings, "mgr_salary", 140000)
    labor = staffing_summary.get("labor", {})
    blended = (labor.get("tech_cost", 0) / day1_field) if day1_field else (
        (
            num(settings, "rate_NAM", 85000)
            + num(settings, "rate_LATAM", 42000)
            + num(settings, "rate_EMEA", 72000)
            + num(settings, "rate_APJC", 40000)
        )
        / 4
    )

    cov = num(settings, "day_one_reach", 0.55)
    exp = num(settings, "reach_decay_exponent", 0.6)
    ship = num(settings, "cost_per_shipment", 38)
    shipshare = num(settings, "parts_shipment_share", 0.55)
    depots = max(1, int(round(camps * num(settings, "depots_per_campus_share", 0.64))))
    depfix = num(settings, "depot_fixed_cost", 60000)
    depvar = num(settings, "depot_variable_per_shipment", 6)
    stockval = num(settings, "stock_value_per_campus", 45000)
    carry = num(settings, "stock_carrying_cost", 0.18)
    dispatch_u = num(settings, "smart_hands_dispatch_cost", 165)
    oem = num(settings, "oem_attach_share", 0.45)
    oemcost = num(settings, "oem_cost_per_incident", 55)
    bfix = num(settings, "break_fix_share", 0.6)
    dpu = num(settings, "devices_per_user", 1.2)
    refresh = num(settings, "refresh_cycle_years", 4)
    zt_ceil = num(settings, "zero_touch_ceiling", 0.85)
    rtouch = num(settings, "refresh_touch_cost", 95)
    rship = num(settings, "refresh_shipping_cost", 24)
    curtech = num(settings, "current_field_techs", max(day1_field, 1))
    curmgmt = num(settings, "current_mgmt_overhead", 0.16)
    curlog = num(settings, "current_logistics_spend", 900000)
    sev = num(settings, "severance_per_exit", 30000)
    hire = num(settings, "hire_train_per_add", 12000)
    par = num(settings, "parallel_run_months", 2)
    pmo = num(settings, "program_mgmt_per_step", 150000)
    ramp = num(settings, "step_year_ramp", 0.6)
    warranty_credit_u = num(settings, "warranty_labor_credit_per_event", 0)
    on_call_on = bool(num(settings, "on_call_enabled", 0))
    on_call_day = num(settings, "on_call_cost_per_tech_day", 85)
    hours_tm = num(settings, "hours_per_year_tm", 2080)
    oppm = num(settings, "oppm_hourly_multiplier", 1.5)
    partner_disp_cost = float(dispatch_summary.get("partner_dispatch_cost") or 0)

    # Prefer site-derived dispatch when available for day-one logistics baseline
    site_disp = float(dispatch_summary.get("dispatch_cost") or 0)
    site_ship = float(dispatch_summary.get("shipment_cost") or 0)

    def techs_for(sc: Dict[str, Any]) -> int:
        if sc["key"] == "cur":
            return int(curtech)
        tickets = tickets_base * (1 - sc["defl"] / 100)
        if sc["key"] == "day1":
            return max(day1_field, int(camps * floor))
        # Roadmap rungs: ratio is a guardrail target, still floored by campus resilience
        return max(int(camps * max(1, floor - 1)), _ceil(users / sc["ratio"]))

    def cost_for(sc: Dict[str, Any]) -> Dict[str, Any]:
        techs = techs_for(sc)
        tickets = tickets_base * (1 - sc["defl"] / 100)
        leads = 0 if sc["key"] == "cur" else _ceil(techs / lead_span)
        mgrs = 0 if sc["key"] == "cur" else _ceil(techs / mgr_span)
        tech_cost = techs * blended * burden
        mgmt_cost = (
            tech_cost * curmgmt
            if sc["key"] == "cur"
            else leads * blended * leadx * burden + mgrs * mgrsal * burden
        )

        touches = tickets * touch
        day1_t = max(day1_field, 1)
        fp = min(1.0, techs / day1_t)
        reach = min(1.0, cov * (fp ** exp))
        cap = techs * 0.6 * onrate * days * util
        covered = min(touches * reach, cap)
        uncovered = max(0.0, touches - covered)
        bfix_un = uncovered * bfix
        other_un = uncovered - bfix_un
        oem_events = bfix_un * oem
        dispatch_events = (bfix_un - oem_events) + other_un
        oem_cost = oem_events * oemcost
        disp_cost = dispatch_events * dispatch_u

        shipments = touches * shipshare
        ship_cost = shipments * ship
        depot_cost = depots * depfix + shipments * depvar
        stock_cost = camps * stockval * carry * (0.6 + 0.4 * fp)

        refresh_units = users * dpu / max(1.0, refresh)
        zt_share = min(1.0, (sc["zt"] / 100.0) * (zt_ceil if zt_ceil else 0.85))
        r_cost = refresh_units * (rship + (1 - zt_share) * rtouch)

        partner_cost = 0.0
        if sc["key"] == "cur":
            ship_cost, depot_cost, stock_cost = curlog, 0.0, 0.0
            disp_cost, oem_cost = 0.0, 0.0
            r_cost = refresh_units * (rship + 0.9 * rtouch)
        elif sc["key"] == "day1" and (site_disp or site_ship):
            # Blend site-derived dispatch/shipment into day-one for realism
            disp_cost = site_disp
            ship_cost = site_ship
            partner_cost = partner_disp_cost

        on_call_cost = (techs * on_call_day * days) if on_call_on and sc["key"] != "cur" else 0.0
        warranty_credit = tickets * warranty_credit_u if sc["key"] != "cur" else 0.0
        training_tools = techs * hire * 0.15 if sc["key"] not in {"cur"} else 0.0  # ongoing tools share of hire/train

        # Partner share is a category split of site-derived dispatch (already in disp_cost for day1)
        logistics = ship_cost + depot_cost + stock_cost + r_cost + disp_cost + oem_cost
        badged_disp = max(0.0, disp_cost - partner_cost) if sc["key"] == "day1" else disp_cost
        categories = {
            "labor": round(tech_cost, 0),
            "management": round(mgmt_cost, 0),
            "dispatch": round(badged_disp, 0),
            "partner_dispatch": round(partner_cost if sc["key"] == "day1" else 0.0, 0),
            "shipment": round(ship_cost, 0),
            "depot": round(depot_cost, 0),
            "stock": round(stock_cost, 0),
            "refresh": round(r_cost, 0),
            "oem": round(oem_cost, 0),
            "on_call": round(on_call_cost, 0),
            "training_tools": round(training_tools, 0),
            "warranty_credit": round(-warranty_credit, 0),
        }
        total = (
            tech_cost + mgmt_cost + logistics + on_call_cost + training_tools - warranty_credit
        )
        hourly = (blended * burden) / hours_tm if hours_tm else 0.0
        return {
            "techs": techs,
            "leads": leads,
            "mgrs": mgrs,
            "techCost": round(tech_cost, 0),
            "mgmtCost": round(mgmt_cost, 0),
            "shipCost": round(ship_cost, 0),
            "depotCost": round(depot_cost, 0),
            "stockCost": round(stock_cost, 0),
            "rCost": round(r_cost, 0),
            "dispCost": round(disp_cost, 0),
            "oemCost": round(oem_cost, 0),
            "onCallCost": round(on_call_cost, 0),
            "warrantyCredit": round(warranty_credit, 0),
            "logistics": round(logistics, 0),
            "total": round(total, 0),
            "ratioImplied": int(round(users / techs)) if techs else 0,
            "perSeat": round(total / users, 2) if users else 0,
            "perEvent": round(total / tickets, 2) if tickets else 0,
            "tmHourly": round(hourly, 2),
            "oppmHourly": round(hourly * oppm, 2),
            "categories": categories,
        }

    scenarios = []
    for sc in scenario_ladder(settings):
        scenarios.append({"sc": sc, "c": cost_for(sc)})

    # Cash / payback 7 years
    cur_total = scenarios[0]["c"]["total"]
    path = [scenarios[1]] + [s for s in scenarios[2:] if s["sc"].get("year") is not None]
    path = sorted(path, key=lambda s: s["sc"]["year"])
    steps = []
    prev = scenarios[0]
    for s in path:
        exits = max(0, prev["c"]["techs"] - s["c"]["techs"])
        hires = max(0, s["c"]["techs"] - prev["c"]["techs"])
        one_off = exits * sev + hires * hire + par * (prev["c"]["techCost"] / 12) * 0.25 + pmo
        steps.append({
            "from": prev["sc"]["name"],
            "to": s["sc"]["name"],
            "year": s["sc"]["year"],
            "exits": exits,
            "hires": hires,
            "oneOff": round(one_off, 0),
            "annual": s["c"]["total"],
        })
        prev = s

    pts = []
    active_annual = cur_total
    cum = 0.0
    tot_one = 0.0
    payback = None
    for y in range(0, 8):
        step_now = [s for s in steps if s["year"] == y]
        for s in step_now:
            cum -= s["oneOff"]
            tot_one += s["oneOff"]
            active_annual = s["annual"]
        if y > 0:
            factor = ramp if any(s["year"] == y for s in steps) else 1.0
            cum += (cur_total - active_annual) * factor
        pts.append(round(cum, 0))
        if payback is None and cum > 0 and y > 0:
            payback = y

    day1_labor = staffing_summary.get("labor", {}).get("total", scenarios[1]["c"]["techCost"])
    day1 = scenarios[1]["c"]
    warnings = []
    band = num(settings, "volume_change_band", 0.05)
    validity = int(num(settings, "cost_validity_days", 90))
    warnings.append(f"Refresh commercial rates within {validity} days of customer use.")
    warnings.append(f"Volume change-order band ±{int(band * 100)}% (structure from PFS; enforce in SOW).")
    if warranty_credit_u == 0:
        warnings.append("Warranty labor credit is 0 — set per OEM program when known.")
    if not on_call_on:
        warnings.append("On-call line disabled — enable when 24×7 coverage is contracted.")

    return {
        "blended_salary": round(blended, 0),
        "day1_labor_from_sites": round(day1_labor, 0),
        "depots": depots,
        "scenarios": scenarios,
        "steps": steps,
        "cash": {"points": pts, "payback_year": payback, "total_one_time": round(tot_one, 0), "year7_net": pts[-1]},
        "day1_categories": day1.get("categories", {}),
        "unit_economics": {
            "per_seat": day1.get("perSeat"),
            "per_event": day1.get("perEvent"),
            "tm_hourly": day1.get("tmHourly"),
            "oppm_hourly": day1.get("oppmHourly"),
        },
        "warnings": warnings,
        "rate_policy": "Modern placeholders only; Reference Deals G–I inform structure, not 2012 dollars.",
        "web_inputs": {
            "sites": staffing_summary.get("sites"),
            "users": staffing_summary.get("users"),
            "tickets_yr": staffing_summary.get("tickets_yr"),
            "campuses": camps,
            "day1_techs": day1_field,
            "tpu": round(tickets_base / users, 3) if users else num(settings, "estate_tickets_per_user", 1.6),
        },
    }
