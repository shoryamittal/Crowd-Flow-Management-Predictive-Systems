# SENTINEL AI — SIH 2026 Three-Minute Winning Demo Runbook

**Document Status:** Operational Evaluation & Jury Demonstration Protocol  
**Target:** Smart India Hackathon 2026 Finals  
**Demonstration Length:** Exactly 3 Minutes (180 Seconds)  
**Presenter Team:** Team X Factor — MIT School of Computing  

---

## 1. Executive Demonstration Philosophy

The presentation is won or lost on **clarity, scientific honesty, and deterministic execution**.
Average teams show a YOLO bounding box and claim "AI predicts stampedes."
**Sentinel AI wins by demonstrating the complete operational loop**:
1. **Observe** live video honestly with uncertainty badges.
2. **Forecast** limit crossing under explicit rate assumptions.
3. **Compare** candidate actions across connected zones.
4. **Reject** an unsafe diversion that causes secondary congestion.
5. **Enforce** an auditable human-in-the-loop lifecycle.
6. **Prove** offline durability during total network collapse.

---

## 2. One-Command Launch Instructions

To launch Sentinel AI on the presentation laptop without external dependencies:

```bash
# Set environment flags (ensures offline local mode and authentic persistence)
$env:FLASK_ENV="production"
$env:SENTINEL_AUTH_ENABLED="false"
$env:SENTINEL_DB_PATH="data/sentinel.db"

# Canonical launch command
python deploy.py
```

- Access URL: `http://localhost:5000`
- Presentation browser: Chrome / Edge running in full-screen (`F11`).
- Default video replay asset: `data/demo/crowd_station.mp4`.

---

## 3. The 3-Minute Demonstration Timeline

```
+-----------------------------------------------------------------------------------------+
| [0:00 - 0:25] LIVE CCTV OBSERVATION (Sensing with Honesty & Latency)                     |
| [0:25 - 1:00] SCENARIO FORECASTING (Inspectable Math, No Fabricated Countdown)          |
| [1:00 - 1:40] DECISION SAFETY LAYER (Reject Diversion at 48s, Meter with Waiting Cost)  |
| [1:40 - 2:15] AUDITABLE LIFECYCLE (Proposed -> Approved -> Delivered -> Acknowledged)   |
| [1:40 - 2:40] VERIFICATION (Post-Action Observation Confirms Trend Reversal)             |
| [2:40 - 2:55] OFFLINE FAILSIGHT TEST (WAN Cut, Local SQLite Preserves State)             |
| [2:55 - 3:00] DEFUSED LIMITATION & SUPERVISED PILOT CLOSING                              |
+-----------------------------------------------------------------------------------------+
```

---

### Step 1 [0:00 – 0:25]: Live Observation Mode (Kumbh Sector 4 Edge Vision)
- **What the Jury Sees:**
  - Full-screen tactical dashboard displaying live edge video replay (`CAM-02: Sangam Ghat Access Bottleneck B`).
  - Active bounding boxes detecting devotees entering the riverfront access ramp.
  - Telemetry bar showing:
    - Sector: `KUMBH-SEC-04 (Sangam Triveni Ghat & Parade Ground)`
    - Source: `CAM-02 — Sangam Ghat Access Bottleneck B (YOLO)`
    - Frame Age: `< 45 ms`
    - Model: `YOLOv8s (Local TensorRT / CPU Inference)`
    - Latency: `28.4 ms`
    - Prominent Badge: `[OBSERVED CCTV SIGNAL]`
- **Speaker Script (15 s):**
  > *"Respected jury, in mass gatherings like the Maha Kumbh Mela, detecting a crowd hotspot is not enough. The next decision can save lives or simply shift the disaster onto a pontoon bridge or riverbank ramp. Here is Sentinel AI's Perception Engine running 100% locally at Sector 4. Notice we do not claim exact headcount from an uncalibrated camera; our UI explicitly tags this as an uncalibrated relative occupancy signal with a 28 millisecond edge latency."*

---

### Step 2 [0:25 – 1:00]: Synthetic Decision Scenario & Transparent Forecast
- **What the Jury Sees:**
  - Presenter toggles top-level switch from **`LIVE OBSERVATION`** to **`DECISION SCENARIO`**.
  - Dashboard loads the pre-configured **SIH Reference Scenario**.
  - Sector schematic highlights **Bottleneck B**:
    - Current Count: `120 people`
    - Operating Limit: `180 people`
    - Inflow Rate: `4.0 pax/s`, Outflow Rate: `2.0 pax/s` $\rightarrow$ Net Growth: `+2.0 pax/s`.
  - Forecast Panel computes:
    - **Time to Configured Operating Limit:** `30.0 seconds`
    - Projected Count at 90 s: `300 people`
    - Sensitivity Envelope: `[20.0 s, 46.7 s]`
    - Prominent Badge: `[SCENARIO / CALIBRATED INPUT]`
- **Action:** Presenter changes inflow from `4.0` to `5.0 pax/s`.
- **Result:** $T_{\text{limit}}$ instantly recalculates to `20.0 seconds`.
- **Speaker Script (20 s):**
  > *"Now we transition to our Decision Scenario Engine. Notice the label: this is an explicit, inspectable scenario. Under 4 people per second in and 2 out, our deterministic conservation model calculates that Bottleneck B will breach its configured limit of 180 in exactly 30 seconds, reaching 300 at 90 seconds. Notice there is no mysterious 'time-to-crush' countdown; the math is 100% transparent and inspectable."*

---

### Step 3 [1:00 – 1:40]: The Decisive Differentiator — Decision Safety Layer
- **What the Jury Sees:**
  - Three candidate intervention cards displayed side-by-side:
    1. **NO ACTION:**
       - Status: `BASELINE — UNSAFE MODELED BREACH`
       - Crosses Limit at $t = 30\text{ s}$; Reaches `300` at $90\text{ s}$.
    2. **DIVERT TO RELIEF R:**
       - Status: `RED — REJECTED`
       - **Rejection Reason:** `Receiving corridor Relief R exceeds configured operating limit at t = 48 s (Projected: 244, Limit: 160)`
    3. **UPSTREAM METERING AT HOLDING H:**
       - Status: `GREEN — FEASIBLE FOR CURRENT 90 s ANALYSIS WINDOW`
       - Bottleneck B Peak: `136 people` (mitigated at $t=8\text{ s}$)
       - Bottleneck B at 90 s: `95 people`
       - Upstream Holding Queue Added: `+205 people`
       - Holding H at 90 s: `305 people` (Safe below limit of `450`)
       - Usable Response Window: `7.0 seconds`
- **Speaker Script (30 s):**
  > *"Here is why Sentinel AI is fundamentally different. An ordinary analytics system would see Bottleneck B overcrowded and recommend: 'Divert people to Relief Corridor R.'*
  > *Our Decision Safety Layer simulates connected zones first. It simulates what happens to Relief R when 2.5 people per second are diverted there. Look at the screen:*
  > **DIVERSION TO RELIEF R — REJECTED. It breaches its limit at 48 seconds.**
  > *Instead, it recommends Upstream Metering at Holding Area H. It reduces the bottleneck to 95 people, but honestly exposes the tradeoff: Holding H queue increases by 205 people, safely within its 450 capacity. And notice: this recommendation expires in 7 seconds."*

---

### Step 4 [1:40 – 2:15]: Human Operator Lifecycle (No Auto-Ack)
- **What the Jury Sees:**
  - Presenter clicks **`[APPROVE INTERVENTION]`**.
  - Status transitions: `PROPOSED` $\rightarrow$ `APPROVED`.
  - System initiates dispatch to NDRF & Police Sector Marshals: `APPROVED` $\rightarrow$ `DELIVERED`.
  - Presenter shows the status: **`DELIVERED (Awaiting Field Acknowledgment)`**.
  - Presenter uses separate control (or simulated field device): clicks **`[ACKNOWLEDGE RECEIPT]`**.
  - Status transitions: `DELIVERED` $\rightarrow$ `ACKNOWLEDGED`.
- **Speaker Script (25 s):**
  > *"In real disaster management, automated systems must never assume an action was executed just because an API returned HTTP 200. The human remains in the loop. The operator approves the action; the system logs dispatch as DELIVERED. Crucially, the system does not auto-acknowledge. Field staff must acknowledge receipt via their terminal or radio. Only then does the audit record transition to ACKNOWLEDGED."*

---

### Step 5 [2:15 – 2:40]: Completion & Verification via Post-Action Observation
- **What the Jury Sees:**
  - Field team completes physical barrier setup: Presenter clicks **`[RECORD COMPLETION]`**.
  - Status becomes: `COMPLETED (Awaiting Trend Verification)`.
  - Presenter injects the new post-action observation frame.
  - The Decision Engine observes negative trend ($\Delta N < 0$): Bottleneck count dropping toward 95.
  - Status updates to: **`VERIFIED`**.
- **Speaker Script (20 s):**
  > *"Completion is still not verification. Sentinel AI keeps the incident open until a NEW observation arrives from the CCTV feed. Once the perception engine detects crowd density dropping in the expected direction, only then is the incident officially marked VERIFIED."*

---

### Step 6 [2:40 – 2:55]: Offline Continuity & Zero-WAN Resilience
- **What the Jury Sees:**
  - Presenter clicks **`[SIMULATE WAN DISCONNECT]`** (or pulls Ethernet / toggles Wi-Fi off).
  - Status banner turns amber: **`WAN: OFFLINE | LOCAL JOURNAL: HEALTHY (SQLite WAL) | PENDING SYNC: 1`**.
  - Presenter shows that all local charts, decisions, and history remain 100% active.
  - Presenter demonstrates that restarting the application offline recovers the exact incident UUID and lifecycle history without data loss.
- **Speaker Script (15 s):**
  > *"Now we sever WAN connectivity. During a stampede, cellular towers congest and fail. Sentinel AI is offline-first. Our safety plane, local SQLite WAL journal, and decision engine continue uninterrupted with zero internet. When WAN reconnects, pending records replay idempotently without duplicates."*

---

### Step 7 [2:55 – 3:00]: Defused Limitation & Closing Hook
- **Speaker Script (10 s):**
  > *"We do not claim to predict human injury. We demonstrate a verifiable decision loop: observe, forecast operating limits, reject dangerous congestion transfer, record the human response, and verify the outcome — completely offline. Thank you, and we welcome your questions."*

---

## 4. Rehearsed Judge Q&A Cheat Sheet

| Question | Winning Response (Under 15 Seconds) |
|---|---|
| **"What is new beyond YOLO?"** | *"YOLO only counts boxes. Our innovation is the Decision Safety Layer: simulating connected zones, checking route constraints, modeling staff delay, expiring recommendations, and providing an auditable human response trail."* |
| **"Can you predict stampedes?"** | *"No, and no one scientifically can from CCTV alone. We model when a configured operating threshold will be crossed under explicit flow rates, allowing staff to intervene before the chokepoint becomes saturated."* |
| **"What if the alternative route is also crowded?"** | *"Our Decision Safety Layer rejects it! If Relief Corridor R is crowded, diversion is rejected. If all routes fail, the system outputs 'NO FEASIBLE OPTION FOUND' and escalates to manual emergency protocols."* |
| **"How do you know staff actually acted?"** | *"We separate Delivered, Acknowledged, Completed, and Verified. Acknowledged only proves receipt; the incident is only marked Verified when subsequent CCTV observations confirm crowd reduction."* |
| **"Is this production-ready for the Kumbh Mela?"** | *"No, this is an MVP designed for a supervised sector pilot. A full rollout requires physical site geometry surveys, Kumbh Mela Administration and Police operational sign-offs, camera calibration, and DPDP privacy compliance."* |
| **"What is actually offline?"** | *"The entire local safety plane: video ingestion, YOLO inference, decision logic, and SQLite WAL persistence run locally. WAN is only used for secondary remote synchronization."* |

---

## 5. Emergency Backup Procedures
- **If Camera Fails / Lags:** Click `[LOAD SYNTHETIC REFERENCE SCENARIO]` to demonstrate all decision safety and lifecycle features deterministically.
- **If Port 5000 is Blocked:** Launch with `python deploy.py --port 5050`.
- **Pre-recorded 1080p Video Backup:** Keep `docs/backup_demo.mp4` ready on the desktop in case projector hardware or laptop display drivers fail.
