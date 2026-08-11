"""Lightweight catchment rule checks — no customer data."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vc_mapper import (  # noqa: E402
    assign_roles,
    est_drive_minutes,
    load_yaml,
    normalize_tickets,
    within_local_range,
)


def _prep(df: pd.DataFrame, rules: dict) -> pd.DataFrame:
    working_days = float(rules.get("working_days_per_year", 252))
    months = float(rules.get("months_per_year", 12))
    tpds, tpms, tpys = [], [], []
    for _, row in df.iterrows():
        d, m, y = normalize_tickets(row, working_days, months)
        tpds.append(d)
        tpms.append(m)
        tpys.append(y)
    out = df.copy()
    out["tickets_per_day"] = tpds
    out["tickets_per_month"] = tpms
    out["tickets_per_year"] = tpys
    out["geocode_status"] = "provided"
    return out


def test_within_local_range_or_logic():
    rules = load_yaml(ROOT / "default_rules.yaml")
    assert within_local_range(10.0, rules) is True
    # 30 mi @ 40 mph ≈ 45 min → still local via minutes OR
    assert within_local_range(30.0, rules) is True
    assert est_drive_minutes(30.0, 40.0) == 45.0
    assert within_local_range(50.0, rules) is False


def test_near_staffed_always_local():
    rules = load_yaml(ROOT / "default_rules.yaml")
    df = _prep(
        pd.DataFrame(
            [
                {
                    "site_id": "H1",
                    "site_name": "Hub",
                    "latitude": 33.75,
                    "longitude": -84.39,
                    "users": 400,
                    "seat_count": 400,
                    "tickets_per_day": 4.0,
                    "tickets_per_month": None,
                    "tickets_per_year": None,
                    "country": "USA",
                    "region": "NAM",
                    "district": "SE",
                    "notes": "",
                },
                {
                    "site_id": "L1",
                    "site_name": "Near spoke",
                    "latitude": 33.78,
                    "longitude": -84.39,
                    "users": 80,
                    "seat_count": 80,
                    "tickets_per_day": 0.4,
                    "tickets_per_month": None,
                    "tickets_per_year": None,
                    "country": "USA",
                    "region": "NAM",
                    "district": "SE",
                    "notes": "",
                },
            ]
        ),
        rules,
    )
    mapped = assign_roles(df, rules, [])
    by_id = mapped.set_index("site_id")
    assert by_id.loc["H1", "mapped_role"] == "Staffed"
    assert by_id.loc["L1", "mapped_role"] == "Local"


def test_far_low_volume_remote():
    rules = load_yaml(ROOT / "default_rules.yaml")
    df = _prep(
        pd.DataFrame(
            [
                {
                    "site_id": "H1",
                    "site_name": "Hub",
                    "latitude": 33.75,
                    "longitude": -84.39,
                    "users": 400,
                    "seat_count": 400,
                    "tickets_per_day": 4.0,
                    "tickets_per_month": None,
                    "tickets_per_year": None,
                    "country": "USA",
                    "region": "NAM",
                    "district": "SE",
                    "notes": "",
                },
                {
                    "site_id": "R1",
                    "site_name": "Far small",
                    "latitude": 43.61,
                    "longitude": -116.20,
                    "users": 20,
                    "seat_count": 20,
                    "tickets_per_day": 0.3,
                    "tickets_per_month": None,
                    "tickets_per_year": None,
                    "country": "USA",
                    "region": "NAM",
                    "district": "MT",
                    "notes": "",
                },
            ]
        ),
        rules,
    )
    mapped = assign_roles(df, rules, [])
    assert mapped.set_index("site_id").loc["R1", "mapped_role"] == "Remote"
