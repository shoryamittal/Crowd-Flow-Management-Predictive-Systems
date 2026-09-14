# SENTINEL-AI — Google Cloud Run Deployment & Architecture Runbook

## Executive Overview
**SENTINEL-AI** is deployed on **Google Cloud Run** for the **Google Cloud AI Builder Cup 2026** under the **Sustainability & Social Impact** theme (SDG 11: Sustainable Cities & Communities / Disaster Risk Reduction).

The deployment adheres to a resilient **Hybrid Edge-to-Cloud Architecture**:
- **Edge / Local Continuity Plane**: High-frequency video capture, YOLOv8 crowd detection, spatial occupancy grid mapping, short-horizon deterministic flow forecasting ($T_{\text{limit}} = (C - N)/g$), Decision Safety candidate evaluation, SQLite WAL persistence, and local alarms operate locally with robust offline continuity.
- **Google Cloud Plane**: Hosted on Google Cloud Run to provide scalable remote command-center access, centralized NDMA SOP knowledge management, and generative operational assistance via the **SENTINEL Incident Copilot** (Google Gemini / Vertex AI, configurable via `GEMINI_MODEL`, e.g. `gemini-2.5-flash`).

```
 ┌─────────────────────────────────────────────────────────┐
 │                   LOCAL EDGE SENSING                    │
 │  CCTV / Replay ──► YOLOv8 ──► Spatial Occupancy (4x6)   │
 │         │                                               │
 │         ▼                                               │
 │  Flow Forecast [T_limit = (C - N)/g]                    │
 │         │                                               │
 │         ▼                                               │
 │  Decision Safety Engine (Deterministic Feasibility)     │
 │  [Secondary Bottleneck Check / Route Verification]      │
 └────────────────────────────┬────────────────────────────┘
                              │ Live Machine State (JSON)
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │            GOOGLE CLOUD RUN & GEMINI COPILOT            │
 │                                                         │
 │  Grounded NDMA (2014) SOP Knowledge Base                │
 │                            │                            │
 │                            ▼                            │
 │  SENTINEL Incident Copilot (Google Gemini)              │
 │  • Operational Decision Rationale Explanation          │
 │  • Sector Magistrate Executive Briefings               │
 │  • Non-Sensational Public Address Announcements        │
 │  • Tri-Lingual Operations (English / हिन्दी / मराठी)   │
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │             HUMAN-IN-THE-LOOP LIFECYCLE                 │
 │  Sector Magistrate Review & Approval                    │
 │  PROPOSED ──► APPROVED ──► DELIVERED ──► ACKNOWLEDGED   │
 │                                                         │
 │  Post-Action Verification via CCTV Sensors              │
 │  COMPLETED ──► VERIFIED                                 │
 └─────────────────────────────────────────────────────────┘
```

---

## 1. Quickstart: 1-Command Deployment to Cloud Run

### Prerequisites
- Google Cloud SDK (`gcloud`) installed and authorized: `gcloud auth login`
- Google Cloud Project with billing enabled

### Deploy Script
Run the automated deployment script:
```bash
chmod +x deploy_cloud_run.sh
./deploy_cloud_run.sh
```

Or deploy directly using `gcloud`:
```bash
gcloud run deploy sentinel-ai \
    --source . \
    --region asia-south1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 5 \
    --set-env-vars="HOST=0.0.0.0,PORT=8080,SENTINEL_AUTH_ENABLED=true"
```

---

## 2. Environment Variables Specification

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `PORT` | `8080` | Container port required by Google Cloud Run. |
| `HOST` | `0.0.0.0` | Bind host for all incoming container traffic. |
| `GEMINI_API_KEY` | *(empty)* | Optional API key for Google Gemini (`gemini-2.5-flash` / configurable). If absent, system automatically runs with the deterministic local safety fallback. |
| `GOOGLE_CLOUD_PROJECT`| *(auto)* | GCP project identifier for Vertex AI / Cloud Logging. |
| `GOOGLE_CLOUD_LOCATION` | `asia-south1` | Preferred Cloud Run / Vertex AI regional endpoint. |
| `STATION_NAME` | `Prayagraj Maha Kumbh — Sector 04` | Mass gathering sector name. |
| `STATION_CODE` | `KUMBH-SEC-04` | Operational sector identifier. |
| `SENTINEL_ADMIN_USER` | `admin` | Console administrator username. |
| `SENTINEL_ADMIN_PASS` | `sentinel2026` | Console administrator password. |
| `SENTINEL_AUTH_ENABLED` | `true` | Enforces authentication for command console (`/login/bypass` available for evaluators). |

---

## 3. Endpoints & Health Probes

Google Cloud Run leverages native HTTP health and readiness probes:

- **Liveness Probe**: `GET /health`
  - Returns `200 OK` with JSON `{ "status": "ok", "ai_state": "RUNNING", ... }`
- **Readiness Probe**: `GET /readiness`
  - Returns `200 OK` with full subsystem status:
    ```json
    {
      "status": "ready",
      "service": "sentinel-ai-mass-gathering-safety",
      "operating_sector": "Maha Kumbh Prayagraj Sector 04 (Sangam Triveni Ghat)",
      "deterministic_safety_engine": "ACTIVE",
      "flow_forecast_engine": "ACTIVE",
      "grounded_sop_knowledge_base": "ACTIVE (NDMA 4.2 / Kumbh Sector 4)",
      "copilot": {
        "available": true,
        "model_name": "gemini-2.0-flash",
        "provider": "Google GenAI (Gemini)"
      },
      "offline_continuity_plane": "HEALTHY"
    }
    ```
- **Copilot Endpoints**:
  - `POST /api/copilot/explain`: Decision rationale and risk trajectory explanation.
  - `POST /api/copilot/brief`: Sector Magistrate executive command briefing.
  - `POST /api/copilot/announcement`: Calm public address drafts.
  - `POST /api/copilot/translate`: Accurate Hindi / Marathi translation preserving technical markers.
  - `POST /api/copilot/whatif`: Candidate intervention comparison.
- **Judge Tour Automation**:
  - `POST /api/demo/judge_flow/step`: Advances deterministic 6-step walkthrough.
  - `POST /api/demo/judge_flow/reset`: Resets demo state back to baseline.

---

## 4. Resilience & Degraded Mode Verification

If network connectivity is severed or the Gemini API is unreachable:
1. **Zero Safety Interruption**: The edge detection, flow forecast ($T_{\text{limit}}$), and Decision Safety Engine continue executing locally at 100% fidelity.
2. **Explicit Transparency**: The UI displays an amber badge:
   `COPILOT UNAVAILABLE — DETERMINISTIC DECISION SUPPORT CONTINUES`
3. **No Hallucinations**: SENTINEL never fabricates responses or uses unchecked LLM fallbacks. Output is strictly generated from the local deterministic rule engine.
