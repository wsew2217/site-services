from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .cost import compute_cost
from .demand import normalize_sites
from .dispatch import compute_dispatch
from .intake import read_intake, write_intake_template
from .ops import build_ops_dashboard
from .staffing import size_estate
from .workbook import write_deal_output, write_web_summary


def run_deal(intake_path: Path, output_path: Path, json_path: Path | None = None) -> Dict[str, Any]:
    sites_raw, settings, policy = read_intake(intake_path)
    sites, issues = normalize_sites(sites_raw, settings)
    if policy is not None and len(policy) and "Country" in policy.columns:
        locked = {
            str(r.Country).strip()
            for r in policy.itertuples()
            if str(getattr(r, "CustomsLocked", "")).strip().upper().startswith("Y")
        }
        mask = sites["Country"].isin(locked) & (~sites["CustomsFlag"])
        sites.loc[mask, "CustomsFlag"] = True
        sites.loc[mask, "Customs"] = "Y"
    sites, vc_plan, staffing_summary = size_estate(sites, settings)
    dispatch_detail, dispatch_summary = compute_dispatch(sites, settings)
    cost = compute_cost(staffing_summary, dispatch_summary, settings)
    ops = build_ops_dashboard(sites, vc_plan, staffing_summary, settings)
    out = write_deal_output(
        output_path,
        sites=sites,
        vc_plan=vc_plan,
        staffing_summary=staffing_summary,
        dispatch_detail=dispatch_detail,
        dispatch_summary=dispatch_summary,
        cost=cost,
        ops=ops,
        issues=issues,
        settings=settings,
    )
    jpath = Path(json_path) if json_path else Path(out).with_suffix(".json")
    write_web_summary(jpath, staffing_summary, cost, settings)
    return {
        "output": str(out),
        "json": str(jpath),
        "sites": staffing_summary["sites"],
        "vcs": staffing_summary["vcs"],
        "field_techs": staffing_summary["overlays"]["field_techs"],
        "total_people": staffing_summary["overlays"]["total_people"],
        "day1_cost": cost["scenarios"][1]["c"]["total"],
        "issues": len(issues),
    }


def make_template(path: Path) -> Path:
    return write_intake_template(path)
