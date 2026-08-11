# Site Services VC Mapper (Mac)

Local Python package that maps site intake into Hub / Local / Remote roles and a cost-model load sheet.

## Folder

```
~/Desktop/site_services_vc_mapper/
  requirements.txt
  default_rules.yaml
  column_aliases.yaml
  vc_mapper.py
  build_template.py
  README.md
  vc_template_pack_v1_0.xlsx
```

Governed storage lives under `~/Desktop/Site Services Solutioning/`.

## Setup (Mac)

```bash
cd ~/Desktop/site_services_vc_mapper
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

## Build / refresh template

```bash
cd ~/Desktop/site_services_vc_mapper
source .venv/bin/activate
python3 build_template.py
```

## Run mapper

```bash
cd ~/Desktop/site_services_vc_mapper
source .venv/bin/activate
python3 vc_mapper.py \
  --input vc_template_pack_v1_0.xlsx \
  --output vc_template_pack_v1_0_mapped.xlsx \
  --operator-name "Darren Reinhardt"
```

Optional: `--skip-geocode` when latitude/longitude are already present (or to avoid Nominatim).

## Catchment rules (v1)

Aligned with `default_rules.yaml` and the site suite engine:

- Local range: ≤ **25 mi** OR ≤ **60 min** drive proxy @ 40 mph
- Near a Staffed campus → always **Local**
- **Remote** only if far **and** tickets/day **&lt; 1.2**
- Far **and** ≥ 1.2 tpd → **Staffed** campus
- Hub selection priority: tickets → users → seats; hub threshold **3.0** tpd

## Output tabs

Instructions, VC_Site_Input_Template, VC_Mapped_Sites, VC_Summary, Cost_Model_Load, Exceptions, Run_Metadata, Alias_Map

## Customer pilots

Keep real customer workbooks on Desktop under `03_Customer_Inputs/` — **do not commit** customer PII or account names to git.
