# SENTINEL AI — Implementation Gap Analysis

**Status:** Pre-Migration Technical Reconnaissance & Gap Matrix  
**Authority:** `Sentinel_AI_SIH2026_Final_Strategy_Report.pdf` vs. Active Sentinel Codebase  
**Baseline Git Commit:** `eb46093` on `main`  
**Test Suite Baseline:** 97 passed in 48.04s (100% pass rate)  

---

## 1. Executive Summary of Codebase State

The Sentinel AI repository contains a mature, robust foundation built during Round 2 development:
- A high-reliability **Safety Plane** (`SentinelRuntime`, `FrameSource`, `PersonDetector`, `ContinuousMonitor`).
- A rock-solid **Continuity Plane** (`IncidentJournal` in SQLite with WAL, `SyncWorker`, `ConnectivityManager` with hysteresis).
- A 19-file test suite with 97 passing tests verifying offline resilience, idempotency, and crash recovery.

However, to align with the **Final SIH 2026 Strategy Report**, several critical gaps must be bridged:
1. **Missing Core Differentiator:** The repository currently lacks the **Decision Safety Layer** that simulates connected zones, verifies route constraints, and rejects dangerous diversions.
2. **Missing Deterministic Flow Forecast Engine:** Inflow/outflow conservation over a 90-second horizon and $T_{\text{limit}} = (C - N)/g$ calculations are not currently hooked up to the runtime or dashboard.
3. **Misleading Old Features in UI:**
   - Severity-based fixed countdowns / "time to crush" references in `templates/index.html`.
   - Fixed Fruin Level of Service (LOS) cards with hard-coded compression risks (e.g., `4.2% MINIMAL`).
   - The RPF dispatch API in `deploy.py` automatically sets `"ack_received": True`.
   - Randomized grid flow particles in `src/core/flow_simulation.py`.
   - Mock railway schedules in `src/core/railway_integration.py` presented without clear synthetic badges.
4. **Missing Evidence Badges:** Displayed metrics do not systematically convey `OBSERVED`, `CALCULATED`, `SCENARIO`, or `PLANNED` provenance.
5. **Incomplete Human Operator Lifecycle:** Dispatches do not enforce distinct manual transitions for `APPROVED`, `DELIVERED`, `ACKNOWLEDGED`, `COMPLETED`, and `VERIFIED`.

---

## 2. Comprehensive Implementation Gap Matrix

| Component | Current Repository Behavior | Final Strategy PDF Requirement | Identified Gap | Files Involved | Change Required | Risk Level | Validation Test Required |
|---|---|---|---|---|---|---|---|
| **Perception Engine & Evidence Labeling** | `PersonDetector` runs YOLOv8, maps boxes to 4×6 grid, computes relative occupancy index and L/A/R metrics. Labeling is generic. | Must explicitly present `OBSERVED CCTV SIGNAL` badge with source, frame age in ms, device/model, and calibration state (`UNCALIBRATED`). Never call proxy "people/m²". | Current UI does not clearly label detector output as an uncalibrated proxy with an `OBSERVED` badge. | `src/detector.py`, `src/runtime.py`, `deploy.py`, `templates/index.html` | Surface `ObservationSnapshot` with explicit `OBSERVED` status, frame age, and latency in UI. | LOW | Verify `OBSERVED` badge appears and uncalibrated index is not described as people/m². |
| **Flow Forecast Engine** | `src/core/prediction.py` contains deprecated least-squares `DensityPredictor`. `deploy.py` intentionally does not import it. | Small, deterministic, inspectable conservation model: $\Delta N = dt \cdot (\text{inflow} - \text{outflow})$, $T_{\text{limit}} = (C-N)/g$, sensitivity envelope. | No deterministic conservation forecast engine hooked to live decision loop. | `src/decision/forecast.py` [NEW], `deploy.py`, `templates/index.html` | Implement `FlowForecastEngine` with exact conservation math, no stochastic jitter, no artificial clipping. | MED | `test_forecast_conservation`, `test_crossing_time`, `test_sensitivity_envelope`. |
| **Decision Safety Layer** | System identifies hotspots (`hotspot: r1c3`) and outputs fixed rule-based strings (`recommended_action: Divert...`). Does NOT evaluate connected zones. | Must simulate connected zones for all candidate actions (`NO ACTION`, `METERING`, `DIVERSION`), check constraints (route closed, stale, direction, capacity), and reject congestion transfer. | Complete absence of connected-zone consequence simulation and diversion rejection. | `src/decision/safety.py` [NEW], `src/decision/models.py` [NEW], `deploy.py` | Build `DecisionSafetyEngine` implementing Stage 1 constraint filtering and Stage 2 ranking. | HIGH | `test_diversion_rejected_due_to_receiving_overload`, `test_metering_feasible_with_queue_cost`. |
| **Reference Scenario Implementation** | No saved reference scenario matching the SIH 2026 worked example. | Must reproduce the 90s reference scenario: Bottleneck B starts 120, limit 180, net +2/s; No action crosses at 30s; Metering at 8s drops B to 95 at 90s, adds +205 to H; Diversion to R breaches R at 48s and is REJECTED. | No implementation of the reference scenario in backend or frontend. | `src/decision/scenario.py` [NEW], `deploy.py`, `templates/index.html` | Implement reference scenario data generator and evaluation endpoint. | MED | `test_sih_reference_scenario_exact_math`. |
| **Time-to-Crush / Countdown Display** | `templates/index.html` has severity-based warning texts with potential crush references. | Must remove all "time to crush" and replace exclusively with "time to configured operating limit" from timestamped inputs. | Misleading physical countdown terminology. | `templates/index.html`, `deploy.py` | Strip any "time to crush" wording; implement calculated $T_{\text{limit}}$ display. | LOW | Grep search confirms zero occurrences of "time to crush". |
| **Fruin LOS Display** | `templates/index.html` displays static Fruin Level of Service cards with hard-coded compression risks (`4.2% MINIMAL`). | Must remove from technical evidence views or explicitly label `SCENARIO / ILLUSTRATIVE`. Never present as live measurements. | Synthetic/fixed crowd metrics presented without scenario caveats. | `templates/index.html` | Relabel Fruin panel with prominent `SCENARIO / ILLUSTRATIVE` badge or replace with named zone status. | LOW | Verify UI displays `SCENARIO` badge on Fruin card. |
| **RPF Dispatch & Auto-Ack** | `deploy.py` line 1090 sets `"ack_received": True` on dispatch. | "Dispatch API auto-sets ack_received=True confuses API success with field response. Use real manual states: proposed, approved, delivered, acknowledged, completed, verified." | Dispatch automatically marks incident acknowledged, violating human-in-the-loop auditability. | `deploy.py`, `src/persistence.py`, `templates/index.html` | Refactor dispatch to set `status="DELIVERED"`; add dedicated manual `ACKNOWLEDGE`, `COMPLETE`, and `VERIFY` endpoints. | MED | `test_dispatch_does_not_auto_acknowledge`, `test_operator_lifecycle_transitions`. |
| **Human Operator Lifecycle** | Local journal tracks `CREATED`, `PERSISTED`, `LOCAL_DELIVERED`, `LOCAL_ACKNOWLEDGED`. | Must support full operational lifecycle: `PROPOSED` → `APPROVED` → `DELIVERED` → `ACKNOWLEDGED` → `COMPLETED` → `VERIFIED`. Post-action observation required for verification. | Missing `APPROVED`, `COMPLETED`, `VERIFIED` states and post-action verification logic. | `src/contracts.py`, `src/persistence.py`, `deploy.py`, `templates/index.html` | Extend `ActionLifecycleState` and persist transitions with actor and timestamp. | MED | `test_action_lifecycle_full_chain`, `test_verification_requires_subsequent_observation`. |
| **Evidence Provenance Tagging** | Displayed metrics lack formal provenance metadata. | Every displayed metric must carry: Value, Unit, Timestamp, Source, Evidence Status (`OBSERVED`, `CALCULATED`, `SCENARIO`, `PLANNED`). | Numbers are shown without provenance badges in UI. | `templates/index.html`, `deploy.py` | Add color-coded provenance badges across all metric cards in the dashboard. | LOW | Frontend rendering inspection for evidence badges. |
| **Synthetic Cameras & Mock Schedules** | Secondary camera options and mock train schedules exist without explicit synthetic watermarks. | Any synthetic data must visibly say `SYNTHETIC` or `MANUAL SCENARIO INPUT` on every view. | Risk of judges misinterpreting mock schedules as real integrations. | `templates/index.html`, `deploy.py` | Add prominent `SYNTHETIC SCENARIO` badges to all secondary feeds and railway schedules. | LOW | Visual inspection and grep verification. |
| **Flow Particles & Simulation** | `src/core/flow_simulation.py` has BFS shortest path and stochastic random jitter. | Decorative flow particles must NOT be presented as simulation evidence or calibrated digital twin. | Ambiguity regarding simulation validity. | `src/core/flow_simulation.py`, `templates/index.html` | Relabel flow visualization as `ILLUSTRATIVE SCHEMATIC VISUALIZATION`. | LOW | Verify UI text clarification. |
| **Offline Incident Continuity** | `deploy.py` + `IncidentJournal` currently support offline SQLite WAL logging and recovery for `IncidentCandidate`. | Must persist new decision actions, candidate evaluations, and full operator lifecycle transitions offline. | Action evaluations and new lifecycle states need SQLite persistence schema integration. | `src/persistence.py`, `deploy.py` | Add `actions` and `action_transitions` tables to `IncidentJournal`. | MED | `test_offline_action_persistence_and_restart`. |

---

## 3. Existing Files Impact Matrix

| File Path | Current Role | Target Role in Migrated Architecture | Action Required |
|---|---|---|---|
| `main.py` | Standalone local CLI monitor | Retained as compatibility CLI | Minor docstring/logging update |
| `deploy.py` | Canonical Round 2 Flask application | Central application hub with Decision Safety Layer APIs | Major refactoring: add decision endpoints, remove auto-ack, integrate forecast and safety engines |
| `src/contracts.py` | Core dataclasses (`RiskSnapshot`, `IncidentCandidate`) | Data contracts for observations, forecasts, and actions | Add `ObservationSnapshot`, `ForecastResult`, `ActionCandidate`, `ActionEvaluation`, `LifecycleState` |
| `src/persistence.py` | SQLite WAL journal (`events` table) | Durable journal for incidents, actions, and audit trail | Extend schema with `actions` and `action_transitions` tables; maintain backwards compatibility |
| `src/detector.py` | YOLOv8 person detector | Perception Engine vision processor | Keep intact; wrap output in `ObservationSnapshot` |
| `src/camera.py` | OpenCV frame grabber | Perception Engine video/camera source | Keep intact |
| `src/runtime.py` | `SentinelRuntime` background supervision | Safety Plane runtime coordinator | Hook new decision analysis as a non-blocking consumer |
| `src/connectivity.py` | Network state machine with hysteresis | Network connectivity monitor | Keep intact |
| `src/sync.py` | Idempotent background sync worker | Background sync worker for actions and incidents | Keep intact; adapt to sync action transitions |
| `templates/index.html` | Dark-mode operator dashboard | Redesigned Operator Decision Dashboard | Major refactoring: add Evidence badges, Decision Safety cards, Lifecycle controls, remove "crush" text |
| `src/core/flow_simulation.py` | Grid BFS simulation | Retained as schematic visual model only | Label clearly as non-physical schematic visual |
| `src/core/railway_integration.py` | Synthetic train schedules | Contextual scenario input | Add `SYNTHETIC SCENARIO INPUT` badge to all outputs |

---

## 4. Decommissioning & Cleanup Plan

1. **Delete auto-acknowledgement:** Remove `"ack_received": True` from `deploy.py` line 1090.
2. **Purge "time to crush":** Replace all references in `templates/index.html` with "Time to configured operating limit".
3. **Relabel Fruin LOS:** Add an explicit `SCENARIO / ILLUSTRATIVE` badge to the Fruin card.
4. **Relabel train schedules:** Add `SYNTHETIC / SCENARIO INPUT` watermark to all railway context outputs.
5. **Freeze old deprecated modules:** Mark `src/core/prediction.py` and `src/core/action_executor.py` as archived legacy code.
