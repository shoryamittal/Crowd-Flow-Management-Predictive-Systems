# SENTINEL AI — Final Strategy Source of Truth

**Document Status:** Locked Architecture Specification  
**Authority:** `Sentinel_AI_SIH2026_Final_Strategy_Report.pdf` (17-page Final Strategy Report, 09 Sep 2026)  
**Target:** Smart India Hackathon 2026 (Software Edition)  
**Registered Track / Theme:** AICTE Student Innovation — Software — Disaster Management (`SIH26206`)  
**Team:** Team X Factor — MIT School of Computing  

---

## 1. Absolute Product Thesis

> [!IMPORTANT]
> **Sentinel AI is NOT a universal stampede predictor.**
>
> It is:
> **an offline-first crowd-flow decision-support system that observes developing crowd conditions, forecasts configured operating-limit crossings, compares finite pre-approved interventions, rejects actions that transfer congestion into another constrained zone, records the human response, and verifies the observed outcome.**

Sentinel AI must **never** be pitched as "AI predicts stampedes" or "eliminates crowd crushes." It is an operational decision-support tool for **Sector Magistrates, Kumbh Mela Disaster Management Authorities, NDRF commanders, and police coordinators** managing mass gatherings (specifically piloted for **Maha Kumbh Mela Prayagraj Sector 04 — Sangam Triveni Ghat**, with the earlier Indian Railways transit prototype retained as prior laboratory evidence).

### Competitive Positioning in One Sentence
> **"Most crowd systems tell you where congestion is high. Sentinel asks the next operational question: if I move this crowd somewhere else, will I create the next dangerous bottleneck?"**

---

## 2. Problem Definition & Operational Gap

### The Real-World Disaster-Management Problem
During peak mass-gathering windows, people enter a corridor faster than downstream infrastructure can clear them. When localized congestion spikes:
1. **Unchecked Diversions Cause Catastrophic Transfers:** Moving people away from one bottleneck often shunts them into an already constrained relief corridor or staircase, simply moving the danger and precipitating a stampede at the secondary chokepoint.
2. **Alerts Disconnect from Field Reality:** Control-room warnings and automated dispatches are routinely treated as "handled," yet field staff never received or executed the order.
3. **Severe Connectivity Fragility:** WAN connections flap or collapse completely during peak mass gatherings, blinding cloud-dependent analytics and centralized dashboards.

### What Sentinel AI Is NOT
- **NOT** a universal stampede or injury predictor.
- **NOT** a claim that crowd crush can be predicted at a fixed physical countdown (e.g., "90 seconds to crush").
- **NOT** a fully calibrated Kumbh or railway digital twin.
- **NOT** autonomous physical crowd control (no automated gate closures or robotic barrier overrides).
- **NOT** an all-disaster general platform.

### Evidence Grounding (Indian Guidelines)
- **NIDM Crowd-Management Training Module (2022):** Demands designated holding areas, transport-arrival pacing, clear operational roles, and coordinated flow controls.
- **BPR&D Guidelines on Crowd Control and Mass Gathering Management:** Mandates pre-agreed actions, unified command authority, and verifiable audit trails.
- **Ministry of Railways Operational Measures (19 Mar 2025):** Emphasizes upstream holding areas, access regulation, unidirectional movement corridors, and emergency war rooms.

---

## 3. Product Scope & Operational Boundaries

### Scope of the Final MVP
- **Operational Sector:** One mass-gathering sector configured as approximately six named zones (modeled on **Maha Kumbh Mela Prayagraj — Sector 04 Sangam Triveni Ghat**):
  - **Holding Area (H):** Controlled staging reservoir with configured capacity (e.g., *Parade Ground Pilgrim Staging Enclosure*, limit 450 pax).
  - **Approach Corridor (A):** Feeder pathway into the primary chokepoint (e.g., *Sangam Approach Marg*).
  - **Bottleneck (B):** Constrained passage (e.g., *Sangam Ghat Descent Ramp*, limit 180 pax).
  - **Ghat / Downstream Area (G):** Primary sacred bathing destination (*Triveni Sangam Snan Ghat*).
  - **Relief Corridor (R):** Pre-designated alternate bypass corridor (e.g., *East Pontoon Bridge Bypass*, limit 160 pax).
  - **Exit / Dispersal (E):** Final egress clearing zone toward mela perimeter.
- **Intervention Comparison:** Compares a finite set of pre-approved candidate interventions:
  1. `NO ACTION` (Baseline — Bottleneck B crosses limit in 30s, reaches 300 pax at 90s)
  2. `UPSTREAM METERING` (Pacing inflow at Holding H to 1.5 pax/s after 8s staff delay to protect Bottleneck B; B drops to 95 pax, H absorbs +205 queue)
  3. `PERMITTED DIVERSION` (Diverting 2.5 pax/s into Relief Corridor R — REJECTED because R breaches limit at $t=48\text{ s}$)
- **Decision Safety Layer:** Simulates connected zones before recommending any action. Rejects any intervention that triggers secondary limit breaches, traverses closed or unverified paths, or exceeds holding capacity.
- **Human In The Loop:** Closed-loop human operator lifecycle:
  `PROPOSED` → `APPROVED` → `DELIVERED` → `ACKNOWLEDGED` → `COMPLETED` → `VERIFIED`
- **Offline Reliability:** Operates 100% locally with camera/replay and SQLite WAL persistence. Remote WAN synchronization is secondary and asynchronous.

---

## 4. Evidence Modes & Data Integrity Rules

The system enforces a strict seam between sensing uncertainty and deterministic modeling.

| Evidence Mode | Input Source | What Sentinel May Claim | Mandatory UI Badge |
|---|---|---|---|
| **Live Observation Mode** | Real camera or licensed replay through local YOLO / OpenCV pipeline | "This is what our current vision pipeline observes." Reports frame age, model/device, processing latency, and relative spatial change. | `OBSERVED CCTV SIGNAL` |
| **Decision Scenario Mode** | Timestamped manual, calibrated, or explicitly synthetic zone counts/flows | "Under these stated assumptions, this is how connected zones evolve and which actions violate constraints." | `SCENARIO / CALIBRATED INPUT` (Must visibly say `SYNTHETIC`) |
| **Future Calibrated Mode** | Site geometry + manually annotated camera ground-truth + route flow calibrations | Calibrated headcount/density/flow only after empirical validation against held-out field observations. | `CALIBRATED SITE MODE` |

### Non-Negotiable Display Rule
Every displayed numeric metric must state:
1. **Value**
2. **Unit**
3. **Timestamp**
4. **Source**
5. **Evidence Status:** `OBSERVED`, `CALCULATED`, `SCENARIO`, or `PLANNED`
6. **Calibration/Quality State:** `UNCALIBRATED`, `CALIBRATED`, `STALE`, or `DEGRADED`

> [!CAUTION]
> If unit, calibration, or freshness is inadequate for a requested calculation, the output MUST be **`FORECAST UNAVAILABLE`** — never an invented countdown or guessed metric.

---

## 5. Words and Claims Forbidden vs Approved

| Forbidden / Words to AVOID | Reason | Approved Terminology to USE |
|---|---|---|
| `"AI predicts stampedes"` | False claim; no system predicts human injury or physics of stampedes from CCTV. | `"Action-aware crowd intelligence"` |
| `"Time to crush"` / `"time-to-crush"` | Sensationalist, unproven, physical impossibility from camera feed. | `"Time to configured operating limit"` |
| `"Optimal routing"` | Implies global mathematical optimality without network knowledge. | `"Compares configured candidate actions"` |
| `"100% effective"` / `"eliminates crowd crush"` | Reckless safety claim. | `"Decision-support within configured operating envelope"` |
| `"90-second guaranteed warning"` | Unscientific guarantee; depends entirely on inflow velocity and camera. | `"Short-horizon forecast under stated assumptions"` |
| `"exactly where and when"` | Overclaim. | `"Identifies modeled limit crossing windows"` |
| `"Zero dependency / fully offline"` | Dishonest if local camera, LAN, or power is still required. | `"Local functions continue without WAN"` |
| `"First AI crowd system"` | False; commercial analytics and Kumbh AI have existed for years. | Focus on `"Decision Safety Layer & auditability"` |
| `"Production ready for Kumbh"` | Prototype requires site survey, calibration, and operational sign-off. | `"Supervised pilot prototype"` |
| `"95% confidence"` | Statistically fraudulent without empirical error distribution calibration. | `"Sensitivity range under stated assumptions"` |

---

## 6. Engineering Audit: Reuse, Remove, Defer

### 6.1 Features to REUSE (Real Foundations)
- **Local Vision Pipeline:** Python, Flask, OpenCV, YOLO detector (`PersonDetector`) feeding the local runtime.
- **Spatial Change Signal:** 4×6 grid, relative load/accumulation/redistribution indicators, occupancy index (retained strictly as a relative change indicator, NOT people/m²).
- **Local Incident Persistence:** SQLite with WAL mode, stable UUIDs, local acknowledgement, retry queue, replay architecture.
- **Operator Dashboard:** Existing Flask template structure and judge-facing UI layout (refactored for the decision loop).

### 6.2 Features to REMOVE or RELABEL
1. **Severity-based fixed "time to crush" countdown:** REMOVE. Replace with calculated time to configured operating limit from timestamped rate and count inputs.
2. **Fixed Fruin LOS percentages and speeds:** REMOVE from technical evidence views or label clearly as `SCENARIO / ILLUSTRATIVE`.
3. **Synthetic secondary cameras / mock train schedules:** Label `SYNTHETIC` or `MANUAL SCENARIO INPUT` on every view.
4. **Dispatch API auto-setting `ack_received=True`:** REMOVE. Implement real manual lifecycle states.
5. **Decorative randomized flow particles:** Keep strictly as cosmetic animation or remove from technical views so judges do not confuse them with physics simulation.

### 6.3 Features Explicitly DEFERRED (Do Not Burn Deadline Here)
- CSRNet / LSTM / GNN deep density replacements without site training data.
- Full physical pedestrian continuous digital twin.
- React frontend rewrite (keep Flask SSR).
- WhatsApp / SMS / voice assistant integrations.
- Live telecom or live IRCTC API integrations.
- Facial recognition, pilgrim identity tracking, or biometric profiling.
- Automated barrier actuation or robotic crowd controls.

---

## 7. Privacy, Governance & Ethics

- **DPDP Rules (2025):** The prototype does not claim formal statutory certification. Deployment is subject to venue permissions and applicable Digital Personal Data Protection Act compliance.
- **No Individual Tracking:** Strictly aggregate spatial analytics; zero facial recognition, zero biometric profiling, zero religious/demographic classification.
- **Ephemeral Video:** No long-term raw video storage; processing occurs in-memory at the edge.
- **Auditable Accountability:** Every intervention transition documents actor ID, timestamp, and decision rationale.

---

## 8. Final Acceptance Checklist (Non-Negotiable Gates)

- [ ] Exact registered problem statement ID (`SIH26206`) used; no fabricated metadata.
- [ ] No hard-coded "time to crush" or fake countdowns.
- [ ] Every metric carries `Observed` / `Calculated` / `Scenario` / `Planned` badge with unit and timestamp.
- [ ] Live camera / replay path works locally with reported frame age and latency.
- [ ] Decision Safety Layer evaluates connected zones and rejects unsafe diversions.
- [ ] Diversion to Relief R is rejected by deterministic calculation because R breaches limit at $t=48\text{ s}$.
- [ ] Upstream metering calculation reproduces the exact worked example (B drops to 95 at 90s, H absorbs +205).
- [ ] Waiting cost of metering is prominently displayed (+205 holding queue).
- [ ] Route closure, stale observation, and unverified route constraints reject candidates.
- [ ] Proposed → Approved → Delivered → Acknowledged → Completed → Verified lifecycle is manual and distinct.
- [ ] Dispatch does NOT automatically mark Acknowledged.
- [ ] Post-action observation is required before an incident is Verified.
- [ ] SQLite WAL persistence survives simulated crash/restart without losing records or altering UUIDs.
- [ ] Local decision support and incident creation continue with zero WAN connectivity.
- [ ] Reconnection replays pending sync without generating duplicate incident records.
