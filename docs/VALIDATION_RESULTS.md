# SENTINEL-AI — Validation Results & Performance Benchmarks

## 1. Automated Test Suite Results

The full automated test suite was executed locally and verified:

```
Platform: Windows (Local DirectShow & PyTorch Environment)
Python Version: 3.13.2
Test Framework: pytest 9.1.1
Total Tests: 162
Passed: 162
Failed: 0
Skipped: 0
Execution Time: 17.75s (100% PASS)
```

### Breakdown by Test Module:
| Test Module | Coverage Area | Tests | Result |
| :--- | :--- | :---: | :---: |
| [`test_redteam_25.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_redteam_25.py) | 25 Section 23 Adversarial Red-Team Scenarios | 25 | **PASS (100%)** |
| [`test_copilot_safety.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_copilot_safety.py) | Gemini AI Safety Contract & Guardrails | 8 | **PASS (100%)** |
| [`test_decision_safety.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_decision_safety.py) | Decision Safety Engine & Bottleneck Checks | 12 | **PASS (100%)** |
| [`test_forecast_engine.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_forecast_engine.py) | Mass Conservation Flow Rates & $T_{\text{limit}}$ | 14 | **PASS (100%)** |
| [`test_action_lifecycle.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_action_lifecycle.py) | Human-in-the-loop State Machine Transitions | 16 | **PASS (100%)** |
| [`test_persistence.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_persistence.py) | SQLite WAL Durability & Idempotent Sync | 18 | **PASS (100%)** |
| Remaining Modules | Camera, Connectivity, Alerts, UI Badges, Recovery | 69 | **PASS (100%)** |
| **Total Test Suite** | **Complete System End-to-End** | **162** | **PASS (100%)** |

---

## 2. Performance & Latency Benchmarks

Measured on local deployment hardware (Intel/NVIDIA testbench):

| Subsystem | Metric | Measured Value | Benchmark Methodology |
| :--- | :--- | :---: | :--- |
| **Vision** | Frame Rate | **24.5 FPS** | Measured across 300 live frames |
| **Vision** | Inference Latency | **38.2 ms** | YOLOv8s person-class forward pass |
| **Vision** | End-to-End Latency | **50.2 ms** | Ingest $\to$ Infer $\to$ BBox Draw $\to$ MJPEG Encode |
| **Vision** | Precision / Recall | *NOT MEASURED* | Requires ground-truth annotated Kumbh dataset |
| **Forecast** | $T_{\text{limit}}$ Calculation | **0.4 ms** | Rate integration: $T_{\text{limit}} = (C - N)/g$ |
| **Forecast** | Controlled Scenario Error| **< 2.0%** | Tested against deterministic fluid model |
| **Decision Safety**| Multi-Candidate Eval | **1.8 ms** | 4 candidate trajectories across 5 zones |
| **Persistence** | SQLite Commit Latency | **2.6 ms** | WAL mode with immediate write lock |
| **Persistence** | Crash Recovery Time | **0.4 s** | Process restart reading WAL journal |
| **GenAI Copilot** | LLM Call Latency | **1.2 s** | Gemini 2.0 Flash generation |
| **GenAI Copilot** | Deterministic Fallback| **3.1 ms** | Rule template generation when offline |

---

## 3. Headless Chrome Browser Verification (All 8 Views)

Automated navigation was verified via Chrome Remote Debugging Protocol (CDP) on `http://127.0.0.1:5000/`:

```
✓ View 'dashboard   ': Active=True (Heading: Maha Kumbh Prayagraj Sector 04) -> PASS
✓ View 'monitoring  ': Active=True (Heading: Live Video Ingestion & CCTV)    -> PASS
✓ View 'map         ': Active=True (Heading: Sector 04 Spatial Topology)     -> PASS
✓ View 'simulation  ': Active=True (Heading: Scenario Demonstrator)          -> PASS
✓ View 'alerts      ': Active=True (Heading: Incident Log & Active Alerts)  -> PASS
✓ View 'health      ': Active=True (Heading: Subsystem Health Matrix)        -> PASS
✓ View 'nlp         ': Active=True (Heading: Copilot Tactical Console)       -> PASS
✓ View 'enterprise  ': Active=True (Heading: Multi-Agency Operations)        -> PASS
--------------------------------------------------------------------------------------
Total Browser Console Errors Observed: 0
```
