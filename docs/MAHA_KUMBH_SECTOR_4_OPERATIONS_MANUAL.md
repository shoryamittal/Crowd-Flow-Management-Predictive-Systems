# MAHA KUMBH MELA PRAYAGRAJ 2025–2026
## SECTOR 04 TACTICAL DISASTER PREVENTION & OPERATIONS MANUAL
### Standard Operating Procedures, Incident Command System, and Decision Support Protocol

---

## 1. Operational Overview & Administrative Authority

- **Deployment Scope:** Maha Kumbh Mela Prayagraj (2025–2026), Sector 04 (Sangam Confluence & Approaches).
- **Participating Agencies:** 
  - Uttar Pradesh Police (Mela Administration)
  - National Disaster Response Force (NDRF 11th Battalion)
  - State Disaster Response Force (SDRF)
  - Uttar Pradesh Jal Police (River Rescue Fleet)
  - District Magistrate & Kumbh Mela Adhikari Command Cell
  - Indian Railways (Prayagraj Junction & Naini Inflow Coordination)
- **Problem Statement Code:** SIH26206 — Mass-Gathering Crowd Disaster Prevention and Flow Pacing.
- **Governing Directives:** NDMA Crowd Management Guidelines (2014), BPR&D Guidelines for Mass Gatherings, and UP State Disaster Management Plan.

---

## 2. Sector 04 Zonal Topology & Infrastructure

Sector 04 is the single highest-density pilgrimage zone in the world, covering the sacred confluence of the Ganga, Yamuna, and mythical Saraswati rivers.

`
       [ GANGA - YAMUNA CONFLUENCE : SANGAM SNAN GHAT (Zone 7) ]
                            ▲             │
                  Inflow    │             ▼  Egress
             [ Sangam Approach ]      [ Pontoon Bridge 4 (Zone 5) ]
                  (Zone 3)                        │
                     ▲                            ▼
                     │                 [ Parade Ground Staging ]
             [ Triveni Marg ]                  (Zone 8)
                 (Zone 2)                         │
                     ▲                            ▼
                     │                 [ Medical Post 4 / Egress ]
             [ Holding Area 4 ]
                 (Zone 1)
                     ▲
             [ Inbound Devotees ]
`

### Zone Directory & Critical Thresholds

| Zone ID | Operational Landmark | Area (m2) | Safe Limit (pax) | Warning (pax) | Critical (pax) | Designated Response Squad |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Zone 1 | Holding Area 4 (Staging Enclosure) | 1,200 | 450 | 650 | 900 | Squad Alpha (UP Police / SDRF) |
| Zone 2 | Triveni Marg (West Inflow Corridor) | 850 | 350 | 500 | 700 | Squad Bravo (4 Marshals) |
| Zone 3 | Sangam Approach (Confluence Feeder) | 600 | 250 | 380 | 550 | Squad Charlie (6 NDRF personnel) |
| Zone 4 | Pontoon Bridge 3 (Inbound Crossing) | 450 | 180 | 260 | 360 | Jal Police & PWD River Team |
| Zone 5 | Pontoon Bridge 4 (Outbound Return) | 450 | 180 | 260 | 360 | Squad Delta (Pontoon Marshals) |
| Zone 6 | Akshayavat Parikrama (Circular Path) | 700 | 280 | 420 | 600 | Temple Corridor Security |
| Zone 7 | Main Sangam Snan Ghat (Sacred Confluence) | 1,500 | 600 | 900 | 1,300 | NDRF QRT & Deep Water Divers |
| Zone 8 | Parade Ground Transit & Medical Camp 4 | 2,500 | 1,000 | 1,500 | 2,200 | DM Coordination & Health Dept |

---

## 3. Four-Tier Threat Matrix & Action Directives

Sentinel AI continuously computes spatial density and flow velocity across the 4x6 grid cells, mapping them into the 4 official NDMA threat tiers:

- LEVEL IV: NOMINAL / SECURE (Density < 1.5 pax/m2, T_limit > 15 min)
  * Standard camera surveillance active across all 4 channels.
  * Unrestricted transit along Triveni Marg and Pontoon Bridges 3 & 4.
  * Routine status broadcasts via Sector 4 PA speakers (Hindi & English).

- LEVEL III: ELEVATED DENSITY (Density 1.5–2.5 pax/m2, T_limit 8–15 min)
  * Pre-position Squad Alpha at Holding Area 4 metering gates.
  * Pace inbound devotee groups at 2.5 pax/sec.
  * Alert NDRF boat patrols along Sangam bathing steps.

- LEVEL II: CONGESTION DANGER (Density 2.5–3.5 pax/m2, T_limit 3–8 min)
  * RESTRICT INFLOW: Engage pneumatic hold gates at Holding Area 4.
  * Activate one-way tidal flow on Pontoon Bridges (No reverse flow allowed).
  * Decision Safety Layer verifies downstream capacity before any rerouting.

- LEVEL I: MAXIMUM OPERATING LIMIT BREACH (Density > 3.5 pax/m2, T_limit < 3m)
  * HALT ALL INBOUND ACCESS to Sangam Ghat Ramp immediately.
  * Open emergency egress gates to Parade Ground transit artery.
  * Trigger automated multi-lingual emergency evacuation broadcast.
  * Escalate Priority 1 red alert to Kumbh Central War Room and NDRF HQ.

---

## 4. Multi-Agency Human-in-the-Loop Lifecycle

To prevent automated systems from creating unsafe operational confusion, Sentinel AI implements an immutable 5-stage action lifecycle:
1. PROPOSED: When AI detects an anomaly, it simulates interventions and submits a recommended action.
2. VALIDATED: The Decision Safety Layer runs mass-conservation checks to ensure the action does not overload a secondary choke point.
3. AUTHORIZED: The Sector Magistrate or NDRF Commander acknowledges and authorizes the recommendation with a cryptographic timestamp.
4. EXECUTED: Field marshals deploy barriers or adjust gates. The action is logged to the local SQLite WAL incident journal.
5. RESOLVED: Sensors verify crowd density drops back below safe thresholds. Episode officially closed.

---

## 5. Offline Emergency Resilience & Failsafe Guarantee

During the Maha Kumbh Mela, cell towers regularly collapse under the load of millions of concurrent devotees. Sentinel AI guarantees:
- 100% On-Premises Edge Computation: Detection, flow equations, and decision logic execute locally on the Sector Command NVR.
- SQLite WAL Local Durability: Zero packet loss. All incidents and operator actions are durably committed before presentation.
- Idempotent Cloud Re-sync: Once 4G/WAN or satellite backhaul restores, the SyncWorker replays buffered logs without duplicating records.
