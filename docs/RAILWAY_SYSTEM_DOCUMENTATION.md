# SENTINEL AI — INDIAN RAILWAYS SYSTEM DOCUMENTATION
## Comprehensive Disaster Management Specification for High-Density Railway Stations

**Target:** Smart India Hackathon 2026 — AICTE Student Innovation — Software — Disaster Management (`SIH26206`)  
**Modeled Reference Domain:** Central Railway Station Junction Terminal (Platforms 1-4 & Main Foot Overbridges)  
**Primary Pilot Station:** Central Junction Terminal (Platforms 1-4, Foot Overbridges FOB-1 & FOB-2, Main Concourse Staging Hall)  
**Authority Reference:** `Sentinel_AI_SIH2026_Final_Strategy_Report.pdf` (Team X Factor, MIT School of Computing)  

---

## 1. Context & Operational Challenge: High-Density Railway Junction Stations

High-density railway junction stations represent massive passenger interchange environments, handling hundreds of thousands of daily commuters and long-distance passengers across narrow vertical staircases, elevated foot overbridges, and boarding platform edges.

### The Physical Disaster Challenge
1. **Extreme Asymmetric Train Arrival Surges:** Simultaneous arrival of multiple heavy express trains (e.g., Rajdhani, Shatabdi, Mail Express) discharges thousands of passengers onto narrow platform staircases within seconds.
2. **Topological Funnels & Constrained Foot Overbridges:** Diverting flow onto secondary pedestrian bridges (such as Alternate East FOB) creates dangerous secondary bottlenecks if the stairs or platform landings saturate.
3. **The Fatal "Secondary Chokepoint" Paradox:** Traditional surveillance detects congestion at platform stairs and prompts security to divert crowds onto alternate foot overbridges. However, if those alternate relief routes are already near capacity or constricted by counterflow, the diversion triggers a crush at the secondary location.
4. **Local Network Outage Resilience:** In high-density station areas or severe weather, external WAN connectivity can drop, rendering cloud-dependent analytics, remote APIs, and centralized web servers unusable.
5. **Operational Accountability Vacuum:** Automated control room alerts are often logged as "sent" or "resolved," while boots-on-the-ground RPF and GRP personnel never received, acknowledged, or executed the physical barrier cordons.

---

## 2. Station Topology & Operating Envelopes

Sentinel AI models the high-density Central Railway Junction Terminal:

```
[Station Concourse H: Waiting Hall]  (Capacity: 450 pax, Inflow: 4.0/s)
              │
              ▼
[FOB Approach Corridor A: Main Overbridge]
              │
              ▼
[Bottleneck B: Platform 1-2 Staircase] ─── (T_limit = 30s) ───► [Platform Boarding G / Exit E]
              │
              │ (Naive Diversion: +2.5/s)
              ▼
[Relief Corridor R: Alternate East FOB] ─── (Breaches Limit at t=48s!) ───► REJECTED!
```

### Configured Station Zones & Constraints
- **Zone H (`Station Concourse H` — Waiting Hall Staging Area):**
  - Staging reservoir equipped with physical flow control barriers and queue holding cordons.
  - Safe Operating Limit: `450 persons`
  - Nominal baseline load: `100 persons`
  - Role: Buffer absorption for upstream concourse inflow metering.
- **Zone A (`FOB Approach Corridor A` — Main Overbridge Feeder):**
  - Elevated pedestrian walkway connecting concourse to platform descents.
  - Flow velocity: $1.2\text{ m/s}$ nominal.
- **Zone B (`Bottleneck B` — Platform 1-2 Staircase Chokepoint):**
  - Constrained vertical staircase descending onto the active platform island.
  - Configured Operating Limit: `180 persons`
  - Baseline load: `120 persons`
  - Inflow: $4.0\text{ pax/s}$; Outflow (train boarding / platform clearance): $2.0\text{ pax/s}$
  - Net accumulation rate: $+2.0\text{ pax/s}$
- **Zone G & E (`Platform Boarding G / Exit E` — Platform Edge & Circulating Egress):**
  - Platform boarding island and designated one-way ground egress gates.
- **Zone R (`Relief Corridor R` — Alternate East FOB Bypass):**
  - Secondary foot overbridge designated for emergency passenger relief.
  - Configured Operating Limit: `160 persons`
  - Baseline load: `80 persons`
  - Net clearance capacity: $0.5\text{ pax/s}$
  - Rejection dynamics: Diverting excess $2.5\text{ pax/s}$ causes load to breach 160 pax in exactly 48 seconds.

---

## 3. Grounded SOP Knowledge Layer & Copilot Integration

Sentinel AI integrates verified standard operating procedures grounded in:
1. **Indian Railways (Railway Board) Comprehensive Guidelines on Crowd Management at Railway Stations.**
2. **National Disaster Management Authority (NDMA) Guidelines — Transit Facilities (2014).**
3. **Research Designs & Standards Organisation (RDSO) Standards for Passenger Foot Overbridges.**

SOP catalog includes:
- `SOP-RAIL-FLOW-01`: Upstream Inflow Metering at Station Concourse & Waiting Hall.
- `SOP-RAIL-SAFE-02`: Secondary Bottleneck & Divergent Foot Overbridge Capacity Guard.
- `SOP-RAIL-EGRESS-03`: Foot Overbridge Unidirectional Flow & Staircase Discipline Enforcement.
- `SOP-RAIL-HOLD-04`: Station Concourse Staging & Passenger Welfare Maintenance.
- `SOP-RAIL-COMM-05`: Station Public Address (PA) & Wayfinding Display Protocol.

---

## 4. Edge Durability & Zero Cloud Dependency

Sentinel AI operates with a strict offline safety plane:
- Edge vision processing (YOLOv8) executes on local GPU/CPU.
- SQLite Write-Ahead Logging (WAL) guarantees transaction durability without internet connectivity.
- Background worker synchronizes accumulated audit events to Central Railway Command when connectivity is available using immutable UUIDs, ensuring zero duplicate entries.
