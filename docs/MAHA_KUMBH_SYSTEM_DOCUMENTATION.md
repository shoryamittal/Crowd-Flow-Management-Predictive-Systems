# SENTINEL AI — MAHA KUMBH MELA SYSTEM DOCUMENTATION
## Comprehensive Disaster Management Specification for Sector 04 (Sangam Triveni Ghat)

**Target:** Smart India Hackathon 2026 — AICTE Student Innovation — Software — Disaster Management (`SIH26206`)  
**Deployment Anchor:** Maha Kumbh Mela Prayagraj (2025–2026)  
**Primary Pilot Sector:** Sector 04 (Sangam Triveni Ghat, Parade Ground Holding Enclosures, and Pontoon Bridge Corridors)  
**Authority Reference:** `Sentinel_AI_SIH2026_Final_Strategy_Report.pdf` (Team X Factor, MIT School of Computing)  

---

## 1. Context & Operational Challenge: Maha Kumbh Mela

The **Maha Kumbh Mela** in Prayagraj represents the largest human gathering on Earth, drawing over 400 million pilgrims across a 45-day cycle, with single-day peaks exceeding 30 to 50 million devotees during auspicious bathing festivals (*Shahi Snan* / *Mauni Amavasya*).

### The Physical Disaster Challenge
1. **Extreme Asymmetric Demand:** Millions of devotees move toward a narrow sacred riverbank (Triveni Sangam Ghat) within narrow morning time windows (brahma muhurta).
2. **Topological Funnels & Dynamic Pontoon Bridges:** Deviating flow over temporary pontoon bridges (East and West Pontoons) creates lethal secondary chokepoints if the pontoon approaches saturate.
3. **The Fatal "Secondary Chokepoint" Paradox:** Traditional surveillance detects congestion at Ghat ramps and prompts security to divert crowds onto alternate routes. However, if those alternate relief routes are already near capacity or constricted by counterflow, the diversion triggers a crush at the secondary location.
4. **Cellular and Cloud Blackout:** The sheer density of 10+ million handsets in a 10 km² radius overwhelms mobile base transceiver stations (BTS), rendering cloud-dependent analytics, remote APIs, and centralized web servers completely useless.
5. **Operational Accountability Vacuum:** Automated control room alerts are often logged as "sent" or "resolved," while boots-on-the-ground police and NDRF personnel never received, acknowledged, or executed the physical barrier cordons.

---

## 2. Sector 04 Pilot Topology & Operating Envelopes

Sentinel AI models **Sector 04**, the high-density epicenter encompassing the Sangam Triveni Ghat approach:

```
[Holding Area H: Parade Ground]  (Capacity: 450 pax, Inflow: 4.0/s)
              │
              ▼
[Approach Corridor A: Sangam Marg]
              │
              ▼
[Bottleneck B: Sangam Descent Ramp] ─── (T_limit = 30s) ───► [Ghat G / Exit E: Triveni Snan]
              │
              │ (Naive Diversion: +2.5/s)
              ▼
[Relief Corridor R: East Pontoon Bridge] ─── (Breaches Limit at t=48s!) ───► REJECTED!
```

### Configured Sector Zones & Constraints
- **Zone H (`Holding Area H` — Parade Ground Staging Area):**
  - Staging reservoir equipped with physical holding pens and queue holding cordons.
  - Safe Operating Limit: `450 persons`
  - Nominal baseline load: `100 persons`
  - Role: Buffer absorption for upstream inflow metering.
- **Zone A (`Approach Corridor A` — Sangam Approach Marg):**
  - Feeder avenue connecting holding grounds to ghat access paths.
  - Flow velocity: $1.2\text{ m/s}$ nominal.
- **Zone B (`Bottleneck B` — Sangam Ghat Descent Chokepoint / Ramp):**
  - Constrained ramp descending onto the riverbank revetment.
  - Configured Operating Limit: `180 persons`
  - Baseline load: `120 persons`
  - Inflow: $4.0\text{ pax/s}$; Outflow (clearance onto sands/water): $2.0\text{ pax/s}$
  - Net accumulation rate: $+2.0\text{ pax/s}$
- **Zone G & E (`Ghat G / Exit E` — Triveni Sangam Sacred Bathing Ghat & Dispersal):**
  - Riverbank bathing platform and designated one-way dispersal corridors.
- **Zone R (`Relief Corridor R` — East Pontoon Bypass Bridge):**
  - Floating pontoon bridge designated for emergency crowd relief.
  - Configured Operating Limit: `160 persons`
  - Baseline load: `80 persons`
  - Spare clearance capacity: $0.5\text{ pax/s}$

---

## 3. The Three Analytical Engines

Sentinel AI structures crowd safety into three transparent, mathematically inspectable engines:

### Engine 1: Perception Engine (*What is happening right now?*)
- **Input:** Edge RTSP CCTV streams or licensed offline video replays (`CAM-01` Concourse H, `CAM-02` Ghat Bottleneck B, `CAM-03` Pontoon Bypass R, `CAM-04` Sector Entry Checkpoint).
- **Processing:** YOLOv8 edge detector running on local hardware (28.4 ms latency).
- **Spatial Signal:** 4×6 localized cell occupancy grid tracking relative accumulation and redistribution.
- **Honesty Seam:** Does **NOT** pretend an uncalibrated camera count is an exact headcount or venue density. Labels output honestly with `[OBSERVED CCTV SIGNAL]` alongside frame age (ms) and inference latency.

### Engine 2: Flow Forecast Engine (*What happens if nothing changes?*)
- **Model:** Deterministic mass-conservation law across connected zones:
  $$\Delta N_i = dt \times \left( \sum q_{\text{in}} - \sum q_{\text{out}} \right)$$
- **Time to Operating Limit ($T_{\text{limit}}$):**
  $$T_{\text{limit}} = \frac{C_B - N_B}{q_{\text{in}} - q_{\text{out}}} = \frac{180 - 120}{4.0 - 2.0} = \mathbf{30.0\text{ seconds}}$$
- **Sensitivity Range:** Evaluates parameter variations ($N \in [110, 130]$, $g \in [1.5, 2.5]$) yielding crossing envelope $[20.0\text{ s}, 46.7\text{ s}]$.
- **Zero Guesses:** If camera age $> 5.0\text{ s}$ or data is occluded, outputs `FORECAST UNAVAILABLE`.

### Engine 3: Decision Safety Layer (*What should we do?*)
- **Core Purpose:** Evaluate candidate field interventions across the entire connected network *before* presenting them to the Sector Magistrate.
- **Hard Safety Constraints:**
  1. **Receiving Zone Limit:** Will the diverted crowd saturate the receiving corridor?
  2. **Holding Area Limit:** Will upstream metering exceed holding pen capacity?
  3. **Route State:** Is the relief path currently `OPEN` and `VERIFIED` by police scouts?
  4. **Directionality:** Does the action violate one-way pilgrim flow rules?
  5. **Staff Delay:** Can NDRF/police deploy within the remaining operational window ($\tau_{\text{delay}} = 8\text{ s}$)?
- **Evaluation of the Reference Scenario:**
  - **No Action:** Bottleneck B reaches $300\text{ pax}$ at $90\text{ s}$ ($167\%$ overload). $\rightarrow$ **CRITICAL BREACH**.
  - **Divert to Relief R:** Diverting $2.5\text{ pax/s}$ into Relief Pontoon R causes R to cross its $160\text{ pax}$ limit at $t = 48\text{ s}$ and reach $244\text{ pax}$ at $90\text{ s}$ ($152\%$ overload). $\rightarrow$ **REJECTED BY DECISION SAFETY LAYER**.
  - **Upstream Metering at H:** Police meter entry at Parade Ground H to $1.5\text{ pax/s}$ after $8\text{ s}$ delay. Bottleneck B peaks at 136 pax and declines to $95\text{ pax}$ at $90\text{ s}$. Holding H absorbs $+205$ pilgrims ($N_H = 305 < 450$). $\rightarrow$ **FEASIBLE FOR 90s WINDOW**.

---

## 4. Multi-Agency Human Command Lifecycle

To prevent the "alert sent = problem solved" failure mode, Sentinel AI enforces an explicit, auditable six-state lifecycle:

```
[PROPOSED] ──► [APPROVED] ──► [DELIVERED] ──► [ACKNOWLEDGED] ──► [COMPLETED] ──► [VERIFIED]
```

1. **`PROPOSED`:** Decision Safety Layer identifies feasible action; displays expected impact and upstream holding cost.
2. **`APPROVED`:** Sector Magistrate or Disaster Controller authorizes the directive with cryptographic timestamp.
3. **`DELIVERED`:** Directive transmitted to NDRF / Police VHF radio handsets and terminal displays.
4. **`ACKNOWLEDGED`:** Field unit commander manually confirms receipt over tactical radio or console.
5. **`COMPLETED`:** Field marshals confirm physical barricades or metering cordons are locked in position.
6. **`VERIFIED`:** Edge vision pipeline observes post-action flow rate drop and confirms accumulation trend reversal.

---

## 5. Offline Durability & Edge Persistence

During Maha Kumbh peak days, WAN and 4G/5G connections inevitably collapse.
- **Local SQLite Write-Ahead Logging (WAL):**
  - All snapshots, incident tickets, operator approvals, and radio ACK events commit to local NVMe/SSD storage in $< 1.2\text{ ms}$.
  - Survives sudden power cuts, system reboots, and kernel panics without data corruption.
- **Zero Cloud Dependence:** Full analytics, forecasting, constraint checks, and operator UI execute on the on-premises Sector Command Laptop.
- **Idempotent Background Replay:** When WAN connectivity is restored, an asynchronous worker synchronizes accumulated audit events to the Central Kumbh Command Center using immutable UUIDs, ensuring zero duplicate entries.

---

## 6. Privacy, Ethics & Regulatory Compliance

- **Digital Personal Data Protection Act (DPDP Rules 2025):**
  - Zero facial recognition.
  - Zero pilgrim identity tracking.
  - Zero biometric profiling or mobile MAC/Bluetooth scraping.
  - In-memory frame processing with zero long-term raw video storage.
- **National Institute of Disaster Management (NIDM 2022 Guidelines):**
  - Strict compliance with crowd capacity guidelines, designated holding zones, and unidirectional flow segregation.
- **Bureau of Police Research & Development (BPR&D):**
  - Preserves chain of command, human-in-the-loop accountability, and forensic tamper-proof audit logs.

---

*Sentinel AI — Autonomous Decision Support for Mass Gathering Disaster Prevention.*  
*Team X Factor — Smart India Hackathon 2026.*
