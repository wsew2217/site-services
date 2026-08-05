# Reference Deal J — Field Services Operations pack

Source vault file: `engine/research/FS_Operations_v3.pptx` (private; gitignored).  
Surfaced label only: **Reference Deal J**. No account or assignee names in committed artifacts.

Internal DWS Field Services best-practices deck (~2020). Mostly **operating-system tooling** (queue automation + compliance), with embedded screenshots of a seat-based VC staffing plan and role-lane roster. Complements Deal E (catchment) and Deal F (ops scorecard).

## What it is
1. **Staffing Plan foundation** — queues → roles → staging/depot → staffing assignments  
2. **SNAP** — action-code ticket management, daily queue control, consistent updates, compliance dashboard  
3. **WAM** — workflow automation that assigns/updates/dispatches by role, schedule, location, and active volume (techs stop cherry-picking tickets)  
4. **SCHA** — scheduling assistant (lookup by schedule + location)  
5. **Solution design** — ITSM ticket initiation → FS assignment group → automation review → assign + work notes → workflow log

## Staffing screenshot patterns (sanitize & reuse)

### Global knobs (observed on plan sheet)
| Knob | Observed | Engine use |
|---|---|---|
| Seats per tech (ratio) | 600 | Optional **guardrail / commercial ratio**, not day-one sizing driver |
| Tickets per tech (plan) | 5 / day | Aligns with remote throughput band |
| Fail rate (events) | ~2.1 (context-specific) | Estate bootstrap only when tickets missing |
| Working days / month | 22 | Ops calibration (`working_days_month`) |
| FMO tickets/tech/day | ~7.17 | Observed productivity target for CMO→FMO resize |

### Virtual campus sheet columns
`Virtual Campus | Site | Queue | Site Type (Primary/Secondary) | Mins | Distance | Seats | Staging (Y/N) | Location Type (Staffed/Local/Remote) | VC Seats | VC Techs | Total Techs | Schedule lanes | Address`

Schedule lane headers observed: **M / TL / T / W / S / RR** (manager, team lead, tech, and specialty lanes — treat as reporting overlays).

### Classification
- Hub row = **Staffed**; satellites = **Local** or **Remote** by drive minutes/distance  
- Staging flag on selected hubs (depot overlay)  
- VC techs rolled at campus level: seats ÷ ratio (legacy) — engine prefers tickets/day sizing, reports ratio as output

### Role lanes (Primary / Secondary / Tertiary)
Observed role vocabulary (genericized):
- Desktop-Incident, Desktop-Requests  
- Remote Desktop Incident / Requests  
- Staging, Site Lead  
- Infrastructure Support, Telecom, Network/VDI  
- Concierge / specialty campus support  
- Projects (flex lane)

Productivity varies sharply by primary role (high for pure desktop closure; low for staging/infra). Engine should **not** average all roles into one throughput without a mix.

### CMO → FMO resize
```
tk_day = monthly_tickets / working_days_month
fmo_techs = tk_day / target_tickets_per_tech_day
```
Compare **% HC by site** vs **% volume by site** (same staffing-gap idea as Deal F). Split FMO HC into Desktop / Telecom / Network pools when the estate has tower mix.

## What Deal J adds to the engine
1. Explicit **P/S/T role-lane** reporting vocabulary (Deskside pack already hinted; this confirms live use)  
2. **Schedule lane** overlay columns for Staffing Actual (not required for v1 math)  
3. Ops tooling expectations: action codes, auto-assign by role/location/load, compliance drill-down  
4. Optional FMO productivity constant (~7 tickets/tech/day) for scenario calibration alongside Focus & Flex throughputs  
5. Confirms seat-ratio plans still exist in the field — keep them as guardrails only

## What Deal J is NOT
- Not a cost/rate card  
- Not a catchment algorithm definition (uses mins/distance columns already populated)  
- Client logos / validation slides may contain account names — vault only  
- Screenshots contain PII (assignee names) — never ship into public suite or samples
