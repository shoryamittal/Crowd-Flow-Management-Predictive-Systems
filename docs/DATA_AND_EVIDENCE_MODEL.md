# SENTINEL-AI — Data & Evidence Lineage Model

## 1. Evidence Tiers & Scientific Provenance

Every significant metric displayed in the SENTINEL-AI dashboard or exported in post-incident audits carries explicit metadata defining its provenance tier:

| Evidence Tier | Definition | Example in System | UI Visual Style |
| :--- | :--- | :--- | :--- |
| **`OBSERVED`** | Direct physical sensor / camera measurement | Live YOLOv8 headcount on CCTV-01 | Blue Badge (`OBSERVED CCTV SIGNAL`) |
| **`CALCULATED`** | Deterministic mathematical calculation | Flow forecast $T_{\text{limit}} = (C - N)/g$ | Cyan Badge (`CALCULATED MATH`) |
| **`SCENARIO`** | Calibrated synthetic or operator scenario input | Simulated 4.0 pax/s express train arrival wave | Amber Badge (`MODELED OPERATIONAL SCENARIO`) |
| **`PLANNED`** | Future engineering or site-survey target | Configured zone capacity of 180 pax | Purple Badge (`CONFIGURED LIMIT`) |
| **`AI-GENERATED`** | GenAI text strictly grounded in verified state | Gemini tactical incident briefing | Green Badge (`AI-GENERATED BRIEF (GROUNDED)`) |

> **Scientific Honesty Rule**: A scenario number or synthetic test pattern must never silently masquerade as a live physical measurement.

---

## 2. Core Telemetry Lineage Contract

All data passed between perception, forecasting, decision support, and the UI implements the following schema:

```json
{
  "metric_id": "METRIC-2026-0914-001",
  "zone_id": "Bottleneck B",
  "value": 138.0,
  "unit": "passengers",
  "timestamp_utc": "2026-09-14T17:35:12.450Z",
  "source": "Platform 1-2 Staircase Chokepoint (CCTV-01)",
  "evidence_tier": "OBSERVED",
  "quality_state": "LIVE",
  "calibration_state": "UNCALIBRATED",
  "frame_age_ms": 42.0,
  "model_version": "yolov8s.pt",
  "lineage": {
    "camera_index": 0,
    "backend": "cv2.CAP_DSHOW",
    "inference_device": "cuda:0 / cpu",
    "processing_latency_ms": 38.2
  }
}
```

---

## 3. Database Schema & Durability Architecture

Persistence is managed by [`src/persistence.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/src/persistence.py) using SQLite in **Write-Ahead Logging (WAL)** mode.

### Database Tables:
1. **`incidents`**: Immutable record of detected threshold breaches and anomalies.
2. **`decision_recommendations`**: Multi-candidate safety evaluations and generated justifications.
3. **`action_transitions`**: Chronological human-in-the-loop transition log (`PROPOSED` $\to$ `APPROVED` $\to$ `DELIVERED` $\to$ `ACKNOWLEDGED` $\to$ `COMPLETED` $\to$ `VERIFIED`).
4. **`sync_queue`**: Idempotent outgoing queue for syncing local events to Google Cloud Run when WAN is restored.

### Cryptographic Audit Seal:
When an incident report is exported via `GET /api/incident/report`, a **SHA-256 seal** is computed across all journal rows and WAL frames:
$$\text{Seal} = \text{SHA256}(\text{StationCode} + \text{Timestamp} + \text{JournalHash})$$
This guarantees tamper-evident provenance for statutory review by the National Disaster Management Authority (NDMA) and state police commands.
