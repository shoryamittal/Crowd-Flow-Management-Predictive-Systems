# SENTINEL AI — Failure Behavior and System Limitations

**Status:** Technical Failure Specification & Boundary Audit  
**Authority:** `Sentinel_AI_SIH2026_Final_Strategy_Report.pdf` (Section 9 & 15)  
**Target:** Smart India Hackathon 2026  

---

## 1. Core Safety Principle

> [!CAUTION]
> **Unknown is not safe.**
>
> If Sentinel AI loses trustworthy input, it must not silently convert missing or corrupted data into an assumed "all-clear" or GREEN state.
> - Missing camera frames are NOT zero crowd.
> - Stale frames are NOT live observations.
> - A non-growing queue does NOT produce an invented countdown.
> - Inadequate calibration produces `FORECAST UNAVAILABLE` — never a fabricated prediction.
> - SMS or radio dispatch is NOT successful intervention delivery.
> - Field acknowledgement is NOT proof that the danger has dissipated.

---

## 2. Deterministic Failure Behaviors

### 2.1 Stale / Frozen / Occluded / Moved Camera
- **Trigger Condition:**
  - Frame reads fail repeatedly for $\ge 3$ cycles.
  - Frame timestamps do not advance for $> 1.5\text{ s}$.
  - Repeated identical frame hash or near-zero optical difference for $> 5.0\text{ s}$ during an active operating window.
- **Required Behavior:**
  1. Transition camera state to `STALE` or `CAMERA_LOST`.
  2. Mark dependent observation snapshot as `UNRELIABLE`.
  3. Immediately invalidate dependent flow forecasts for affected zones.
  4. Emit warning banner on dashboard: `"CAMERA FEED STALE — FORECAST INVALIDATED"`.
  5. Preserve last valid observation strictly as historical reference; never project into the future using stale inputs.

### 2.2 Closed or Unverified Route
- **Trigger Condition:**
  - Route status is marked `CLOSED` (e.g., maintenance, physical obstruction, shutter down).
  - Route status is `UNVERIFIED` (route egress or clearance has not been physically validated within the shift).
- **Required Behavior:**
  1. The Decision Safety Layer automatically prunes any candidate action traversing this route during Stage 1 constraint filtering.
  2. Rejection reason explicitly logged: `"REJECTED: Route [Route_ID] is CLOSED or UNVERIFIED"`.
  3. Under no circumstances may the system recommend routing passengers onto a closed or unverified path.

### 2.3 Stable but Heavily Loaded Area
- **Trigger Condition:**
  - A crowd zone remains at high density for an extended period without active movement.
  - Learned adaptive anomaly detection might view this as "normal" background baseline.
- **Required Behavior:**
  1. Configured venue operating limits ($C$) operate **completely independently** of statistical anomaly baselines ($L/A/R$).
  2. The system must never allow a learned "busy normal" to suppress a limit breach alert.
  3. If $N \ge C$, the zone is in active breach, regardless of whether growth rate $g \approx 0$.

### 2.4 Holding Area Approaching Capacity Limit
- **Trigger Condition:**
  - Upstream holding area $H$ accumulates queued passengers approaching its configured threshold ($N_H \ge C_H \times 0.9$).
- **Required Behavior:**
  1. The Decision Safety Layer rejects further upstream metering if simulated queue addition causes $N_H(t) \ge C_H$.
  2. Rejection reason logged: `"REJECTED: Upstream Holding Area [Zone_H] exceeds capacity limit (Capacity: 450, Modeled: >450)"`.
  3. System triggers an operational escalation: `"HOLDING AREA SATURATED — ESCALATE TO SECTOR MASTER"`.

### 2.5 WAN Unavailable (Internet Loss)
- **Trigger Condition:**
  - Remote health check fails; `ConnectivityManager` transitions from `ONLINE` → `DEGRADED` → `OFFLINE`.
- **Required Behavior:**
  1. **Zero Disruption to Safety Plane:** Local frame ingestion, YOLO inference, spatial occupancy mapping, Flow Forecast Engine, and Decision Safety Layer continue running uninterrupted.
  2. Local operator dashboard remains fully functional on the local network (`http://localhost:5000` or local LAN).
  3. Incidents, decision evaluations, and operator transitions are committed synchronously to the local SQLite WAL journal.
  4. Remote synchronization queue transitions to `SYNC_PENDING`.
  5. Dashboard shows `WAN: OFFLINE | LOCAL JOURNAL: HEALTHY`.

### 2.6 Local LAN / Camera Link Unavailable
- **Trigger Condition:**
  - Local PoE switch fails or RTSP camera network becomes unreachable.
- **Required Behavior:**
  1. System explicitly surfaces `LAN / CAMERA SENSING UNAVAILABLE`.
  2. Do **NOT** claim continuous autonomous coverage; affected camera views freeze and show clear disconnection warnings.
  3. Previously committed local records and historical audit trails remain 100% durable in SQLite.

### 2.7 Power / Storage Failure Boundary
- **Trigger Condition:**
  - Host OS sudden shutdown, power failure, or disk full error.
- **Required Behavior:**
  1. SQLite WAL journaling guarantees atomic commits: either a transaction committed completely or rolls back cleanly upon restart.
  2. Upon host reboot, `IncidentJournal.initialize()` performs integrity check, runs recovery replay, and rebuilds the active in-memory state machine.
  3. The system explicitly acknowledges that in-memory frames currently in the GPU buffer during power cutoff cannot be recovered.

### 2.8 Delayed Delivery / Late Command Execution After Reconnect
- **Trigger Condition:**
  - An operator approved an intervention, but network delays or staff radio disconnect delayed field delivery until after recommendation expiry ($\text{validity\_window} \le 0$).
- **Required Behavior:**
  1. The expired action is marked `EXPIRED_DELIVERY_REJECTED`.
  2. The system refuses to execute an expired action.
  3. Operator must request a fresh Decision Safety evaluation based on current real-time observations.

### 2.9 Staff Acknowledges but Crowd Conditions Persist
- **Trigger Condition:**
  - Field team acknowledges receipt of dispatch, but new CCTV observations show congestion continuing or worsening.
- **Required Behavior:**
  1. Incident remains **OPEN**; acknowledgement proves only that field staff heard the order.
  2. State does NOT advance to `VERIFIED`.
  3. If conditions do not reverse within the expected operational window, the incident is flagged `INTERVENTION_INEFFECTIVE — ESCALATE`.

### 2.10 Inconsistent Units / Inadequate Calibration
- **Trigger Condition:**
  - Uncalibrated spatial occupancy index is passed into a function expecting calibrated people counts, or camera calibration data is missing.
- **Required Behavior:**
  1. Forecast engine refuses to calculate a false physical countdown.
  2. Returns `FORECAST UNAVAILABLE: UNCALIBRATED GEOMETRY`.
  3. Never fabricates numbers.

### 2.11 No Feasible Action Found
- **Trigger Condition:**
  - All candidate actions (No Action, Metering, Diversion) fail one or more safety constraints.
- **Required Behavior:**
  1. The Decision Safety Layer returns `status="NO_FEASIBLE_OPTION_FOUND"`.
  2. Rejection reasons for all candidates are displayed side-by-side to the operator.
  3. Emergency escalation protocol triggered: `"ALL CONFIGURED INTERVENTIONS VIOLATE CONSTRAINTS — ENGAGE MANUAL PROTOCOL"`.

---

## 3. Explicit Claims Sentinel AI Does NOT Make

To maintain strict scientific and engineering integrity before hackathon judges, the following claims are **strictly disavowed**:

1. **NO Universal Stampede Prediction:**
   Sentinel AI models mathematical conservation of people across configured corridors and operating thresholds. It does not predict human panic, biomechanical collapse, or the chaotic micro-physics of stampedes.
2. **NO Fixed Physical Countdown to Injury:**
   The system never outputs a "Time to Crush" or "90 Seconds to Disaster" countdown. It computes *"Time to configured operating limit ($T_{\text{limit}}$)"* strictly under stated inflow/outflow assumptions.
3. **NO Global "Optimal Routing":**
   Sentinel AI does not claim global network optimality. It *compares finite, pre-approved candidate interventions* and weeds out those that violate safety constraints.
4. **NO Autonomous Actuation:**
   Sentinel AI does not actuate motorized turnstiles, drop physical gates, or override human authority. Every action requires human approval and confirmation.
5. **NO Production Readiness for Live Kumbh:**
   This system is an MVP prototype for a supervised sector pilot. A full production rollout requires surveyed physical geometry, RPF operational sign-offs, camera calibration, and legal DPDP compliance validation.
6. **NO "100% Guaranteed" Casualty Prevention:**
   Disaster management is probabilistic and human-dependent. The system provides decision support, constraint checking, and auditable accountability.
