# Site Services Deal Engine

Customer-name-free Python + Excel engine for virtual-campus staffing and generic cost modeling.

## Quick start

```bash
python3 -m venv engine/.venv
engine/.venv/bin/pip install -r requirements.txt
engine/.venv/bin/python -m engine init-template -o samples/intake_template.xlsx
engine/.venv/bin/python -m engine run samples/intake_template.xlsx -o samples/out/Deal_Output.xlsx
cp samples/out/Deal_Output.json assets/engine-summary.json
```

Outputs:
- `Deal_Output.xlsx` — Dashboard, VC Plan, Site Roster, Staffing, Overlays, Dispatch, Cost, Scenarios, Cash, Ops, Data Quality, Assumptions
- `Deal_Output.json` — summary for `/cost-model` (generic) or `/cost-model-deal-a` (publish Deal A as `/assets/engine-summary-deal-a.json`)

## Demand rules
1. `TicketsYr` if present  
2. Else `Users`/`Seats` × `estate_tickets_per_user`  
3. Else `Devices` × `estate_tickets_per_device`  
4. Else placeholder (flagged low confidence)

Sites without coordinates are never auto-Local/Staffed by distance.

## Settings
Edit the `Settings` sheet in the intake workbook, or `engine/defaults/parameters.json`.

## Methodology
See `engine/defaults/methodology.md` and `engine/defaults/ops_kpis.json`.

## Footprint map
Shared visual asset: `/assets/maps/footprint-map.png`
