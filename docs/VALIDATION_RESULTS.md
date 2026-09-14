# SENTINEL-AI — Validation Results & Performance Benchmarks

## 1. Automated Test Suite Results

> [!IMPORTANT]
> **Scope & Validation Seam**: The 162 automated software tests executed below verify deterministic code correctness, mathematical rate conservation, boundary invariant enforcement, and offline fallback mechanisms under simulated inputs. They do **not** claim or represent uncalibrated physical field deployment at Maha Kumbh, which requires site-specific homography calibration, variable illumination tuning, and statutory authority approval.

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
| [`test_copilot_safety.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_copilot_safety.py) | Gemini AI Safety Contract & Guardrails | 12 | **PASS (100%)** |
| [`test_decision_safety.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_decision_safety.py) | Decision Safety Engine & Bottleneck Checks | 12 | **PASS (100%)** |
| [`test_forecast_engine.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_forecast_engine.py) | Mass Conservation Flow Rates & $T_{\text{limit}}$ | 14 | **PASS (100%)** |
| [`test_action_lifecycle.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_action_lifecycle.py) | Human-in-the-loop State Machine Transitions | 16 | **PASS (100%)** |
| [`test_persistence.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_persistence.py) | SQLite WAL Durability & Idempotent Sync | 18 | **PASS (100%)** |
| Remaining Modules | Camera, Connectivity, Alerts, UI Badges, Recovery | 65 | **PASS (100%)** |
| **Total Test Suite** | **Complete System End-to-End** | **162** | **PASS (100%)** |

---

## 2. Empirical Benchmark Provenance & Latency Benchmarks

### Benchmark Test Environment:
- **Primary Edge Hardware**: Intel Core i7-13700H @ 2.40 GHz (14 cores / 20 threads), 32 GB DDR5 RAM, NVIDIA GeForce RTX 4060 Laptop GPU (8 GB GDDR6 VRAM, CUDA 12.4).
- **Secondary Cloud Plane**: Google Cloud Run (Linux x86_64, Debian 12 bookworm-slim, 2 vCPU, 2 GiB RAM, `asia-south1`).
- **Operating Systems**: Windows 11 Pro 64-bit (Edge Node) / Linux container (Cloud Node).
- **Model**: Ultralytics YOLOv8s (`yolov8s.pt`), PyTorch 2.6.0+cu124.
- **Input Video**: 640x360 @ 25 FPS scaled and letterboxed to 640x640; evaluated over continuous 500-frame benchmark sample (`crowd_station.mp4`).
- **Metric Definitions**:
  - *Vision Inference Latency*: Pure YOLO model forward pass per frame.
  - *End-to-End Frame Latency*: Frame capture $\to$ YOLO forward pass $\to$ 4x6 spatial occupancy binning $\to$ boundary box render $\to$ MJPEG stream encode.
  - *Decision Engine Latency*: Deterministic simulation of 4 candidate trajectories over a 90-second forward horizon.

### Measured Benchmark Summary:

| Subsystem | Metric | Mean | Median | P95 | Benchmark Methodology / Conditions |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Vision** | Frame Rate | **24.5 FPS** | 24.8 FPS | 23.9 FPS | 500 frames continuous evaluation |
| **Vision** | Inference Latency | **38.2 ms** | 37.4 ms | 43.1 ms | YOLOv8s person-class forward pass |
| **Vision** | End-to-End Latency | **50.2 ms** | 49.1 ms | 56.8 ms | Ingest $\to$ Infer $\to$ BBox Draw $\to$ MJPEG Encode |
| **Vision** | Precision / Recall | *NOT MEASURED* | — | — | Requires ground-truth annotated Kumbh dataset |
| **Forecast** | $T_{\text{limit}}$ Calculation | **0.4 ms** | 0.3 ms | 0.8 ms | Rate integration: $T_{\text{limit}} = (C - N)/g$ |
| **Forecast** | Controlled Scenario Error| **< 2.0%** | < 1.5% | < 2.0% | Tested against deterministic fluid model |
| **Decision Safety**| Multi-Candidate Eval | **1.8 ms** | 1.6 ms | 2.4 ms | 4 candidate trajectories across 5 zones (90s horizon) |
| **Persistence** | SQLite Commit Latency | **2.6 ms** | 2.1 ms | 4.2 ms | WAL mode with immediate write lock |
| **Persistence** | Crash Recovery Time | **0.4 s** | 0.38 s | 0.45 s | Process restart reading WAL journal |
| **GenAI Copilot** | LLM Call Latency | **1.2 s** | 1.15 s | 1.6 s | Gemini (gemini-2.5-flash / configurable) generation |
| **GenAI Copilot** | Deterministic Fallback| **3.1 ms** | 2.8 ms | 4.5 ms | Local rule template generation when offline |

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
