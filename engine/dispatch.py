from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd

from .config import num


def _region_cost(settings: Dict[str, Any], region: str, kind: str) -> float:
    key = f"{kind}_cost_{region}"
    fallback = {
        "dispatch": num(settings, "smart_hands_dispatch_cost", 165),
        "shipment": num(settings, "cost_per_shipment", 38),
    }[kind]
    return num(settings, key, fallback)


def compute_dispatch(sites: pd.DataFrame, settings: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Variable dispatch/shipment economics by site role and region."""
    inc_share = num(settings, "incident_share", 0.5)
    d_inc = num(settings, "dispatch_rate_incident_remote", 0.12)
    d_req = num(settings, "dispatch_rate_request_remote", 0.35)
    s_inc = num(settings, "shipment_rate_incident", 0.18)
    s_req = num(settings, "shipment_rate_request", 0.45)

    rows = []
    for _, r in sites.iterrows():
        tix = float(r["TicketsYr"])
        incidents = tix * inc_share
        requests = tix * (1 - inc_share)
        remote = str(r.get("Role")) == "Remote"
        dispatches = (incidents * d_inc + requests * d_req) if remote else 0.0
        shipments = incidents * s_inc + requests * s_req
        region = str(r.get("Region") or "EMEA")
        d_cost = dispatches * _region_cost(settings, region, "dispatch")
        s_cost = shipments * _region_cost(settings, region, "shipment")
        rows.append({
            "Site": r["Site"],
            "Region": region,
            "Country": r.get("Country", ""),
            "VC": r.get("VCkey", ""),
            "Role": r.get("Role", ""),
            "TicketsYr": int(round(tix)),
            "DispatchesYr": round(dispatches, 1),
            "ShipmentsYr": round(shipments, 1),
            "DispatchCost": round(d_cost, 0),
            "ShipmentCost": round(s_cost, 0),
            "TotalVarCost": round(d_cost + s_cost, 0),
        })

    detail = pd.DataFrame(rows)
    by_region = (
        detail.groupby("Region", dropna=False)
        .agg(
            sites=("Site", "count"),
            tickets=("TicketsYr", "sum"),
            dispatches=("DispatchesYr", "sum"),
            shipments=("ShipmentsYr", "sum"),
            dispatch_cost=("DispatchCost", "sum"),
            shipment_cost=("ShipmentCost", "sum"),
            total=("TotalVarCost", "sum"),
        )
        .reset_index()
        if len(detail)
        else pd.DataFrame()
    )
    summary = {
        "dispatch_events": float(detail["DispatchesYr"].sum()) if len(detail) else 0.0,
        "shipment_events": float(detail["ShipmentsYr"].sum()) if len(detail) else 0.0,
        "dispatch_cost": float(detail["DispatchCost"].sum()) if len(detail) else 0.0,
        "shipment_cost": float(detail["ShipmentCost"].sum()) if len(detail) else 0.0,
        "total_variable": float(detail["TotalVarCost"].sum()) if len(detail) else 0.0,
        "by_region": by_region,
    }
    return detail, summary
