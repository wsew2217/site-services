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
    """Variable dispatch/shipment economics by site role and region.

    Structure from Cost Model v2 + Reference Deals G–I (partner remote split, SLA urgency).
    Dollar rates come from modern Settings placeholders — never legacy 2012 tables.
    """
    inc_share = num(settings, "incident_share", 0.5)
    d_inc = num(settings, "dispatch_rate_incident_remote", 0.12)
    d_req = num(settings, "dispatch_rate_request_remote", 0.35)
    s_inc = num(settings, "shipment_rate_incident", 0.18)
    s_req = num(settings, "shipment_rate_request", 0.45)
    partner_share = min(max(num(settings, "partner_remote_share", 0.25), 0.0), 1.0)
    badged_share = min(max(num(settings, "badged_share", 0.99), 0.0), 1.0)
    urgency = num(settings, "sla_dispatch_urgency", 1.15)
    fast_sla = (
        num(settings, "sla_mix_2h", 0.10) + num(settings, "sla_mix_4h", 0.20)
    )
    spares_flag = bool(num(settings, "fast_sla_spares_flag", 1)) and fast_sla >= 0.25

    # Estate SLA mix intensifies remote dispatch probability (structure only)
    urgency_factor = 1.0 + (urgency - 1.0) * (num(settings, "sla_mix_2h", 0.10) + 0.5 * num(settings, "sla_mix_4h", 0.20))

    rows = []
    for _, r in sites.iterrows():
        tix = float(r["TicketsYr"])
        incidents = tix * inc_share
        requests = tix * (1 - inc_share)
        remote = str(r.get("Role")) == "Remote"
        critical = bool(r.get("Critical24x7Flag"))
        dispatches = (incidents * d_inc + requests * d_req) * urgency_factor if remote else 0.0
        shipments = incidents * s_inc + requests * s_req
        if critical and spares_flag:
            shipments *= 1.1  # fast SLA / 24x7 → more stocked parts movement
        region = str(r.get("Region") or "EMEA")
        unit_d = _region_cost(settings, region, "dispatch")
        unit_s = _region_cost(settings, region, "shipment")

        partner_disp = dispatches * partner_share
        badged_disp = dispatches * (1.0 - partner_share) * badged_share
        # Residual non-badged / non-partner stays in badged cost lane for simplicity
        internal_disp = dispatches - partner_disp
        d_cost_partner = partner_disp * unit_d
        d_cost_badged = internal_disp * unit_d
        d_cost = d_cost_partner + d_cost_badged
        s_cost = shipments * unit_s
        rows.append({
            "Site": r["Site"],
            "Region": region,
            "Country": r.get("Country", ""),
            "VC": r.get("VCkey", ""),
            "Role": r.get("Role", ""),
            "TicketsYr": int(round(tix)),
            "DispatchesYr": round(dispatches, 1),
            "PartnerDispatchesYr": round(partner_disp, 1),
            "BadgedDispatchesYr": round(badged_disp, 1),
            "ShipmentsYr": round(shipments, 1),
            "DispatchCost": round(d_cost, 0),
            "PartnerDispatchCost": round(d_cost_partner, 0),
            "BadgedDispatchCost": round(d_cost_badged, 0),
            "ShipmentCost": round(s_cost, 0),
            "TotalVarCost": round(d_cost + s_cost, 0),
            "SparesStockFlag": "Y" if (critical and spares_flag) or (remote and spares_flag and fast_sla >= 0.25) else "",
        })

    detail = pd.DataFrame(rows)
    by_region = (
        detail.groupby("Region", dropna=False)
        .agg(
            sites=("Site", "count"),
            tickets=("TicketsYr", "sum"),
            dispatches=("DispatchesYr", "sum"),
            partner_dispatches=("PartnerDispatchesYr", "sum"),
            shipments=("ShipmentsYr", "sum"),
            dispatch_cost=("DispatchCost", "sum"),
            partner_dispatch_cost=("PartnerDispatchCost", "sum"),
            shipment_cost=("ShipmentCost", "sum"),
            total=("TotalVarCost", "sum"),
        )
        .reset_index()
        if len(detail)
        else pd.DataFrame()
    )
    summary = {
        "dispatch_events": float(detail["DispatchesYr"].sum()) if len(detail) else 0.0,
        "partner_dispatch_events": float(detail["PartnerDispatchesYr"].sum()) if len(detail) else 0.0,
        "shipment_events": float(detail["ShipmentsYr"].sum()) if len(detail) else 0.0,
        "dispatch_cost": float(detail["DispatchCost"].sum()) if len(detail) else 0.0,
        "partner_dispatch_cost": float(detail["PartnerDispatchCost"].sum()) if len(detail) else 0.0,
        "badged_dispatch_cost": float(detail["BadgedDispatchCost"].sum()) if len(detail) else 0.0,
        "shipment_cost": float(detail["ShipmentCost"].sum()) if len(detail) else 0.0,
        "total_variable": float(detail["TotalVarCost"].sum()) if len(detail) else 0.0,
        "partner_remote_share": partner_share,
        "sla_urgency_factor": round(urgency_factor, 4),
        "fast_sla_spares": spares_flag,
        "by_region": by_region,
    }
    return detail, summary
