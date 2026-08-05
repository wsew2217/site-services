# Reference Deals G–I — PFS / ITO cost-model research (sanitized)

Private research note for the generic Site Services deal engine.  
**Zero customer / account names.** Source workbooks are labeled only as:

| Label | Private file handle (local only) |
| --- | --- |
| Reference Deal G | `…PFS Cost Model - Mar 2012 v1 9_….xlsx` |
| Reference Deal H | `…_ITO_CM_V3_50_84.xlsm` |
| Reference Deal I | `… PFS cost model 071012_v3.xlsx` |

Store originals under `engine/research/` (gitignored). Never copy account identifiers into committed code, samples, or the live suite.

---

## Critical rate policy (read first)

These workbooks are **~2009–2012 PFS / IMS cost models**.

### Leverage (structure & logic)

- Tab architecture and calculation flow
- Cost **categories** and how they compose into run-rate vs transition
- Productivity / SLA / volume-driver / transition **formula patterns**
- Which Settings knobs should exist in `parameters.json`

### Do **not** ship as live defaults

- Historical salaries, partner/badged wage tables, burden **dollars**, warranty remit $, mileage unit $, tools $, PMO $, dispatch trip charges, monthly $/seat, total run costs
- Prefer current placeholders already in `engine/defaults/parameters.json` (Cost Model v2 / World Class / modern engine lineage)
- If any 2012 figure is kept for side-by-side comparison, tag it `legacy_reference_only` / `historical` and require a rate refresh before commercial use

Structural ratios and floors below (e.g. vac/sick uplift **1.18**, travel util **0.5**, SLA headcount uplifts) are **candidates to model as knobs**, not mandatory live defaults — calibrate against modern ops data.

---

## Cross-deal verdict

| Deal | What it is | Value to generic engine |
| --- | --- | --- |
| **G** | Classic **PFS field-services** cost model + healthcare estate inventory overlays | Primary pattern for VC staffing math, service×device×fail-rate demand, SLA uplift, transition WBS, salary-modifier gate |
| **H** | Full **multi-tower ITO** cost model (`.xlsm`, macros present — **not executed**); EU Field Services is a ROM side summary + End User desktop engineering tower | Tower composition, delivery-region FTE ratios, transition/PMO assumptions, partner vs badged campus split, service-select catalogs — **not** the PFS seat-level engine |
| **I** | Same PFS template family as G (cleaner, fewer inventory sheets) | Cleanest readable copy of the PFS Single-Year Inputs engine |

**G and I are the same product family** (“How To Use” + `Single Year Inputs` + `Staffing by Site`). H is a different product (IMS ITO) that *embeds* a PFS ROM summary and an End User services catalog.

---

## Reference Deal G — sheet inventory & purpose

| Sheet | Purpose |
| --- | --- |
| How To Use | Operator guide: starred inputs, device/fail/SLA table, VC fields, salary modifier, cost summary |
| PFS Approval | Governance gate before cost submission |
| Assumptions | Commercial + modeling assumptions (volume change bands, SLA attainment, scope exclusions, VC floor, optimization narrative) |
| Client Unit Counts | Facility-level device inventory by region/profile (deal-specific estate feed) |
| Data Sheet | Pivot/region rollups → multi-year device counts, call rates, CPY (calls per year) |
| Single Year Inputs | **Core engine**: services, VCs, management, salary mod, cost summary, hidden calc columns, transition, rate tables |
| Staffing by Site | Per-VC tech / tech-lead / users-per-tech by year (links into Single Year Inputs) |
| Hospitals / Outpatient / Site_Map | Geo/facility lists for MapPoint-era campus mapping (deal-specific) |
| Change / Model Change Log / Version Change Log | Rate-card and logic history |

### Key assumption parameters (structure — not live $)

- **Volume drivers:** device/seat counts × fail (event) rate → annual events; multi-year device mix shifts (thick→thin, growth, refresh)
- **Service taxonomy:** Break/Fix, DSS, IMAC (+ refresh / specialty device lines in filled deals)
- **Device taxonomy:** desktop, laptop, printer, WOW/COW, handheld, barcode, thin client, VIP, etc.
- **Timing:** minutes per service (time-on-task)
- **SLA classes:** NBD, 2-hour, 4-hour, 5 business day; service hours (e.g. M–F 8–5, M–F 7–7, 24×7)
- **In-warranty %** → warranty remit offset (category exists; **$ rate is legacy**)
- **Virtual campus:** map code, VC name, #locations, seats in VC, seats in tech home office (no-travel), 7×24 flag, shared/leveraged city
- **VC mileage radius:** Deal G filled example **30** (miles-era MapPoint radius)
- **VC floor:** assumptions note **VC Floor 1.5** (minimum tech presence concept)
- **Risk:** “standard risk ~4%” narrative; later versions moved risk into burden / removed explicit risk line
- **SLA attainment:** **94%** compliance assumption; onsite spares required for 2h/4h resolve
- **Volume change band:** ±5% → change order
- **Cost validity:** 90 days from submission
- **Productivity / optimization narrative:** tech:asset ratio improvement path; shift-left / FCR; badged vs contractor mix; staging centers; centralized WFM
- **Mgmt span suggestion:** e.g. Delivery Manager ≈ techs/22 (formula pattern; spans should stay modern Settings)
- **Shipping:** often excluded / direct-bill to customer (category flag, not a rate)

### Formula patterns (reusable)

1. **Events = seats × fail_rate** (and multi-year volume columns L–O)
2. **Tickets/seat** aggregated from service minutes / mix → feeds VC sizing
3. **Baseline techs** ≈ `(seats × tickets_per_seat) / (tickets_per_tech_day × working_days)`
4. **Home-base vs travel split:** home-office seats sized at full productivity; travel seats divided by travel utilization
5. **SLA uplift** on baseline heads from mix of 2h/4h/NBD/extended hours/7×24
6. **Vac/sick uplift** on heads (legacy structural factor ~1.18 in sibling Deal I)
7. **Floor / max(uplifted, floor factors)** including 7×24 minimum and shared-city leverage
8. **Tech lead ≈ 10% of uplifted heads** (0.1 factor in template)
9. **Campus validation:** Valid vs Underutilized vs Excess Capacity
10. **Salary modifier gate:** if program modifier &lt; threshold (~0.89), cost lines zero out (incomplete geo mod)
11. **Cost rollup categories:** badged labor + contracted labor + mileage + training + tools/comms (+ WFM) − warranty remit → per-seat / per-event / per-tech / T&M / OPPM (1.5×)
12. **Transition:** role × (design + pilot + training weeks) × weekly cost

### Site / tower / coverage taxonomy

- **Coverage unit = Virtual Campus** (city/area), not modern geo-clustered hub automatically
- Roles implied: home-office (no travel), travel-within-radius, 7×24 site, shared/leveraged city
- Estate feed: facility profiles (hospital size/beds, satellites) → device counts — **industry-specific, do not hardcode**
- Towers: PFS / desk-side field services only (not full ITO)

### Reusable vs deal-specific

| Reusable | Deal-specific / do not port |
| --- | --- |
| VC staffing formula skeleton | Facility names, addresses, hospital/outpatient lists |
| Service×device×fail×minutes×SLA table shape | Healthcare device mix & clinical exclusions |
| Transition WBS by role | Filled VC names / MapPoint codes |
| Cost category tree | 2012 rate cards, partner rates, warranty $ |
| Assumptions language patterns (±5% volume, 90-day validity, spares for fast SLA) | Optimization story unique to that pursuit |

### Gaps vs modern virtual-campus + Focus & Flex

- No automatic hub selection by demand catchment / haversine
- No Staffed / Local / Remote **queue** model with Focus & Flex flexing
- Mileage radius is static MapPoint miles, not drive-minutes + modern overlays
- Productivity is seat/fail-rate based; modern engine prefers tickets/day by incident vs request + utilization
- Limited remote/OEM/smart-hands economics (modern `dispatch.py` is ahead)
- No depot/staging/tech-bar/virtual-tech overlays as first-class objects
- No DSCTM / ops KPI pack
- Geo salary modifier via external MapPoint — replace with region/country rate tables already in Settings

---

## Reference Deal I — sheet inventory & purpose

| Sheet | Purpose |
| --- | --- |
| How To Use | Same PFS operator guide as G |
| PFS Approval | Same governance gate |
| Assumptions | Deal-scope + SLA/severity/VIP/gov-furnished equipment notes |
| Single Year Inputs | Same core engine (best readable instance) |
| Staffing by Site | Same VC staffing output by year |
| Change / logs | Template evolution |

### Key structural knobs observed (Deal I filled model — **logic only**)

Treat as **illustration of the template**, not ship defaults:

| Knob | Observed structural value | Notes |
| --- | --- | --- |
| Working days | **250** | Modern engine uses **252** — keep modern |
| Projected tech load | **0.875** | Multiplies optimized tickets/day |
| Vac/sick uplift | **1.18** | Headcount multiplier |
| Travel utilization | **0.5** | Travel ticket productivity penalty |
| SLA head uplifts | 2h **0.45**, 4h **0.33**, ext hours **0.125**, 7×24 **0** in this fill | Mix-weighted |
| 7×24 floor factor | **5** | Minimum techs when VC flagged 7×24 |
| Floor factor (non-7×24) | via staffing adjustment (**1** in this fill) | |
| VC mileage radius | **20** | Miles-era |
| Badged vs contractor split | B168 / (1−B168) | Staffing mix |
| On-call | Yes/No flag → cost category | |
| Salary mod gate | ~**0.89** | Blocks cost if incomplete |
| Hours basis | **2080** (T&M), **2000** (per-hour view) | Reporting conventions |
| OPPM multiplier | **1.5 ×** T&M hourly | Commercial adder pattern |
| WFM tickets/day capacity | **45** | Workflow manager sizing |
| Transition phases | Design / Pilot / Training weeks by role | Structure to port |
| Services used | Break/Fix, DSS, IMAC, Refresh/MD, Remote Hands | |
| SLA list | 2 Hour / 4 Hour / NBD / 5 Bus. Day | |
| Service hours example | M–F 7–7 (12) | |

Named ranges: `Cost_Summary` → summary anchor; little else (unlike H).

### Formula patterns

Identical family to G. Notable closed-form VC line (conceptual):

```text
baseline_techs = (seats_vc * tickets_per_seat) / (tpd_per_tech * working_days)
home_techs     = (home_seats * tickets_per_seat) / (tpd_per_tech * working_days)
travel_techs   = ((seats_vc - home_seats) * tickets_per_seat) / (tpd_per_tech * travel_util * working_days)
sla_uplift     = baseline_techs * weighted_sla_uplift
uplifted       = max( (vip + home + travel + sla_uplift) * vac_sick * 0.95 , floor_factors )
tech_leads     = (vip + home + travel + sla_uplift) * vac_sick * 0.10
users_per_tech = seats_vc / (uplifted + tech_leads)
```

Demand side:

```text
annual_events[service] = device_count * fail_rate
# minutes feed FTE-hours style columns: (events * minutes / 60) / 2080
```

Cost side categories (compose into Total Costs):

1. Dell management / support / team leads / technicians  
2. Contracted labor  
3. Mileage reimbursements  
4. Training  
5. Tools / communications (+ WFM implementation)  
6. On-call (optional)  
7. Warranty remit **credit** (events × unit $ — **legacy $**)  
8. Transition/training one-time  
→ Annual per seat, monthly per seat, per event, cost per tech, T&M / OPPM hourly  

### Reusable vs deal-specific

| Reusable | Deal-specific |
| --- | --- |
| Entire Single Year Inputs **section architecture** | Filled seat counts, site names, VIP counts |
| SLA / hours / service dropdown taxonomy | Gov security / CMDB AQL language |
| Transition week matrix by role | Incumbent / city split notes |
| Staffing-by-site output shape | Any 2012 salary grid (C3…A5 / partner) |

### Gaps vs Focus & Flex

Same as G. Additionally: “Remote Hands” appears as a **service line**, not as a modern remote-queue + OEM/smart-hands dispatch graph. Staging/spares called out in assumptions for fast SLAs, but not as campus depot objects.

---

## Reference Deal H — sheet inventory & purpose

**Format:** `.xlsm` with `vbaProject.bin`. Inspection used sheet XML / shared strings / named ranges only — **macros not executed**. openpyxl may fail on invalid font `family` in shared strings; zip+XML parse is the reliable path.

### Sheet groups (~85 sheets)

| Group | Examples | Purpose |
| --- | --- | --- |
| Navigation / governance | Cover, DocInfo, TOC, Tags, Opportunity, Solution, Risk Assess, Update Log | Deal metadata, costing mode, cert validity (60 days), risk |
| Assumptions / SLA | Assumptions, SLAs | Narrative assumptions; SLA pointers to solution scope |
| Labor / P&L | FTE-T&L Project, FTE-T&L Recurring, Acct-T&L, Acct-Capital, Acct-Expenses, Acct-Travel, Summary | Multi-year FTE & expense engines |
| Transition | TnT Sched, Ref-Transition | Transition / migration / transformation schedule |
| Volumes | Unit Volumes - Baseline | Baseline monthly volumes by tower |
| **EU Field ROM** | **DTS Summary** | **PFS-style ROM**: campus-staffed vs partner-dispatch vs refresh vs asset recovery — **legacy $** |
| Service catalogs (CS-*) | CS-EndUser, CS-SvcDesk, CS-Windows, … | Tower service-select → qty × unit rates × delivery region |
| Detail / Ref | Detail-*, Ref-ResRates, Ref-Currency, Ref-Country, Ref-CF Tower, Ref-*-Cntl/Lkup | Rate cards, FTE ratios, tower rollups |
| Quotes | MF/security quote tabs | Deal-specific BOM — ignore for Site Services engine |

~**369** named ranges (EndUser_* delivery options, Cap*, Asmpt*, Cost_Mode, currency, etc.).

### DTS Summary (EU Field Services ROM) — structural split

Even with dollars redacted, the **composition** is gold for the generic engine:

1. **Badged / campus PFS cost** (N campus locations) → monthly $/seat on campus seat pool  
2. **Partner dispatch** for remote locations (M remote/dispatch sites) → monthly $/seat + PMO adder  
3. **Refresh program** (device count over months) + remote-site trip charge category  
4. **Asset recovery** (wipe/resell) as separate lifecycle cost  
5. Summary EU-Field = sum of above (with formula adjustments)

This is the clearest historical articulation of **campus-staffed vs partner-dispatch coverage** — maps to modern Staffed/Local vs Remote + `dispatch.py`, but rates must stay modern.

### CS-EndUser (not desk-side PFS)

Catalog of **desktop engineering** services (config collection, SW distribution, patch, packaging, image/hw model management) with:

- Quantity × unit type × start/end month  
- Delivery option (US / India / Mexico / Global / Customer)  
- Thick/thin image option  
- Control sheet FTE ratios: hours → FTE by skill/region (`Ref-EndUser Cntl`)

**Port the pattern** (service component × qty × delivery region → FTE/cost), **not** the 2012 unit costs or FTE hour ratios as defaults.

### SLAs / Assumptions (H)

- SLA tab is mostly scope pointers (“see SLA docs…”) rather than resolve-time math like PFS  
- Assumptions emphasize transition length, smart-hands at sites without Dell associates, remote support, service-desk AHT/FCR-style metrics on SvcDesk control (contacts/user, answer %, resolution rate, leveraged efficiencies)

### Key H parameters useful as **knob ideas**

- Costing mode: Allocation vs Indicative  
- Contract term (months), start date, 60-day cost validity  
- Delivery region & offshore/leverage options  
- Transition duration (example narrative: ~180 days / multi-month phases)  
- Service Desk: avg contacts/user bands, target answer %, resolution rate, shift coverage hours, leveraged efficiency curves  
- Smart-hands / remote support as explicit assumption (not always costed in CS-EndUser)

### Reusable vs deal-specific / do not port

| Reusable | Do not port |
| --- | --- |
| Tower + service-select architecture | Entire non-EUC towers (Unix, storage, mainframe quotes, SecureWorks, …) |
| Campus vs partner-dispatch ROM split (DTS) | Any Ref-ResRates / unit $ tables as live defaults |
| Delivery-region dimension | VBA macros / export machinery |
| Transition & PMO assumption checklist | Account-specific quote BOMs |
| Named-range discipline for controls | 7k+ shared-string deal prose into product copy |

### Gaps vs Focus & Flex

- ITO model is **service-catalog × rate card**, not geo virtual campuses with three queues  
- DTS ROM knows “3 campuses vs 47 remote” but does not compute campuses from drive-time clustering  
- No Focus & Flex lane switching; partner dispatch is a commercial bucket  
- CS-EndUser optimizes imaging/packaging, not field ticket throughput  
- Macros and opaque Ref sheets are hostile to a pure-Python engine — reimplement patterns, don’t embed workbook

---

## Unified formula patterns for the generic engine

Port these as **pure Python constructs** (names illustrative):

1. **Demand resolution chain**  
   tickets if present → else seats/devices × rates → else placeholder  
   (PFS: seats × fail_rate; modern: already in `demand.py`)

2. **Service catalog vector**  
   `{service, device_class, volume, fail_rate, minutes, sla_class, hours_class, in_warranty_pct}`

3. **VC / campus sizing**  
   baseline from tickets÷(tpd×days×util) + travel penalty + SLA uplift + vac/sick + floors (team_floor, 7×24, single-tech exception)

4. **Home vs travel seats**  
   maps to modern Staffed/Local (home/drive) vs Remote (dispatch)

5. **Mgmt pyramid**  
   leads by span, managers by span (PFS used ~techs/22 suggestion + manual C3/C2/C1 rows; modern: `lead_span`, `mgr_span`)

6. **Cost composition**  
   `labor_loaded + logistics(dispatch, ship, depot, stock) + refresh + transition_one_time − credits`  
   (modern `cost.py` already close; add warranty credit & on-call as optional)

7. **Transition WBS**  
   role × phase_weeks × weekly_loaded_cost; parallel_run_months already exists

8. **Commercial outputs**  
   annual total, monthly per seat, per event, T&M hourly, premium hourly multiplier

9. **Governance gates**  
   incomplete geo/rate modifier → block or flag; volume band → change-order warning; cost validity days

10. **Partner vs badged split**  
    fraction of remote volume costed at dispatch partner rates vs campus labor

---

## Incorporation checklist — `engine/`

### A. Settings keys to add to `parameters.json`

Add as **modern placeholders** (or `null` + docs). Do **not** copy 2012 dollars. Where a historical illustration exists, keep it only under a nested `"legacy_reference_only"` object if needed for research UIs — never as the live key.

**Productivity / staffing (align PFS patterns with Focus & Flex)**

| Key | Intent | Suggested modern seed |
| --- | --- | --- |
| `working_days` | Already present | keep **252** (PFS used 250 — do not regress) |
| `utilization` | Already present | keep **0.85** (PFS “projected load” 0.875 is related) |
| `vac_sick_uplift` | PFS CG21-style headcount uplift | e.g. **1.12–1.18** band; default near **1.15** pending ops calibration |
| `travel_utilization` | Productivity while traveling | e.g. **0.5** as starting knob (calibrate) |
| `sla_uplift_2h` / `sla_uplift_4h` / `sla_uplift_nbd` / `sla_uplift_extended_hours` | Headcount multipliers by SLA mix | start from PFS *shape* (0.45 / 0.33 / 0 / 0.125) but treat as **tunable**, not sacred |
| `critical_24x7_floor_techs` | Min techs when campus/site is 24×7 | e.g. **2–5** (PFS used 5 in one fill — likely high for modern flex) |
| `vc_validation_load_factor` | “Valid campus” threshold (PFS 0.95) | optional QA flag |
| `tech_lead_share` | PFS 10% of uplifted heads | prefer existing `lead_span` (keep span model; optional dual mode) |
| `badged_share` | Badged vs contractor mix | e.g. **0.99** or deal override |
| `on_call_enabled` | Boolean | default false |
| `on_call_cost_per_tech_day` | Only if enabled | **modern** rate, not 2012 |
| `fail_rate_desktop` / `fail_rate_laptop` / … | Optional estate bootstrapping when no tickets | modern-calibrated; mark industry packs separately |
| `time_on_task_minutes_default` | Default minutes when catalog thin | calibrate from ops, not 60-min template habit alone |
| `sla_attainment_target` | PFS 94% narrative | align with `ops_kpis.json` slo/sla (already richer) |
| `volume_change_band` | ±5% change-order trigger | **0.05** |
| `cost_validity_days` | Commercial freshness | **60–90** |
| `warranty_labor_credit_per_event` | Credit category | modern OEM program rate or **0** |
| `oppm_hourly_multiplier` | Premium T&M | e.g. **1.5** |
| `hours_per_year_tm` / `hours_per_year_reporting` | 2080 vs 2000 views | optional reporting |
| `transition_design_weeks_*` / `transition_pilot_weeks_*` / `transition_training_weeks_*` | By role band | structure from PFS; **$ from modern labor** |
| `wfm_tickets_per_coordinator_day` | WFM sizing | optional overlay |
| `partner_remote_share` | Fraction of remote work via partner | from H DTS pattern |
| `home_office_seat_share` | Seats needing no travel | intake-driven preferred |
| `salary_modifier_min` | Gate incomplete geo mods | e.g. **0.89** as warning threshold — or replace with “all regions priced?” QA |

**Already covered — do not duplicate blindly**

`drive_radius_km`, `team_floor`, `lead_span`, `mgr_span`, `burden_uplift`, regional `rate_*`, dispatch/shipment rates, depot/stock, refresh, transition cash (`parallel_run_months`, `hire_train_per_add`, `program_mgmt_per_step`), overlays.

### B. `cost.py` constructs to add

| Construct | Source pattern | Notes |
| --- | --- | --- |
| Cost category breakdown object | G/I Cost Summary rows | Expose labor / contract / mileage / training / tools / dispatch / ship / depot / stock / refresh / transition / credits |
| Optional `warranty_credit` | G/I warranty remit | `events * warranty_labor_credit_per_event` — default 0 |
| Optional on-call line | G/I on-call flag | |
| Per-seat & per-event unit economics | G/I outputs | Useful commercial sheet; derive from totals |
| T&M / premium hourly views | ÷ hours_per_year × multiplier | Reporting only |
| Transition WBS aggregator | G/I DP81+ block | Role×weeks×weekly cost; feed `cash.total_one_time` |
| Partner vs badged remote split | H DTS | `partner_remote_share * remote_tickets * dispatch_cost_region` |
| Volume-band / validity warnings | Assumptions | Non-blocking QA in summary JSON |
| `legacy_reference_only` compare block | optional | Never used in `day1` totals |

### C. `dispatch.py` constructs to add

| Construct | Source pattern | Notes |
| --- | --- | --- |
| SLA-class → dispatch urgency multiplier | PFS SLA uplifts | Affect rate or probability, not 2012 $ |
| Coverage split: campus labor vs partner dispatch | H DTS | Remote role already gates dispatch; add partner share |
| Trip-charge style remote visit (optional) | H remote trip charge category | Use modern `dispatch_cost_*` |
| Spares / stocking flag for 2h/4h sites | G/I assumptions | Link to depot/stock in `cost.py` when `Critical24x7` or fast SLA |
| Service-line Remote Hands | Deal I | Map into remote queue + dispatch, don’t invent parallel staffing |

### D. Related modules (for completeness)

| Module | Incorporate |
| --- | --- |
| `demand.py` | Optional fail-rate bootstrap when tickets missing; service catalog expansion |
| `staffing.py` | Travel util, vac/sick uplift, SLA mix uplift, 24×7 floor; keep Focus & Flex queues |
| `ops.py` / `ops_kpis.json` | Prefer modern SLO/SLA matrices over PFS 94% single number |
| `intake.py` | Columns: home-office seats, SLA class, 7×24, partner-remote flag, device counts |
| `workbook.py` | Staffing-by-campus sheet akin to PFS Staffing by Site (generic names) |

### E. Do **NOT** port

- Any 2012 salary grids (C3/C2/C1/B3/B2/B1/A5, partner, ASP)
- Mileage unit rates, warranty $45-style credits, tools $650-style adders, WFM setup $, PMO fixed $ from H
- MapPoint / salary-mod map dependency
- Healthcare facility master data / hospital profile heuristics as core engine
- Full IMS tower stack from H (Unix, storage, mainframe, messaging, …)
- VBA / macro workflows, Ref-Export, printer settings bloat
- Opaque `Ref-ResRates` as authoritative live rate card
- Working-days regression 250←252
- Users:tech ratio as day-one sizing driver (PFS reported users/tech; modern methodology: throughput first, ratios as guardrails — already correct in `cost.py` / methodology)
- Account prose, emails, opportunity IDs, quote BOMs
- Executing or embedding `.xlsm` macros

---

## Suggested implementation sequence

1. **Document knobs** in `parameters.json` + methodology (vac/sick, travel util, SLA uplifts, 24×7 floor, partner share) with modern seeds.  
2. **Extend `staffing.py`** to apply travel + SLA + vac/sick uplifts on top of Focus & Flex natural sizing (preserve team_floor / single-tech rules).  
3. **Extend `dispatch.py`** with partner_remote_share + optional SLA urgency.  
4. **Extend `cost.py`** category rollup + transition WBS + optional credits; keep scenario ladder.  
5. **Intake fields** for home-office share, SLA class, 24×7, device counts.  
6. Only then consider a `legacy_reference_only` comparison pack — never as production defaults.

---

## Source handling notes

- Deal H: do not execute macros; prefer zip/XML if openpyxl chokes on sharedStrings font families.  
- Deals G/I: `data_only=True` needs a prior Excel cache for evaluated constants; formula inspection used `data_only=False`.  
- All dollar outputs in sources are **historical** — refresh before any customer-facing model.

