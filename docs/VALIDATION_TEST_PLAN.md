# SENTINEL AI — Validation and Test Plan

**Status:** Executable Verification Matrix & Test Specification  
**Authority:** `Sentinel_AI_SIH2026_Final_Strategy_Report.pdf` (Sections 10 & 18)  
**Target:** Smart India Hackathon 2026  

---

## 1. Evidence Separation Axiom

> [!IMPORTANT]
> **Evidence layers must remain separate:**
> - **Software tests** do NOT prove **vision accuracy**.
> - **Vision accuracy** does NOT prove **forecast quality**.
> - **Forecast quality** does NOT prove **intervention effectiveness**.
> - **Intervention logic** does NOT prove **real-world casualty reduction**.
>
> We do not use one layer as proof of another. If a metric has not been empirically measured on-site, the system reports **`EVALUATION PLAN`**, never a fabricated achievement.

---

## 2. Mandatory Pass/Fail Gates (Non-Negotiable)

Every gate below must pass unconditionally before declaring implementation complete:

| Gate # | Non-Negotiable Pass/Fail Requirement | Target Test / Verification | Status |
|---|---|---|---|
| **GATE-01** | A closed route is never recommended under any condition. | `tests/test_decision_safety.py::test_closed_route_rejected` | MANDATORY |
| **GATE-02** | An unverified or stale route is never recommended. | `tests/test_decision_safety.py::test_unverified_route_rejected` | MANDATORY |
| **GATE-03** | A receiving area that would exceed its operating limit rejects the diversion. | `tests/test_decision_safety.py::test_receiving_overload_rejects_diversion` | MANDATORY |
| **GATE-04** | A non-growing queue ($g \le 0$) produces no invented countdown. | `tests/test_forecast_engine.py::test_zero_growth_produces_no_countdown` | MANDATORY |
| **GATE-05** | Camera failure or stale frames invalidate dependent forecasts. | `tests/test_forecast_engine.py::test_stale_camera_invalidates_forecast` | MANDATORY |
| **GATE-06** | No dispatch API call automatically marks an action as `ACKNOWLEDGED`. | `tests/test_action_lifecycle.py::test_dispatch_does_not_auto_acknowledge` | MANDATORY |
| **GATE-07** | Field acknowledgement does not automatically verify the outcome. | `tests/test_action_lifecycle.py::test_acknowledgement_does_not_verify_outcome` | MANDATORY |
| **GATE-08** | All synthetic values and mock feeds are visibly labeled `SYNTHETIC`. | `tests/test_ui_evidence_badges.py::test_synthetic_scenarios_have_watermark` | MANDATORY |
| **GATE-09** | Worked synthetic scenario reproduces exact arithmetic from the Strategy Report. | `tests/test_sih_reference_scenario.py::test_reference_scenario_exact_math` | MANDATORY |
| **GATE-10** | Upstream metering displays its added waiting/queue cost (+205). | `tests/test_sih_reference_scenario.py::test_metering_displays_waiting_cost` | MANDATORY |
| **GATE-11** | System correctly outputs `"NO FEASIBLE OPTION FOUND"` when all actions violate constraints. | `tests/test_decision_safety.py::test_all_constraints_violated_returns_no_feasible` | MANDATORY |
| **GATE-12** | Recommendation expiry is enforced; expired actions cannot be executed. | `tests/test_action_lifecycle.py::test_expired_recommendation_rejected` | MANDATORY |
| **GATE-13** | Local decision support and incident creation continue 100% offline without WAN. | `tests/test_offline_continuity.py` + `tests/test_round2_end_to_end.py` | MANDATORY |
| **GATE-14** | Process restart preserves successfully committed incident/action state and UUIDs. | `tests/test_local_alert_restart.py` + `tests/test_offline_action_persistence.py` | MANDATORY |
| **GATE-15** | Post-action verification strictly requires a subsequent CCTV observation. | `tests/test_action_lifecycle.py::test_verification_requires_subsequent_observation` | MANDATORY |
| **GATE-16** | Every judge-facing metric has value, unit, timestamp, and evidence status badge. | `tests/test_ui_evidence_badges.py::test_metrics_carry_provenance` | MANDATORY |

---

## 3. Test Suites & Verification Scope

### 3.1 Unit Test Suite: Flow Forecast Engine (`tests/test_forecast_engine.py`)
1. **Conservation of People:** Verify $\sum N_i(t+dt) = \sum N_i(t) + dt \cdot (\text{external arrivals} - \text{external departures})$.
2. **Transfer Symmetry:** Verify flow from Zone A to Zone B is simultaneously subtracted from A and added to B.
3. **Outflow Clamping:** Outflow from zone cannot exceed available people in that zone.
4. **Positive Growth Crossing:** Verify $T_{\text{limit}} = (C - N)/g$ for $N < C$ and $g > 0$.
5. **Current Limit Breach:** Verify $N \ge C$ immediately reports current breach.
6. **Zero or Negative Growth:** Verify $g \le 0$ reports no modeled limit crossing within horizon.
7. **Overload Visibility:** Overloaded zones are not artificially capped at $C$ (modeled accumulation must be visible).
8. **Invalid Inputs:** Verify stale inputs, missing calibration, or inconsistent units return `FORECAST UNAVAILABLE`.

### 3.2 Unit & Integration Suite: Decision Safety Layer (`tests/test_decision_safety.py`)
1. **Route Closure Check:** Candidate action traversing a closed route is rejected with reason.
2. **Route Unverified Check:** Candidate traversing unverified path is rejected.
3. **Directionality Check:** Contraflow action is rejected.
4. **Receiving Zone Overload:** Action routing into a zone that breaches capacity within horizon is rejected.
5. **Holding Capacity Breach:** Action that overloads upstream reservoir is rejected.
6. **Staff Response Delay:** Modeling incorporates 8-second delay before intervention takes physical effect.
7. **Action Ranking:** Feasible actions are ranked by worst modeled overload, waiting cost, and complexity.
8. **No Feasible Option:** When all candidates fail, returns `NO FEASIBLE OPTION FOUND`.

### 3.3 Reference Scenario Test: Exact Arithmetic (`tests/test_sih_reference_scenario.py`)
Validates the official SIH 2026 worked demonstration example:
- **Baseline (No Action):**
  - $B_{\text{initial}} = 120$, $C_B = 180$, $g = +2\text{ pax/s}$.
  - $T_{\text{limit}} = (180 - 120) / 2 = 30\text{ seconds}$.
  - $B(90\text{ s}) = 120 + 2 \times 90 = 300\text{ people}$.
- **Candidate 1 (Upstream Metering):**
  - $\tau_{\text{delay}} = 8\text{ s}$.
  - $B(8\text{ s}) = 120 + 2 \times 8 = 136\text{ people}$ (Peak).
  - Inflow throttled to $1.5\text{ pax/s}$, outflow $2.0\text{ pax/s}$, net growth $-0.5\text{ pax/s}$.
  - $B(90\text{ s}) = 136 - 0.5 \times 82 = 95\text{ people}$.
  - Holding queue added: $2.5\text{ pax/s} \times 82\text{ s} = 205\text{ people}$.
  - $H(90\text{ s}) = 100 + 205 = 305\text{ people}$ (Safe below $C_H = 450$).
  - Status: **FEASIBLE FOR CURRENT 90 s ANALYSIS WINDOW**.
- **Candidate 2 (Diversion to Relief R):**
  - $R_{\text{initial}} = 80$, $C_R = 160$, spare clearance $0.5\text{ pax/s}$.
  - Diverted inflow: $2.5\text{ pax/s}$; net growth in R: $+2.0\text{ pax/s}$.
  - Time to limit in R: $8\text{ s} + (160 - 80) / 2.0 = 48\text{ seconds}$.
  - $R(90\text{ s}) = 80 + 2.0 \times 82 = 244\text{ people}$.
  - Status: **REJECTED — Receiving corridor exceeds configured operating limit at t = 48 s**.
- **Sensitivity Envelope:**
  - $N \in [110, 130]$, $g \in [1.5, 2.5]\text{ pax/s}$.
  - Earliest modeled crossing: $T_{\min} = (180 - 130) / 2.5 = 20\text{ seconds}$.
  - Response delay: $8\text{ s}$, planning margin: $5\text{ s}$.
  - Usable response window: $20 - 8 - 5 = 7\text{ seconds}$.

### 3.4 Action Lifecycle Suite (`tests/test_action_lifecycle.py`)
1. **Transition Progression:** Enforce `PROPOSED` → `APPROVED` → `DELIVERED` → `ACKNOWLEDGED` → `COMPLETED` → `VERIFIED`.
2. **Dispatch Non-Equivalence:** Calling dispatch sets `DELIVERED` and explicitly does NOT set `ACKNOWLEDGED`.
3. **Acknowledgement Non-Equivalence:** Setting `ACKNOWLEDGED` does NOT mark `COMPLETED` or `VERIFIED`.
4. **Observation Requirement:** Setting `VERIFIED` requires providing an `ObservationSnapshot` confirming negative trend in the bottleneck.
5. **Persistent History:** Every transition records timestamp, actor ID, and audit note.

### 3.5 Offline Resilience & Restart Suite (`tests/test_offline_action_persistence.py`)
1. Sever network; create new incident and proposed action offline.
2. Advance action through `APPROVED`, `DELIVERED`, and `ACKNOWLEDGED`.
3. Verify SQLite commit succeeds with WAL checkpoint.
4. Terminate process; restart server from scratch.
5. Reload incident and action; verify exact UUIDs, timestamps, and states survive intact.
6. Reconnect network; verify idempotent background replay synchronizes event without creating duplicates.

---

## 4. Empirical Evaluation Protocol (Beyond Code Tests)

| Evaluation Layer | Diagnostic Protocol | Target Metric / Report Evidence |
|---|---|---|
| **Vision Diagnostic** | 6 short permitted clips: Ordinary, Dense, Low-light, Occlusion, Motion, Empty. 10 labeled frames per clip (60 total). | Count MAE, Signed undercount, Frame resolution, Hardware device, p50/p95 latency (ms). |
| **Forecast Quality** | 20 saved synthetic flow scenarios. Compare deterministic conservation model against rolling-trend baseline. | 15s/30s/60s prediction errors, Crossing time error, False/missed warnings, Sensitivity coverage. |
| **Decision Safety** | Varied parameter matrix (inflow rates, response delays, corridor limits). | Constraint violation rejection rate (100%), Avoided downstream overloads, Queue costs. |
| **Operational Usability** | Single-blind walkthrough with unfamiliar evaluator (e.g., student peer or faculty reviewer). | Task completion time, Operator misinterpretations, Action selection clarity. |
