from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from .config import default_ops_kpis, num


def build_ops_dashboard(
    sites: pd.DataFrame,
    vc_plan: pd.DataFrame,
    staffing_summary: Dict[str, Any],
    settings: Dict[str, Any],
) -> Dict[str, Any]:
    """Design-time ops QA metrics inspired by Reference Deal F (no live ITSM required)."""
    kpis = default_ops_kpis()
    days = num(settings, "working_days", 252)
    field = int(staffing_summary["overlays"]["field_techs"])
    tickets = float(staffing_summary.get("tickets_yr") or 0)
    avg_daily = tickets / max(days, 1)
    # Healthy open inventory ~ DOH target × daily close capacity
    doh_target = float(kpis.get("doh_green_max", 1.5))
    healthy_open = avg_daily * doh_target
    prod_target = float(kpis.get("productivity_closed_per_tech_day_target", 5))
    capacity_daily = field * prod_target * num(settings, "utilization", 0.85)

    # Volume vs staff share by VC
    rows: List[Dict[str, Any]] = []
    total_tix = float(vc_plan["TicketsYr"].sum()) if len(vc_plan) else 0.0
    total_team = float(vc_plan["Team"].sum()) if len(vc_plan) else 0.0
    for _, r in vc_plan.iterrows():
        vol_share = (float(r["TicketsYr"]) / total_tix) if total_tix else 0.0
        staff_share = (float(r["Team"]) / total_team) if total_team else 0.0
        gap = staff_share - vol_share
        rows.append({
            "VC": r["VC"],
            "Region": r["Region"],
            "TicketsYr": int(r["TicketsYr"]),
            "Team": int(r["Team"]),
            "VolumeShare": round(vol_share, 4),
            "StaffShare": round(staff_share, 4),
            "Gap": round(gap, 4),
            "Flag": "overstaffed vs volume" if gap > 0.08 else ("understaffed vs volume" if gap < -0.08 else "balanced"),
        })

    conf = sites["DemandConfidence"].value_counts().to_dict() if "DemandConfidence" in sites.columns else {}
    role = sites["Role"].value_counts().to_dict() if "Role" in sites.columns else {}

    return {
        "kpis": kpis,
        "summary": {
            "tickets_yr": int(tickets),
            "avg_daily_tickets": round(avg_daily, 2),
            "field_techs": field,
            "daily_close_capacity": round(capacity_daily, 2),
            "capacity_vs_demand": round(capacity_daily / avg_daily, 2) if avg_daily else None,
            "doh_target": doh_target,
            "healthy_open_inventory": round(healthy_open, 1),
            "incident_share_assumed": num(settings, "incident_share", 0.5),
            "slo_target": kpis.get("slo_target", 0.95),
            "demand_confidence_counts": conf,
            "role_counts": role,
        },
        "staffing_gap_by_vc": pd.DataFrame(rows),
        "notes": [
            "DOH/aging/SLO tabs are design targets until a live ticket extract is supplied.",
            "Productivity uses closed/tech/day target from ops_kpis.json.",
            "Staffing gap compares VC headcount share to ticket volume share.",
            "Calibrate incident_share from ITSM Ticket Type when available.",
        ],
    }
