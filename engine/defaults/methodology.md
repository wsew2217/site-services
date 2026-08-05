# Site Services methodology pack (generic)

Customer-name-free operating defaults for the deal engine.

## Focus & Flex / Focused-Lane
- Every site has one accountable virtual campus (no orphans).
- Two mirrored modes by volume: campus-focused (local-first) and remote-focused (depot-first).
- Focus when work is present; flex into secondary lanes when it eases.
- Queues: Campus (hub), Local (drive range), Remote (remainder + dispatch/OEM).

## Staffing math
- Working days: 252.
- Incident share default 50/50 until ticket extract calibrates it.
- On-site: 6 incidents / tech / day, 4 requests / tech / day.
- Remote: 5 tickets / tech / day.
- Utilization: 85%.
- Team floor: 2 (single-tech exception below 2.5 tickets/day).
- Leads: 1 per 10 techs (by region). Managers: 1 per 24 field techs.

## Hub selection
- Prefer home-country sites with coordinates.
- Hub maximizes catchment volume inside drive radius (default 60 km / ~60 minutes).
- Sites without coordinates are Remote/Uncertain — never auto-local.

## Demand resolution
1. Annual tickets if present  
2. Else users/seats × estate ticket rate  
3. Else devices × device ticket rate  
4. Else placeholder with low-confidence flag  

## Coverage classes (overlays)
- Dedicated business hours / Dispatch / Critical 24×7  
- Depot/staging, tech bar, VIP, virtual tech overlays  

## Role lanes (Primary / Secondary / Tertiary)
From Deskside + Reference Deal J (FS Ops pack):
- Every tech has a **primary** lane; secondary/tertiary are flex coverage, not additive headcount.
- Common lanes: Desktop-Incident, Desktop-Requests, Remote Desktop, Staging, Site Lead, Telecom, Network/VDI, Projects.
- Throughput differs by primary lane — do not blend staging/infra with deskside closure rates.
- Schedule reporting lanes (optional): Manager / Team Lead / Tech / specialty (W, S, RR).

## FS ops tooling expectations (SNAP / WAM pattern)
- Tickets assigned by role, schedule, location, and active load — not tech self-select.
- Action-code driven updates; consistent formatting; management oversight of all queues.
- Compliance dashboard drills account → technician.
- Engine outputs should remain ITSM-agnostic; these are operating assumptions for post-go-live design QA.

## Ops KPIs (post-design QA)
- DOH = open ÷ average daily closed  
- Productivity = closed ÷ working days ÷ techs  
- Staffing gap = site staff share − site volume share  
- SLO target 95%; tighter internal SLO than contractual SLA  

## DSCTM
- Future-oriented status codes; close only as RSLV or CNRC  
- Update cadence ~ every 2 hours when needed  
- Capture time-on-task minutes  

Ratios (users:tech) are reported outputs / commercial guardrails — not the day-one sizing driver.
Legacy seat-ratio plans (e.g. 600:1 in Reference Deal J screenshots) stay optional guardrails.
Optional FMO calibration: `techs ≈ (monthly_tickets / working_days_month) / target_tickets_per_tech_day`.

## Cost rate policy
- Settings dollar amounts are **modern placeholders** (Cost Model v2 / World Class lineage).
- Older PFS cost workbooks (Reference Deals G–I era) are leveraged for tab structure, cost categories, and driver logic only.
- Always refresh labor, dispatch, shipment, and burden rates per deal before customer-facing use.
