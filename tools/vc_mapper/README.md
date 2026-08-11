# Site Services VC Mapper

Local Python package that maps site intake into Hub / Local / Remote roles and a `Cost_Model_Load` sheet for the suite cost model / deal engine.

## In this repo

```
tools/vc_mapper/
  requirements.txt
  default_rules.yaml
  column_aliases.yaml
  vc_mapper.py
  build_template.py
  cost_model_bridge.py
  normalize_pilot.py   # Desktop pilot helper — keep customer files off git
  README.md
  vc_template_pack_v1_0.xlsx
  tests/
```

Suite docs + downloads: `/vc-kit` (static pages) and `/assets/vc-kit/`.

Optional Mac working copy: `~/Desktop/site_services_vc_mapper/`  
Governed storage: `~/Desktop/Site Services Solutioning/`

## Setup (Mac)

```bash
cd tools/vc_mapper   # or ~/Desktop/site_services_vc_mapper
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

## Build / refresh template

```bash
python3 build_template.py
```

## Run mapper

```bash
python3 vc_mapper.py \
  --input vc_template_pack_v1_0.xlsx \
  --output vc_template_pack_v1_0_mapped.xlsx \
  --operator-name "Your Name"
```

Optional: `--skip-geocode` when latitude/longitude are already present (or to avoid Nominatim).

## Cost_Model_Load → engine

```bash
python3 cost_model_bridge.py \
  --input vc_template_pack_v1_0_mapped.xlsx \
  --sites-out engine_sites.xlsx \
  --json-out bridge.json

# Prefer full engine for /cost-model:
python -m engine run engine_sites.xlsx -o Deal_Output.xlsx
```

`bridge.json` is a rough sandbox summary only — not a priced proposal.

## Catchment rules (v1)

Aligned with `default_rules.yaml` and the site suite engine:

- Local range: ≤ **25 mi** OR ≤ **60 min** drive proxy @ 40 mph
- Near a Staffed campus → always **Local**
- **Remote** only if far **and** tickets/day **&lt; 1.2**
- Far **and** ≥ 1.2 tpd → **Staffed** campus
- Hub selection priority: tickets → users → seats; hub threshold **3.0** tpd

## Output tabs

Instructions, VC_Site_Input_Template, VC_Mapped_Sites, VC_Summary, Cost_Model_Load, Exceptions, Run_Metadata, Alias_Map

## Tests

```bash
cd tools/vc_mapper
source .venv/bin/activate
python -m pytest tests/ -q
```

## Customer pilots

Keep real customer workbooks on Desktop under `03_Customer_Inputs/` — **do not commit** customer PII or account names to git. Suite samples use Reference Deal A / Sample labels only.
