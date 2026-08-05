# Reference Deal K — FMO Process Pack

Source vault files (private; gitignored):
- `engine/research/FMO_Process_Flows_V2.pdf` (~26 pages, 2018 lineage)
- `engine/research/FMO_Process_Diagrams_A03.pdf` (~22 pages, 2019–2020 lineage)

Surfaced label only: **Reference Deal K / FMO Process Pack**.  
No customer, account, project, vendor, or assignee names in committed artifacts.

## Locked decision (Site Services ≡ Field Services)

**Site Services and Field Services share the same process-flow model.**  
Treat deskside / site / field FMO swimlanes as one operating system for deal design. Do not maintain separate Site vs Field process trees in the engine. Differences (campus vs remote, staging vs dispatch partner) are **coverage overlays and routing branches**, not distinct methodologies.

## What the decks are

Two Future Mode of Operation (FMO) process-diagram packs for deskside / field services:

| Pack | Focus | Process IDs |
|---|---|---|
| Flows V2 | Campus + remote HW, IMAC, logistics, swivel-seat / partner dispatch | FS001–FS021 |
| Diagrams A03 | Call initiation → triage → break/fix towers → MACD → quarantine → stock | FS-001–FS-017 + Supp-001 |

Same skeleton: ITSM ticket → quality / misroute gates → contact & schedule → work tower → finalize / asset updates.  
A03 is the cleaner numbered set; V2 adds logistics depth (shipping, receiving, hot swap, data wipe, partner dispatch / swivel seat).

## Canonical stage chain

```
Intake (SD / self-service / walk-up)
  → Quality review & categorization
  → Misroute correction (voice handoff when high priority)
  → Remote-eligible? → remote resolve
  → Else Contact & Schedule
  → Tower work (HW / SW / IMAC / Smart Hands / AV / Printer / …)
  → Staging / warehouse / quarantine / RMA as needed
  → Finalize (KB, EU confirm, close)
```

### Escalation & queue rules (genericized)
- Ticket transferred **more than twice** → escalate to deskside lead.
- High-priority / ESS events get **voice handoff** (phone until answered), not silent reassignment.
- ESS / hardware-outage work moves to the **front of the queue**.
- Shared-device / clinical-area pattern: tech may **walk-by** instead of remote contact.
- Misroute: if resolver group unknown → return to Service Desk with notes; if known → transfer (voice if high priority).

### Contact & scheduling
- Contact channels: email, phone, IM, walk-by (staffed sites).
- Attempt contact **at least twice per business day**.
- Incidents: **3 contact attempts over 3 business days**; then update / cancel path (SLA clock stopped while Pending).
- Requests: **~2 weeks** with no end-user response → notify / close-cancel (exclude known OOO).
- Schedulers create calendar invites for tech + end user on request work.

### Work towers (process catalog)

**Shared core (both packs)**  
Call initiation · Misroute · Contact/Scheduling · Hardware break/fix · Software support · Smart Hands · IMAC (install / move / add-change / de-install) · Quarantine / device return · Resolve / finalize · Backend repair / RMA

**V2-leaning logistics**  
Hot swap · Re-image · Data wipe · Shipping · Receiving · Asset disposition · Partner / swivel-seat dispatch · New-hire campus/remote · Remote HW (near campus vs not-in-scope / partner)

**A03-leaning towers**  
Incident triage · Printer break/fix · Conference / AV · Rounding · Onsite stock management

### Swimlanes (generic roles)
| Lane | Typical responsibility |
|---|---|
| End user / requestor | Raise issue; accept schedule; confirm resolution |
| Service Desk | Intake, triage, categorization, misroute return |
| Workflow / automation | Completeness checks; auto-assign by priority / rules |
| Deskside / field tech | Contact, onsite work, asset updates, close |
| Remote resolution team | Remote-eligible resolve before dispatch |
| Scheduler | Request calendaring (may be separate from incident tech) |
| Warehouse / staging / depot | Image, ship, receive, quarantine, stock reorder |
| Dispatch partner | Remote / non-campus physical touch when not local |
| Site lead / manager | Escalation after repeated transfers; stock reorder oversight |
| Asset management | AMDB / status / disposition (often sibling FMO) |

### Staging / depot / dispatch patterns
- **Campus HW:** inventory check → hot swap / repair path; quarantine full systems before reuse.
- **Remote HW:** remote team first; else dispatch partner or ship-to-user; EU may escalate if out of scope.
- **IMAC install:** warehouse build/image → ship to tech → deskside complete → asset update.
- **De-install / return:** receive → quarantine hold → wipe if applicable → reuse pool or disposal pickup.
- **Smart Hands:** short guided tasks from requesting IT; **not** for work over ~1 hour TOT.
- **Stock mgmt:** review asset DB / reorder points → pull warehouse / order OEM / borrow from another site.
- Quarantine hold observed as **14 calendar days** (V2) or **7 business days** (A03) — engine default uses 14 calendar days; tune per deal.

## What maps into the deal engine

| Theme | Engine use |
|---|---|
| Site ≡ Field process model | Methodology lock; one FMO process pack for Site Services deals |
| Campus / Local / Remote + partner dispatch | Catchment queues + `partner_remote_share` + dispatch cost lines |
| Staging / warehouse / quarantine | Depot overlay, staging radius, shipment rates, stock carrying |
| Contact / unreachable cadence | Ops KPI defaults (attempts, incident days, request weeks) |
| Smart Hands TOT ceiling | Caps when classifying Smart Hands vs full break/fix volume |
| Misroute escalate-after-N-transfers | Ops design QA / queue health (not staffing math) |
| Role lanes already in Deal J | Confirmed: Desktop-Incident/Requests, Staging, Remote, Projects |
| Break/fix vs IMAC vs logistics mix | Informs physical-touch / shipment / dispatch share knobs |

## Operating procedure only (do not hardcode into math)

- Exact ITSM form names, knowledge-article IDs, leave-behind card scripts  
- Voice-handoff scripts and Skype/IM channel lists  
- Warranty redeploy rule (“under 3 months remaining unless critical”)  
- Asset-management sibling FMO (HAM / disposal) detail  
- Rounding cadence for metro sites  
- Clinical / shared-device walk-by etiquette  
- Vendor- or account-specific resolver group names  

## Numeric cues captured as defaults

| Cue | Observed | Default key |
|---|---|---|
| Contact attempts / business day | ≥ 2 | `contact_attempts_per_business_day` |
| Incident unreachable window | 3 business days / 3 attempts | `unreachable_incident_business_days` (+ existing `unreachable_attempts`) |
| Request unreachable window | 2 weeks | existing `unreachable_window_weeks` |
| Misroute escalate after transfers | more than 2 | `misroute_escalate_after_transfers` |
| Quarantine hold | 14 calendar days (alt: 7 business) | `quarantine_hold_days` |
| Smart Hands max TOT | 1 hour | `smart_hands_max_tot_minutes` |

## What Deal K is NOT
- Not a cost/rate card  
- Not a catchment / hub-selection algorithm (uses campus vs remote as process branches only)  
- Not a staffing-ratio source (see Reference Deal J for FMO tickets/tech/day)  
- Source PDFs contain customer/vendor/PII labels — vault only; never ship into suite or samples
