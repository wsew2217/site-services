# Field Services / Site Services — delivery optimization metrics

Public research note for **Generic Site Services** deal design.  
All ranges below are **industry-typical** (vendor benchmarks, TSIA / MetricNet / Microsoft / Salesforce / ServiceNow docs). They are **not** Dell, Deal A, or any named-customer truth.

Site Services ≡ Field Services on process skeleton (see `reference_deal_k_fmo_process.md`). This note maps external FSM / deskside KPIs onto that skeleton and onto `ops_kpis.json`.

---

## Ranked metrics for Site Services deal design

Usefulness ranking for **solution design / commercial conversation**, not for a 40-KPI ops dashboard.

| Rank | Metric | Why it matters for deal design | Industry-typical range | Suite alignment |
| --- | --- | --- | --- | --- |
| 1 | **First-time fix / first-visit resolution (FTFR)** | Single strongest cost × capacity × CX lever; failed visits drive repeat truck rolls and inflate cost-to-serve | OEM/FSM median ~**75–77%**; top ~**86–88%**; bottom ~**53–60%** (30-day window). Deskside first-visit resolution avg ~**84%** (MetricNet) | Design target **≥85%** on-site; measure reopen ≤15 days (`reopen_days`) |
| 2 | **Avoidable dispatch / remote-resolve potential** | Prices tech-bar, virtual tech, and remote-first overlays; every avoided truck roll frees capacity | Avoidable dispatch median **~14%** (top **~3%**, bottom **~24%**). ~**1 in 5** cases remotely resolvable (Aquant 2026); ~**33%** of queries solvable without a field pro (Aquant 2025) | Cost-model deflection + remote queue; Deal B virtual tech pattern |
| 3 | **SLA / SLO attainment** | Contractual trust + penalty risk; separate internal SLO from customer SLA | Industry ops targets often **≥90%**; this suite uses **SLO 95%** tighter than contractual SLA matrices | `slo_target` 0.95; `slo_*` / `sla_*` hour matrices by priority |
| 4 | **Technician utilization (booked / productive)** | Converts headcount into daily close capacity; over-max kills response slack | Billable util typical **75–85%**; pacesetters ~**90%** (TSIA). Dynamics: booked ÷ working hours | Methodology / cost-model **85%**; keep band, do not chase 95%+ |
| 5 | **Travel time vs wrench / productive time** | Hub-and-spoke and catchment radius story; Local vs Remote economics | Travel often targeted **&lt;20%** of work hours; wrench time (hands-on only) commonly **25–35%**, best-in-class **45–55%** (maintenance literature) | `travel_utilization` penalty on Local-drive seats; local range ≈25 mi or ~60 drive-min @ 40 mph |
| 6 | **Cost per resolution / cost-to-serve** | Makes labor→logistics shift visible; failed first visit raises total resolution cost | Resolution cost ~**34–44%** higher than single work-order cost when first visit fails. Top performers’ cost/WO ~**23%** below median | Generic cost model; parts ship, dispatch, OEM attach |
| 7 | **Parts fill / logistics readiness** | Leading cause of FTFR failure; depot & stock knobs | Mature targets often discussed **92–96%** fill when segmented by criticality (no universal blended benchmark) | Depot count, stock value, ship share in cost model |
| 8 | **Schedule adherence / on-time arrival** | Dispatch quality + CSAT driver | Strong ops often cite **~85–90%+** on-time within window | Contact/schedule FMO stage; ERT / CETA status codes |
| 9 | **Productivity (closed / tech / day) & coverage ratios** | Day-one HC math and commercial ratio guardrails | Suite: on-site ~**4–6**/day by type; remote ~**5**/day; FMO calibration ~**7**/day. Users:tech bands are **guardrails only** | `productivity_closed_per_tech_day_target` 5; `fmo_tickets_per_tech_day_target` 7 |
| 10 | **Backlog health (DOH) & aging** | Capacity vs demand QA before go-live | Design: DOH green ≤**1.5**, amber ≤**2.5**; aging bands 0–3 … 30+ | `doh_*`, `aging_bands` in `ops_kpis.json` |
| 11 | **CSAT / NPS / revisit / abandon** | Outcome proof for CX; revisit ≈ failed FTFR | Field CSAT often discussed **80–85%** “good”, **90%+** strong. Service-desk abandon healthy **~2–5%**. Revisit rate ≈ 1 − FTFR | Post-go-live scorecard; not day-one sizing |
| 12 | **Dispatch / routing optimization KPIs** | Automation rate, travel hours saved, schedule stability | Salesforce ESO guidance: automation rate often **&gt;80%**; manual **&lt;20%**; track tech hours saved & resource assigned time | ITSM-agnostic operating assumption |

---

## Topic deep-dives

### 1. Core FSM KPIs

**First-time fix rate (FTFR)**  
`(jobs resolved on first visit ÷ total jobs) × 100`. Prefer a **30-day** related-ticket window; shorter windows overstate FTFR by splitting revisits (Aquant). Pair with resolution time — high FTFR with long waits is not good service.

**MTTR / resolution time**  
Define the clock: repair (hands-on) vs recovery/resolve (customer-experienced). Aquant 2026: median resolution ~**4.5 days**; top **~2.5**; bottom **~10**. Deskside / Site Services estates often measure hours against priority SLA, not multi-day OEM cycles — use the **priority matrices** in `ops_kpis.json`.

**SLA attainment**  
Dynamics 365 Field Service tracks work-order arrival / resolution KPIs against business hours. This suite separates **SLO** (internal, tighter) from **SLA** (contractual).

**Travel vs wrench time**  
Utilization can look healthy while wrench time is low (travel + admin + waiting). Tractian-style maintenance literature: wrench time excludes travel/wait/admin. For Site Services, prefer **productive touch time** and **travel share of Local queue**.

**Utilization & schedule adherence**  
Microsoft Dynamics: `Utilization % = booked hours ÷ available working hours` (Committed bookings). Salesforce Field Service Optimization Hub tracks FTFR, average travel, utilization, automation rate. Pushing utilization past mid-80s trades away same-day response slack (VSight / TSIA framing).

### 2. Dispatch / routing optimization

Track as a **system** of metrics, not one score:

- Average travel time / travel share of day  
- Jobs per tech per day (lane-specific)  
- Schedule adherence (arrival in window)  
- Optimization automation rate vs manual schedule edits  
- Appointment handoffs / reassignments (schedule instability)  
- Capacity allocated vs demand by territory / campus (ServiceNow Capacity Console pattern)

Hub-and-spoke (virtual campus): hub maximizes catchment volume; Local stays inside local range (25 mi OR ~60 drive-min); Remote + Smart Hands / OEM only for far sites below `remote_max_tpd`; far high-volume sites promote to Staffed. Routing KPIs should be **split by Campus / Local / Remote** — blended averages hide the remote cost problem.

### 3. Remote resolve / virtual tech / tech bar deflection

| Metric | Definition | Industry-typical |
| --- | --- | --- |
| Avoidable dispatch rate | Dispatches that did not need a truck ÷ total dispatches | Median **~14%** (Aquant 2025) |
| Remote resolution rate | Cases closed with **no** site visit | No strong public median — track vs own baseline; proxy via avoidable dispatch |
| Remote resolution potential | Cases that *could* have closed remotely | **~20%** (Aquant 2026); mismanaged potential can inflate cost share from ~1.4% to ~18% |
| Self-service / L1 deflection | Queries solved without a field professional | **~33%** of service queries (Aquant 2025) |
| Tech bar deflection | Walk-up closes that never become field tickets | Estate-specific; design as overlay capacity, not generic % |

For Site Services: remote-eligible work tries remote **before** contact/schedule (FMO). Virtual tech / tech bar are **overlays** on the same process ladder.

### 4. Staffing productivity & coverage (no invented customer data)

| Lever | Suite default | Notes |
| --- | --- | --- |
| Utilization | 85% | Inside TSIA typical band |
| On-site incidents / tech / day | ~6 | Throughput sizing |
| On-site requests / tech / day | ~4 | Throughput sizing |
| Remote tickets / tech / day | ~5 | Remote queue |
| Closed / tech / day (ops QA) | 5 | `productivity_closed_per_tech_day_target` |
| FMO calibration | ~7 tickets / tech / day | Scenario resize, not sole truth |
| Lead / manager span | 1:10 / 1:24 | Ops overhead |
| Users : tech bands | 250:1 – 2000:1 by pattern | **Commercial guardrails only** — size from workload |

MetricNet / HDI lineage: size from **workload**, not a fixed seats-per-tech myth. Coverage metrics: on-site reach % of physical touches, campus count, Local vs Remote ticket share, staffing-gap (staff share − volume share by VC).

### 5. Cost-to-serve & parts logistics

- **Cost per ticket / cost per resolution**: total operating cost ÷ resolved tickets (include labor, travel, parts, overhead). Field **resolution cost** includes multi-visit closure within ~30 days.  
- Failed first visit → resolution cost **~34%** (Aquant 2025) to **~44%** (Aquant 2024) above single work-order cost.  
- Failed visits ≈ **25%** of total service cost at median; **44%** for bottom performers vs **14%** for top (Aquant 2026).  
- Top performers’ cost per work order ~**23%** below median (Aquant 2025).  
- **Parts fill rate**: fulfilled from available stock ÷ parts requests. Segment by criticality; blended 95% can hide critical stockouts. Target discussion band **92–96%** for mature segmented ops (industry commentary — not a single global standard).

Site Services cost model already prices shipments, depot fixed/variable, stock carrying, smart-hands dispatch, OEM attach — use those as the deal-design cost-to-serve story.

### 6. Customer experience

| Metric | Role | Industry-typical |
| --- | --- | --- |
| CSAT | Post-visit / post-ticket satisfaction | Often **80–85%** “good”, **90%+** strong (vendor/practitioner guides) |
| NPS | Relationship loyalty | Sector-dependent; use as trend, not sizing input |
| Revisit / reopen rate | Inverse of durable FTFR | Align reopen window with `reopen_days` (15) |
| Abandon (walk-up / phone / chat) | Access friction at tech bar / SD | Healthy service-desk abandon often cited **~2–5%** |
| On-time arrival | Window promise kept | Strongly correlated with CSAT |

Aberdeen-cited practitioner summaries put CSAT ahead of pure efficiency for “success” perception — still pair with FTFR and SLA.

### 7. Capacity, backlog, aging

ServiceNow FSM Capacity Console / Territory Capacity Analytics pattern:

- Allocated capacity vs actual demand (by territory / channel)  
- Used vs unused capacity  
- Reservation rules by demand channel (break/fix vs PM vs projects)

Suite design targets:

- **DOH** (open ÷ avg daily closed): green ≤1.5, amber ≤2.5; incidents tighter than requests  
- **Aging bands**: 0–3, 4–7, 8–9, 10–19, 20–29, 30+ days  
- Growing backlog with high utilization → aging priority boost (do not only maximize booked hours)

### 8. Hub-and-spoke / campus / Smart Hands

Industry language:

- **Hub-and-spoke / virtual campus**: central accountable team + local drive-range sites + remote tail  
- **Smart Hands**: short, guided physical tasks under remote direction (suite cap ~**60 min TOT**) — not full break/fix  
- **Remote hands** (DC) vs **field / deskside** (offices, plants, campuses) — Site Services is the latter, with Smart Hands as a logistics branch  
- Partner / OEM dispatch for Remote uncovered touches

KPIs that prove the model: Local travel share, Remote dispatch unit cost, Smart Hands TOT, on-site reach %, FTFR by Campus/Local/Remote, avoidable dispatch after remote triage.

---

## Trade-offs (do not optimize one KPI alone)

1. **Utilization ↑** vs **response / SLA** — mid-80s is a band, not a ceiling to smash.  
2. **FTFR ↑** by delaying visits for parts/skills vs **resolution time / CSAT**.  
3. **Contact-center AHT ↓** vs **avoidable dispatch** — rushed triage creates truck rolls.  
4. **Short FTFR windows** vs honest performance — use ≥30 days for related issues.  
5. **Labor cut** without logistics maturity → cost-to-serve shifts to ship/dispatch/OEM (cost model ladder).

---

## Mapping to engine defaults

| External concept | `ops_kpis.json` / methodology |
| --- | --- |
| SLO / SLA clocks | `slo_target`, `slo_ack_hours`, `slo_res_hours`, `sla_*` |
| Backlog health | `doh_*`, `aging_bands` |
| Productivity | `productivity_closed_per_tech_day_target`, `fmo_tickets_per_tech_day_target` |
| Contact / unreachable | `contact_attempts_*`, `unreachable_*` |
| Smart Hands | `smart_hands_max_tot_minutes` |
| Reopen / revisit window | `reopen_days` |
| Delivery optimization targets | `delivery_optimization` object (industry-typical + design targets) |
| Utilization | methodology / parameters `utilization` 0.85 |

---

## Sources (URLs)

### Benchmarks & KPI frameworks
- https://vsight.io/field-service-kpis/ — formulas + attributed TSIA / Aquant / Siemens tables  
- https://www.globenewswire.com/news-release/2026/02/19/3241231/0/en/Aquant-s-2026-Field-Service-Benchmark-Companies-Can-Unlock-up-to-26-in-Service-Cost-Savings-by-Scaling-Knowledge-Across-the-Workforce.html — Aquant 2026 (FTF 77/88/60, MTTR 4.5/2.5/10, remote potential 1-in-5)  
- https://21176235.fs1.hubspotusercontent-na1.net/hubfs/21176235/2025%20General%20BMR%20010824.pdf — Aquant 2025 General Benchmark PDF  
- https://21176235.fs1.hubspotusercontent-na1.net/hubfs/21176235/ebook-2024-benchmarkreport-12-19.pdf — Aquant 2024 benchmark PDF  
- https://smartserviceops.com/field-service-kpi-framework/ — KPI maturity framework  
- https://smartserviceops.com/parts-fill-rate-kpi/ — parts fill as FTFR driver  
- https://fieldcamp.ai/blog/field-service-metrics/ — metric catalog including remote resolution  
- https://shifton.com/service/blog/field-service-kpis/ — utilization, travel, schedule adherence, CSAT framing  

### Deskside / IT support
- https://www.metricnet.com/desktop-support-metrics-part-5/ — deskside first-visit resolution ~84% avg (70–97%)  
- https://www.metricnet.com/service-desk-cost-per-ticket-motm/ — cost per ticket definition & drivers  
- https://www.zendesk.com/blog/customer-service/help-desk/help-desk/top-10-help-desk-metrics/ — help-desk cost per ticket / abandon context  

### Platform docs
- https://learn.microsoft.com/en-us/dynamics365/field-service/schedule-board-utilization — utilization formula  
- https://learn.microsoft.com/en-us/dynamics365/field-service/sla-work-orders — SLA KPIs on work orders  
- https://www.salesforce.com/en-us/wp-content/uploads/sites/4/documents/resources/field_service_scheduling_and_optimization.pdf — optimization layers & KPI examples  
- https://help.salesforce.com/s/articleView?id=service.fs_es_insights_consider.htm — ESO dashboard (automation rate, tech hours saved)  
- https://www.servicenow.com/docs/r/field-service-management/capacity-console.html — capacity vs demand by territory  

### Hub / Smart Hands context
- https://techmate.com/blog/smart-hands-vs-remote-hands-vs-field-services/ — glossary: smart hands vs field services  
- https://www.fortsol.com/smart-hands-why-on-site-expertise-matters-for-distributed-infrastructure/ — distributed smart hands + SLA tiers  
- https://tractian.com/en/glossary/wrench-time — wrench time vs utilization  

---

## How to use in a deal conversation

1. Lead with **FTFR + avoidable dispatch + SLO** — cost, capacity, and contract in three numbers.  
2. Show **utilization band (85%)** and **throughput** as the staffing engine; ratios as guardrails.  
3. Price **remote / tech bar deflection** before cutting Local heads.  
4. Show **parts / depot / dispatch** rising as labor falls (cost-to-serve shift).  
5. Put **DOH / aging** on the post-design QA scorecard, not the day-one HC formula.  
6. Label every external benchmark **industry-typical** — calibrate from the estate’s ticket extract.
