# INDIAN RAILWAYS — STATION CROWD SAFETY REFERENCE MANUAL
## HIGH-DENSITY JUNCTION TERMINAL TACTICAL DISASTER PREVENTION & OPERATIONS MANUAL
### Standard Operating Procedures, Incident Command System, and Decision Support Protocol

---

## 1. Operational Overview & Administrative Authority

- **Operational Scope:** Modeled Reference Domain for Central Railway Station Junction Terminal (Platforms 1-4, Foot Overbridges FOB-1 & FOB-2, Main Concourse Staging Hall).
- **Participating Agencies:** 
  - Indian Railways (Railway Board & Northern Railway Division)
  - Railway Protection Force (RPF Station Safety Command)
  - Government Railway Police (GRP State Police Marshals)
  - Station Director & Commercial Operations Cell
  - National Disaster Management Authority (NDMA Transit Safety Cell)
- **Problem Statement Code:** SIH26206 — High-Density Transit Crowd Disaster Prevention and Flow Pacing.
- **Governing Directives:** Indian Railways (Railway Board) Comprehensive Guidelines on Crowd Management at Railway Stations, RDSO Station Planning Standards, and NDMA Transit Guidelines (2014).

---

## 2. Station Zonal Topology & Infrastructure

Central Railway Junction Terminal is a high-density passenger interchange hub connecting suburban, express, and inter-city passenger flows across elevated foot overbridges and platform staircases.

```
       [ PLATFORMS 1-4 BOARDING ISLAND & TRACKS : Platform G (Zone 7) ]
                             ▲             │
                   Inflow    │             ▼  Egress
              [ Platform Staircase B ]  [ Alternate East FOB (Zone 5) ]
                   (Zone 3)                        │
                      ▲                            ▼
                      │                 [ Concourse Waiting Hall ]
              [ FOB Approach A ]                   (Zone 8)
                  (Zone 2)                         │
                      ▲                            ▼
                      │                 [ Circulating Area / Egress ]
              [ Concourse Staging H ]
                  (Zone 1)
                      ▲
              [ Inbound Passengers ]
```

### Zone Directory & Critical Thresholds

| Zone ID | Operational Landmark | Area (m2) | Safe Limit (pax) | Warning (pax) | Critical (pax) | Designated Response Squad |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Zone 1 | Concourse Waiting Hall H (Staging Enclosure) | 1,200 | 450 | 650 | 900 | RPF Concourse Safety Squad |
| Zone 2 | FOB Approach Corridor A (Main Overbridge Feeder) | 850 | 350 | 500 | 700 | RPF Overpass Patrol |
| Zone 3 | Platform 1-2 Staircase Chokepoint B | 600 | 250 | 380 | 550 | RPF Platform Quick Response Team |
| Zone 4 | East FOB Overpass 1 (Inbound Crossing) | 450 | 180 | 260 | 360 | GRP Overpass Cordon Squad |
| Zone 5 | East FOB Overpass 2 (Outbound Egress) | 450 | 180 | 260 | 360 | GRP Egress Marshals |
| Zone 6 | Platform 3-4 Island (Central Boarding Spine) | 700 | 280 | 420 | 600 | RPF Platform 3-4 Patrol |
| Zone 7 | Platform 1-2 Boarding Island G | 1,500 | 600 | 900 | 1,300 | RPF Platform 1-2 Task Force |
| Zone 8 | Concourse Passenger Waiting Hall & Amenities | 2,500 | 1,000 | 1,500 | 2,200 | Station Director Operations Staff |

---

## 3. Four-Tier Threat Matrix & Action Directives

Sentinel AI continuously computes spatial density and flow velocity across the 4x6 grid cells, mapping them into the 4 official NDMA / Railway Board threat tiers:

- LEVEL IV: NOMINAL / SECURE (Density < 1.5 pax/m2, T_limit > 15 min)
  * Standard camera surveillance active across all 4 channels.
  * Unrestricted transit along Concourse H, FOB Approach A, and East FOB.
  * Routine status broadcasts via Station PA speakers (Hindi, English, regional).

- LEVEL III: ELEVATED DENSITY (Density 1.5–2.5 pax/m2, T_limit 8–15 min)
  * Pre-position RPF personnel at Concourse H metering gates.
  * Pace inbound passenger groups at 2.5 pax/sec.
  * Alert platform marshals along Platform 1-2 edges.

- LEVEL II: CONGESTION DANGER (Density 2.5–3.5 pax/m2, T_limit 3–8 min)
  * RESTRICT INFLOW: Engage flow metering barriers at Concourse Waiting Hall H.
  * Activate one-way tidal flow on Foot Overbridges (No counterflow against arriving passengers).
  * Decision Safety Layer verifies downstream capacity before any rerouting.

- LEVEL I: MAXIMUM OPERATING LIMIT BREACH (Density > 3.5 pax/m2, T_limit < 3m)
  * HALT ALL INBOUND ACCESS to Platform 1-2 Staircase B immediately.
  * Open emergency egress gates to Station Circulating Area.
  * Trigger automated multi-lingual emergency evacuation broadcast.
  * Escalate Priority 1 red alert to Divisional Railway Control Room and RPF HQ.

---

## 4. Multi-Agency Human-in-the-Loop Lifecycle

To prevent automated systems from creating unsafe operational confusion, Sentinel AI implements an immutable 5-stage action lifecycle:
1. PROPOSED: When AI detects an anomaly, it simulates interventions and submits a recommended action.
2. VALIDATED: The Decision Safety Layer runs mass-conservation checks to ensure the action does not overload a secondary choke point.
3. AUTHORIZED: The Station Director or RPF Duty Officer acknowledges and authorizes the recommendation with a cryptographic timestamp.
4. EXECUTED: Field marshals deploy barriers or adjust gates. The action is logged to the local SQLite WAL incident journal.
5. RESOLVED: Sensors verify crowd density drops back below safe thresholds. Episode officially closed.

---

## 5. Offline Emergency Resilience & Failsafe Guarantee

During peak junction congestion or local telecommunication faults, Sentinel AI guarantees:
- 100% On-Premises Edge Computation: Detection, flow equations, and decision logic execute locally on the Station Command Server.
- SQLite WAL Local Durability: Zero packet loss. All incidents and operator actions are durably committed before presentation.
- Idempotent Cloud Re-sync: Once network connectivity is restored, the SyncWorker replays buffered logs without duplicating records.
