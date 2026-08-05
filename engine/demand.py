from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd

from .config import as_bool, num


SITE_OPTIONAL = [
    "City",
    "State",
    "Address",
    "PostalCode",
    "DepotHub",
    "Customs",
    "CustomerStaffed",
    "CoverageClass",
    "Critical24x7",
    "SpaceNeeded",
    "Notes",
    "Users",
    "Seats",
    "Devices",
    "TicketsYr",
    "Latitude",
    "Longitude",
    "Zone",
]


def normalize_sites(df: pd.DataFrame, settings: Dict[str, Any]) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """Resolve demand with sparse inputs and attach data-quality flags."""
    issues: List[Dict[str, Any]] = []
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    out = out.dropna(how="all")
    if "Site" not in out.columns:
        raise ValueError("Sites sheet requires a Site column")

    for col in SITE_OPTIONAL + ["Country", "Region"]:
        if col not in out.columns:
            out[col] = "" if col not in {"Users", "Seats", "Devices", "TicketsYr", "Latitude", "Longitude"} else pd.NA

    out = out[out["Site"].notna()].copy()
    out["Site"] = out["Site"].astype(str).str.strip()
    out["Country"] = out["Country"].astype(str).str.strip().replace({"nan": "", "None": ""})
    out["Region"] = out["Region"].astype(str).str.strip().replace({"nan": "", "None": ""})
    for c in ["City", "State", "Address", "PostalCode", "DepotHub", "Customs", "CustomerStaffed",
              "CoverageClass", "Critical24x7", "SpaceNeeded", "Notes", "Zone"]:
        out[c] = out[c].astype(str).str.strip().replace({"nan": "", "None": ""})

    for c in ["TicketsYr", "Users", "Seats", "Devices", "Latitude", "Longitude"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    # Prefer Users, fall back to Seats
    out["UsersEff"] = out["Users"].where(out["Users"].notna(), out["Seats"])

    tpu = num(settings, "estate_tickets_per_user", 1.6)
    tpdv = num(settings, "estate_tickets_per_device", 0.8)
    fail_desktop = num(settings, "fail_rate_desktop", 1.6)
    fail_laptop = num(settings, "fail_rate_laptop", 1.8)
    # Blended fail-rate for seat/device bootstrap (PFS structure; modern seeds)
    fail_blend = 0.6 * fail_desktop + 0.4 * fail_laptop
    placeholder = num(settings, "placeholder_tickets_per_site", 12)
    use_fail = bool(num(settings, "use_fail_rate_bootstrap", 0))

    tickets = []
    sources = []
    confidence = []
    for i, row in out.iterrows():
        if pd.notna(row["TicketsYr"]) and float(row["TicketsYr"]) >= 0:
            tickets.append(float(row["TicketsYr"]))
            sources.append("tickets")
            confidence.append("high")
        elif use_fail and pd.notna(row["UsersEff"]) and float(row["UsersEff"]) > 0:
            tickets.append(float(row["UsersEff"]) * fail_blend)
            sources.append("seats_x_fail_rate")
            confidence.append("medium")
        elif pd.notna(row["UsersEff"]) and float(row["UsersEff"]) > 0:
            tickets.append(float(row["UsersEff"]) * tpu)
            sources.append("users_x_rate")
            confidence.append("medium")
        elif pd.notna(row["Devices"]) and float(row["Devices"]) > 0:
            tickets.append(float(row["Devices"]) * tpdv)
            sources.append("devices_x_rate")
            confidence.append("medium")
        else:
            tickets.append(placeholder)
            sources.append("placeholder")
            confidence.append("low")
            issues.append({
                "site": row["Site"],
                "level": "warn",
                "message": "No tickets/users/seats/devices; used placeholder demand",
            })

        if not row["Country"]:
            issues.append({"site": row["Site"], "level": "error", "message": "Missing Country"})
        if not row["Region"]:
            issues.append({"site": row["Site"], "level": "warn", "message": "Missing Region"})
        if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]):
            issues.append({
                "site": row["Site"],
                "level": "info",
                "message": "Missing coordinates; site cannot be Local/Staffed by distance",
            })

    out["TicketsYr"] = tickets
    out["TicketSource"] = sources
    out["DemandConfidence"] = confidence
    out["tpd"] = out["TicketsYr"] / max(num(settings, "working_days", 252), 1)

    dep = out["DepotHub"].astype(str).str.strip()
    out["VCkey"] = dep.where((dep != "") & (dep.str.lower() != "nan"), out["Country"])
    out.loc[out["VCkey"] == "", "VCkey"] = "UNASSIGNED"

    out["CustomerStaffedFlag"] = out["CustomerStaffed"].map(as_bool)
    out["CustomsFlag"] = out["Customs"].map(as_bool)
    out["Critical24x7Flag"] = out["Critical24x7"].map(as_bool)
    out["SpaceNeededFlag"] = out["SpaceNeeded"].map(as_bool)

    return out, issues
