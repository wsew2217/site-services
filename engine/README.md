# Site Services Deal Engine

Customer-name-free Python + Excel engine for virtual-campus staffing and generic cost modeling.

## What this tool does

There is **one** deal tool in this repo: the **Python deal engine** (`python -m engine …`).

| Need | Where it lives |
|------|----------------|
| Latitude / Longitude + Campus vs Local vs Remote | Catchment / staffing in the engine (`python -m engine run …`) |
| Excel output workbook | Same engine (workbook writer) |
| JSON summary / sidecar | Same engine (`--json` or default `.json` next to the Excel out) |

There is **no** separate geo GUI. Geocode addresses externally, put **Latitude** / **Longitude** on the Sites sheet, then run the engine.

## Quick start

```bash
python3 -m venv engine/.venv
engine/.venv/bin/pip install -r requirements.txt
engine/.venv/bin/python -m engine init-template -o samples/intake_template.xlsx
engine/.venv/bin/python -m engine run samples/intake_template.xlsx -o samples/out/Deal_Output.xlsx
# optional JSON:
engine/.venv/bin/python -m engine run path/to/intake.xlsx -o Deal_Output.xlsx --json Deal_Output.json
```

### Blank intake template

```bash
engine/.venv/bin/python -m engine init-template -o samples/intake_template.xlsx
```

Produces a blank Sites sheet with these headers:

`Site`, `Country`, `Region`, `City`, `State`, `Address`, `PostalCode`, `Latitude`, `Longitude`, `TicketsYr`, `Users`, `Seats`, `Devices`, `DepotHub`, `Customs`, `CustomerStaffed`, `CoverageClass`, `Critical24x7`, `SpaceNeeded`, `Zone`, `Notes`

Also includes Settings (defaults from `engine/defaults/parameters.json`) and CountryPolicy starter rows.

Outputs:
- `Deal_Output.xlsx` — Dashboard, VC Plan, Site Roster, Staffing, Overlays, Dispatch, Cost, Scenarios, Cash, Ops, Data Quality, Assumptions
- `Deal_Output.json` — summary for `/cost-model` (generic) or `/cost-model-deal-a` (publish Deal A as `/assets/engine-summary-deal-a.json`)

## Catchment rules (Staffed / Local / Remote)

Local range (inclusive OR): haversine miles ≤ `staging_radius_miles` (25) **or** estimated drive minutes ≤ `drive_minutes` (60) at `avg_drive_speed_mph` (40 → ~40 miles for the 1-hour limb). The engine takes the more inclusive bound.

1. **Hub / campus** — highest-volume catchment within local range (primary Staffed hub).
2. **Near a campus** → always **Local** (never Remote + dispatch).
3. **Remote + dispatch** only when tickets/day **&lt; `remote_max_tpd` (1.2)** and **outside** local range of every campus.
4. **Far** and **≥ 1.2 tpd** → promote to **Staffed** campus (additional hub), not Remote.

`drive_radius_km` is legacy/unused. `single_tech_threshold` remains a **team-sizing** exception only (not the remote gate).

## Demand rules
1. `TicketsYr` if present  
2. Else `Users`/`Seats` × `estate_tickets_per_user`  
3. Else `Devices` × `estate_tickets_per_device`  
4. Else placeholder (flagged low confidence)

Sites without coordinates are never auto-Local/Staffed by distance.

## Settings
Edit the `Settings` sheet in the intake workbook, or `engine/defaults/parameters.json`.

## Methodology
See `engine/defaults/methodology.md`, `engine/defaults/ops_kpis.json`, and `engine/defaults/field_services_delivery_metrics.md`.

## Footprint map
Shared visual asset: `/assets/maps/footprint-map.png`

## Cost model how-tos
Each interactive cost page has a **Guide** tab (purpose, inputs, method, how to use, what not to confuse):
- `/cost-model#pane-guide` — generic Site Services
- `/cost-model-deal-a#pane-guide` — Reference Deal A campus estate
- `/cost-model-deal-b#pane-guide` — Reference Deal B tech-bar pattern
