"""Catchment / Staffed-Local-Remote assignment tests."""
from __future__ import annotations

import pandas as pd

from engine.config import default_settings
from engine.demand import normalize_sites
from engine.staffing import local_range_miles, size_estate, within_local_range


def _sites_frame(rows):
    cols = [
        "Site", "Country", "Region", "City", "State", "Address", "PostalCode",
        "Latitude", "Longitude", "TicketsYr", "Users", "Seats", "Devices",
        "DepotHub", "Customs", "CustomerStaffed", "CoverageClass", "Critical24x7",
        "SpaceNeeded", "Zone", "Notes",
    ]
    return pd.DataFrame(rows, columns=cols)


def _roles_for(rows, settings=None):
    settings = settings or default_settings()
    raw = _sites_frame(rows)
    sites, _ = normalize_sites(raw, settings)
    sized, _, _ = size_estate(sites, settings)
    return dict(zip(sized["Site"], sized["Role"]))


def test_local_range_is_inclusive_or():
    settings = default_settings()
    # 40 mph × 60 min → 40 mi; staging is 25 → inclusive max is 40
    assert local_range_miles(settings) == 40.0
    assert within_local_range(25.0, settings) is True
    assert within_local_range(35.0, settings) is True  # drive-time limb
    assert within_local_range(41.0, settings) is False


def test_near_campus_always_local_any_volume():
    """Site within local range of hub → Local regardless of ticket volume."""
    # Hub Austin; spoke ~18 mi north (Round Rock area) with low volume
    wd = 252
    roles = _roles_for([
        ["Hub Campus", "USA", "NAM", "Austin", "TX", "", "", 30.27, -97.74, 5.0 * wd, "", "", "", "", "", "", "", "", "", "", ""],
        ["Near Low", "USA", "NAM", "Round Rock", "TX", "", "", 30.51, -97.68, 0.3 * wd, "", "", "", "", "", "", "", "", "", "", ""],
        ["Near High", "USA", "NAM", "Pflugerville", "TX", "", "", 30.44, -97.62, 3.0 * wd, "", "", "", "", "", "", "", "", "", "", ""],
    ])
    assert roles["Hub Campus"] == "Staffed"
    assert roles["Near Low"] == "Local"
    assert roles["Near High"] == "Local"


def test_far_low_volume_is_remote():
    """Outside local range + tpd < 1.2 → Remote + dispatch."""
    wd = 252
    roles = _roles_for([
        ["Hub Campus", "USA", "NAM", "Austin", "TX", "", "", 30.27, -97.74, 5.0 * wd, "", "", "", "", "", "", "", "", "", "", ""],
        ["Far Thin", "USA", "NAM", "Houston", "TX", "", "", 29.76, -95.37, 0.5 * wd, "", "", "", "", "", "", "", "", "", "", ""],
    ])
    assert roles["Hub Campus"] == "Staffed"
    assert roles["Far Thin"] == "Remote"


def test_far_high_volume_promotes_to_staffed():
    """Outside local range + tpd ≥ 1.2 → Staffed campus (not Remote)."""
    wd = 252
    roles = _roles_for([
        ["Hub Campus", "USA", "NAM", "Austin", "TX", "", "", 30.27, -97.74, 5.0 * wd, "", "", "", "", "", "", "", "", "", "", ""],
        ["Far Dense", "USA", "NAM", "Houston", "TX", "", "", 29.76, -95.37, 2.0 * wd, "", "", "", "", "", "", "", "", "", "", ""],
    ])
    assert roles["Hub Campus"] == "Staffed"
    assert roles["Far Dense"] == "Staffed"


def test_near_promoted_hub_becomes_local():
    """After a far high-volume site promotes, a neighbor becomes Local."""
    wd = 252
    roles = _roles_for([
        ["Hub Campus", "USA", "NAM", "Austin", "TX", "", "", 30.27, -97.74, 5.0 * wd, "", "", "", "", "", "", "", "", "", "", ""],
        ["Houston Hub", "USA", "NAM", "Houston", "TX", "", "", 29.76, -95.37, 2.0 * wd, "", "", "", "", "", "", "", "", "", "", ""],
        ["Houston Spoke", "USA", "NAM", "Pasadena", "TX", "", "", 29.69, -95.21, 0.4 * wd, "", "", "", "", "", "", "", "", "", "", ""],
    ])
    assert roles["Hub Campus"] == "Staffed"
    assert roles["Houston Hub"] == "Staffed"
    assert roles["Houston Spoke"] == "Local"
