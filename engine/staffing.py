from __future__ import annotations

from math import asin, ceil, cos, radians, sin, sqrt
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .config import num


def allocate_role_lanes(field_techs: int, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Split field HC across Primary lanes for reporting. Secondary/Tertiary are flex labels, not additive HC."""
    lanes = settings.get("role_lanes") or [
        "Desktop-Incident", "Desktop-Requests", "Remote-Desktop", "Staging",
        "Site-Lead", "Telecom", "Network-VDI", "Projects",
    ]
    mix = settings.get("role_lane_primary_mix") or {}
    if not isinstance(mix, dict) or not mix:
        mix = {lanes[0]: 1.0} if lanes else {}
    weights = []
    for lane in lanes:
        weights.append(max(0.0, float(mix.get(lane, 0.0))))
    total_w = sum(weights) or 1.0
    weights = [w / total_w for w in weights]

    primary_rows = []
    assigned = 0
    n = len(lanes)
    for i, lane in enumerate(lanes):
        if field_techs <= 0:
            hc = 0
        elif i < n - 1:
            hc = int(round(field_techs * weights[i]))
            assigned += hc
        else:
            hc = max(0, field_techs - assigned)
        primary_rows.append({
            "Lane": lane,
            "PrimaryHC": hc,
            "Share": round(weights[i], 4),
            "Secondary": str(settings.get("role_lane_secondary_default") or "Desktop-Requests"),
            "Tertiary": str(settings.get("role_lane_tertiary_default") or "Projects"),
        })
    # Fix rounding drift on largest lane
    drift = field_techs - sum(r["PrimaryHC"] for r in primary_rows)
    if drift and primary_rows:
        idx = max(range(len(primary_rows)), key=lambda i: primary_rows[i]["PrimaryHC"])
        primary_rows[idx]["PrimaryHC"] = max(0, primary_rows[idx]["PrimaryHC"] + drift)

    schedule = settings.get("schedule_lanes") or ["M", "TL", "T", "W", "S", "RR"]
    return {
        "note": "Primary HC is a reporting split of sized field techs. Secondary/Tertiary are flex coverage, not additive headcount.",
        "primary": primary_rows,
        "schedule_lanes": list(schedule),
        "field_techs": field_techs,
    }


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    if any(pd.isna(x) for x in [lat1, lon1, lat2, lon2]):
        return 9e9
    a, b, c, e = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    return 2 * 6371 * asin(sqrt(sin((c - a) / 2) ** 2 + cos(a) * cos(c) * sin((e - b) / 2) ** 2))


def _coverage_class(row: pd.Series, role: str) -> str:
    explicit = str(row.get("CoverageClass") or "").strip()
    if explicit:
        return explicit
    if row.get("Critical24x7Flag"):
        return "Critical 24x7"
    if role == "Staffed":
        return "Dedicated business hours"
    if role == "Local":
        return "Local drive-range"
    return "Dispatch / remote"


def size_estate(sites: pd.DataFrame, settings: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Assign hubs, classify Staffed/Local/Remote, size teams and overlays."""
    workdays = num(settings, "working_days", 252)
    drive = num(settings, "drive_radius_km", 60)
    inc_share = num(settings, "incident_share", 0.5)
    inc_rate = num(settings, "onsite_incident_rate", 6)
    req_rate = num(settings, "onsite_request_rate", 4)
    rem_rate = num(settings, "remote_rate", 5)
    util = num(settings, "utilization", 0.85)
    floor = int(num(settings, "team_floor", 2))
    low_thresh = num(settings, "single_tech_threshold", 2.5)
    per_lead = num(settings, "lead_span", 10)
    per_mgr = num(settings, "mgr_span", 24)
    tech_bar_users = num(settings, "overlay_tech_bar_threshold_users", 400)
    depot_per = int(num(settings, "overlay_depot_techs_per_depot_campus", 1))
    virtual_techs = int(num(settings, "overlay_virtual_techs", 0))
    hub_wl = num(settings, "hub_workload_threshold", 0.5)
    vac_sick = num(settings, "vac_sick_uplift", 1.15)
    travel_util = max(num(settings, "travel_utilization", 0.5), 0.15)
    floor_247 = int(num(settings, "critical_24x7_floor_techs", 2))
    sla_uplift = (
        num(settings, "sla_mix_2h", 0.10) * num(settings, "sla_uplift_2h", 0.45)
        + num(settings, "sla_mix_4h", 0.20) * num(settings, "sla_uplift_4h", 0.33)
        + num(settings, "sla_mix_nbd", 0.55) * num(settings, "sla_uplift_nbd", 0.0)
        + num(settings, "sla_mix_extended_hours", 0.15) * num(settings, "sla_uplift_extended_hours", 0.125)
    )

    df = sites.copy()
    df["dkm"] = 9e9
    df["Role"] = "Remote"
    hubs: Dict[str, Any] = {}
    vc_rows = []

    for key, sub in df.groupby("VCkey"):
        base = str(key).split("-")[0].strip()
        pool = sub[(sub["Country"] == base) & sub["Latitude"].notna() & sub["Longitude"].notna()]
        if len(pool) == 0:
            pool = sub[sub["Latitude"].notna() & sub["Longitude"].notna()]
        hub_idx = None
        hub_city = "(remote)"
        if len(pool) > 0:
            coords = pool[["Latitude", "Longitude", "tpd"]].to_numpy()
            best, best_catch, best_tpd = None, -1.0, -1.0
            for idx, row in pool.iterrows():
                catch = sum(
                    tp for (la, lo, tp) in coords
                    if haversine_km(row["Latitude"], row["Longitude"], la, lo) <= drive
                )
                if catch > best_catch or (catch == best_catch and row["tpd"] > best_tpd):
                    best, best_catch, best_tpd = idx, catch, float(row["tpd"])
            hub_idx = best
            hub_city = str(pool.loc[best, "City"] or "").strip() or str(pool.loc[best, "Site"])
            hlat, hlng = pool.loc[best, "Latitude"], pool.loc[best, "Longitude"]
            dists = [
                haversine_km(hlat, hlng, r.Latitude, r.Longitude)
                for r in sub.itertuples()
            ]
            df.loc[sub.index, "dkm"] = dists
            # Staffed = hub; Local = within drive (non-hub); Remote = rest / no coords
            for i, d in zip(sub.index, dists):
                if i == hub_idx:
                    df.at[i, "Role"] = "Staffed"
                elif d <= drive:
                    df.at[i, "Role"] = "Local"
                else:
                    df.at[i, "Role"] = "Remote"
        hubs[key] = hub_idx

        on = df.loc[sub.index][df.loc[sub.index, "Role"].isin(["Staffed", "Local"])]
        hub_sites = df.loc[sub.index][df.loc[sub.index, "Role"] == "Staffed"]
        local_sites = df.loc[sub.index][df.loc[sub.index, "Role"] == "Local"]
        rem = df.loc[sub.index][df.loc[sub.index, "Role"] == "Remote"]
        hub_tpd = float(hub_sites["tpd"].sum()) if len(hub_sites) else 0.0
        local_tpd = float(local_sites["tpd"].sum()) if len(local_sites) else 0.0
        on_tpd = float(on["tpd"].sum()) if len(on) else 0.0
        rem_tpd = float(rem["tpd"].sum()) if len(rem) else 0.0
        served = float(sub["tpd"].sum())

        def _onsite_heads(tpd: float, util_eff: float) -> int:
            if tpd <= 0 or util_eff <= 0:
                return 0
            return int(ceil((tpd * inc_share / inc_rate + tpd * (1 - inc_share) / req_rate) / util_eff))

        # Hub work at full util; Local/drive work at travel_utilization (PFS structure)
        on_t = _onsite_heads(hub_tpd, util) + _onsite_heads(local_tpd, util * travel_util)
        rem_t = int(ceil(rem_tpd / (rem_rate * util))) if rem_tpd > 0 else 0
        natural = on_t + rem_t
        # SLA mix + vac/sick uplifts (structure from G/I; rates are modern settings)
        uplifted = int(ceil(natural * (1.0 + sla_uplift) * vac_sick)) if natural > 0 else 0
        staffed_flag = bool(sub["CustomerStaffedFlag"].any())
        critical = int(sub["Critical24x7Flag"].sum())
        if uplifted <= 1 and served < low_thresh:
            team = max(1, uplifted) if uplifted > 0 else (1 if staffed_flag else 0)
        else:
            team = max(floor, uplifted) if uplifted > 0 or staffed_flag else 0
        if staffed_flag and on_t < 1 and served > 0:
            on_t = 1
            team = max(team, 1)
        if critical > 0 and team > 0:
            team = max(team, floor_247)
        if team > 0:
            # Preserve on/remote split shape after uplift
            if natural > 0:
                on_t = max(on_t, int(round(team * (on_t / natural)))) if on_t else on_t
            rem_t = max(0, team - on_t)
        else:
            rem_t = 0

        region = sub["Region"].mode().iat[0] if len(sub["Region"].mode()) else (sub["Region"].iat[0] if len(sub) else "")
        onsite_share = (on_tpd / served) if served > 0 else 0.0
        campus_mode = "Hub-led" if onsite_share >= hub_wl else "Depot-led"
        users_sum = float(pd.to_numeric(sub["UsersEff"], errors="coerce").fillna(0).sum())
        tech_bar = 1 if users_sum >= tech_bar_users and team >= floor else 0
        depot_techs = depot_per if campus_mode == "Depot-led" and team > 0 else 0

        vc_rows.append({
            "VC": str(key),
            "Region": region,
            "Hub": hub_city,
            "Countries": int(sub["Country"].nunique()),
            "StaffedSites": int((df.loc[sub.index, "Role"] == "Staffed").sum()),
            "LocalSites": int((df.loc[sub.index, "Role"] == "Local").sum()),
            "RemoteSites": int((df.loc[sub.index, "Role"] == "Remote").sum()),
            "Served": int(len(sub)),
            "WorkDay": round(served, 2),
            "TicketsYr": int(round(float(sub["TicketsYr"].sum()))),
            "Users": int(round(users_sum)),
            "OnSite": on_t,
            "Remote": rem_t,
            "Team": team,
            "CampusMode": campus_mode,
            "Customs": "Y" if bool(sub["CustomsFlag"].any()) else "",
            "Staffed": "Y" if staffed_flag else "",
            "TechBar": tech_bar,
            "DepotTechs": depot_techs,
            "CriticalSites": critical,
            "NaturalTechs": natural,
            "UpliftedTechs": uplifted,
        })

    R = pd.DataFrame(vc_rows)
    if len(R) == 0:
        R = pd.DataFrame(columns=[
            "VC", "Region", "Hub", "Countries", "StaffedSites", "LocalSites", "RemoteSites",
            "Served", "WorkDay", "TicketsYr", "Users", "OnSite", "Remote", "Team",
            "CampusMode", "Customs", "Staffed", "TechBar", "DepotTechs", "CriticalSites",
            "NaturalTechs", "UpliftedTechs",
        ])
    else:
        R = R.sort_values(["Region", "WorkDay"], ascending=[True, False]).reset_index(drop=True)

    # Coverage class on sites
    df["CoverageClassResolved"] = [
        _coverage_class(r, r["Role"]) for _, r in df.iterrows()
    ]
    df["DistKm"] = df["dkm"].replace(9e9, np.nan)

    field = int(R["Team"].sum()) if len(R) else 0
    order = {"NAM": 0, "LATAM": 1, "EMEA": 2, "APJC": 3}
    if len(R):
        by = (
            R.groupby("Region", dropna=False)
            .agg(VCs=("VC", "count"), techs=("Team", "sum"), on=("OnSite", "sum"),
                 rem=("Remote", "sum"), sites=("Served", "sum"), tix=("TicketsYr", "sum"),
                 users=("Users", "sum"))
            .reset_index()
        )
        by["o"] = by["Region"].map(lambda r: order.get(str(r), 9))
        by = by.sort_values("o").drop(columns="o").reset_index(drop=True)
        by["leads"] = by["techs"].apply(lambda t: int(ceil(t / per_lead)) if t > 0 else 0)
    else:
        by = pd.DataFrame(columns=["Region", "VCs", "techs", "on", "rem", "sites", "tix", "users", "leads"])

    leads = int(by["leads"].sum()) if len(by) else 0
    mgrs = int(ceil(field / per_mgr)) if field > 0 else 0
    tech_bars = int(R["TechBar"].sum()) if len(R) else 0
    depot_techs = int(R["DepotTechs"].sum()) if len(R) else 0
    overlays = {
        "field_techs": field,
        "leads": leads,
        "managers": mgrs,
        "tech_bars": tech_bars,
        "depot_techs": depot_techs,
        "virtual_techs": virtual_techs,
        "total_people": field + leads + mgrs + tech_bars + depot_techs + virtual_techs,
    }
    role_lanes = allocate_role_lanes(field, settings)

    rates = {
        "NAM": num(settings, "rate_NAM", 85000),
        "LATAM": num(settings, "rate_LATAM", 42000),
        "EMEA": num(settings, "rate_EMEA", 72000),
        "APJC": num(settings, "rate_APJC", 40000),
    }
    leadx = num(settings, "lead_premium", 1.25)
    mgrc = num(settings, "mgr_salary", 140000)
    if len(R):
        R["LaborCost"] = R.apply(lambda r: int(r.Team * rates.get(str(r.Region), 0)), axis=1)
        by["tech_cost"] = by.apply(lambda b: b.techs * rates.get(str(b.Region), 0), axis=1)
        by["lead_cost"] = by.apply(lambda b: b.leads * leadx * rates.get(str(b.Region), 0), axis=1)
    else:
        by["tech_cost"] = []
        by["lead_cost"] = []

    labor = {
        "tech_cost": float(by["tech_cost"].sum()) if len(by) else 0.0,
        "lead_cost": float(by["lead_cost"].sum()) if len(by) else 0.0,
        "mgr_cost": mgrs * mgrc,
    }
    labor["total"] = labor["tech_cost"] + labor["lead_cost"] + labor["mgr_cost"]

    summary = {
        "sites": int(len(df)),
        "tickets_yr": int(round(float(df["TicketsYr"].sum()))),
        "users": int(round(float(pd.to_numeric(df["UsersEff"], errors="coerce").fillna(0).sum()))),
        "countries": int(df["Country"].nunique()),
        "vcs": int(len(R)),
        "overlays": overlays,
        "role_lanes": role_lanes,
        "labor": labor,
        "by_region": by,
        "settings_echo": {
            "working_days": workdays,
            "drive_radius_km": drive,
            "incident_share": inc_share,
            "onsite_incident_rate": inc_rate,
            "onsite_request_rate": req_rate,
            "remote_rate": rem_rate,
            "utilization": util,
            "team_floor": floor,
            "single_tech_threshold": low_thresh,
            "lead_span": per_lead,
            "mgr_span": per_mgr,
            "vac_sick_uplift": vac_sick,
            "travel_utilization": travel_util,
            "sla_uplift_weighted": round(sla_uplift, 4),
            "critical_24x7_floor_techs": floor_247,
        },
    }
    return df, R, summary
