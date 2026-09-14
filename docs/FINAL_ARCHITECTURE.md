# SENTINEL-AI — Final System Architecture

## 1. Architectural Mission & Philosophy

SENTINEL-AI is an **action-aware, hybrid edge-to-cloud crowd intelligence and decision-support platform** engineered for high-density mass gatherings (modeled case study: **Maha Kumbh Mela Prayagraj Sector 04 Operational Layout**).

The core operational thesis of SENTINEL-AI addresses the fatal flaw of traditional crowd management tools:
> *"Most crowd systems tell you where congestion is high. Sentinel asks the next operational question: **If I move this crowd somewhere else, will I create the next dangerous bottleneck downstream?**"*

```
                         THE SAFETY-CRITICAL PIPELINE
                        
   [ Video / CCTV ] ──► [ OpenCV + YOLOv8 ] ──► [ OBSERVED STATE ]
                                                        │
                                                        ▼
                                             [ DETERMINISTIC FORECAST ]
                                              T_limit = (C - N) / g
                                                        │
                                                        ▼
                                             [ DECISION SAFETY LAYER ]
                                                        │
                         ┌──────────────────────────────┼──────────────────────────────┐
                         ▼                              ▼                              ▼
                   [ SAFE OPTION ]             [ REJECTED + REASON ]           [ NO FEASIBLE OPTION ]
                         │                              │                              │
                         └──────────────────────────────┼──────────────────────────────┘
                                                        │
                                                        ▼
                                            [ GEMINI INCIDENT COPILOT ]
                                        (Google Gemini / gemini-2.5-flash)
                                      • Explain • Brief • Multilingual Public PA
                                                        │
                                                        ▼
                                            [ HUMAN-IN-THE-LOOP ]
                                     PROPOSED ──► APPROVED ──► DELIVERED
                                                        │
                                                        ▼
                                            [ POST-ACTION SENSORS ]
                                          COMPLETED ──► VERIFIED
                                                        │
                                                        ▼
                                            [ IMMUTABLE AUDIT LOG ]
                                          SQLite WAL + SHA-256 Seal
```

---

## 2. Separation of Concerns (The Seven-Link Chain)

1. **Perception (Edge / Local)**:
   - OpenCV + YOLOv8 inference running at 24+ FPS on edge hardware.
   - Dynamic DirectShow camera auto-discovery on Windows and `/dev/video*` on Linux.
   - 4x6 spatial occupancy representation preserving zone-level headcounts.
   - Strict quality tagging: `LIVE`, `STALE`, `CAMERA_LOST`, `UNCALIBRATED`.

2. **Forecast Engine (Deterministic Physics)**:
   - Mass conservation rate equation: $T_{\text{limit}} = \frac{C - N}{g}$ where $g = \text{inflow} - \text{outflow}$.
   - Sensitivity envelope $[T_{\text{min}}, T_{\text{max}}]$ computed under explicit rate assumptions.
   - Automatic invalidation (`FORECAST_UNAVAILABLE`) if camera quality drops to `STALE` or `CAMERA_LOST`.

3. **Decision Safety Layer (Deterministic Feasibility)**:
   - Simulates downstream corridor impacts over a 90-second horizon before any recommendation is proposed.
   - **Secondary Bottleneck Check**: Automatically rejects crowd diversions if the receiving zone will breach its operating limit (e.g. Relief Pontoon Bridge R rejected at $t=48\text{s}$ due to 108% peak load).
   - Route status verification (`OPEN`, `CLOSED`, `UNVERIFIED`) and flow directionality enforcement.

4. **Incident Copilot (Google Gemini / gemini-2.5-flash)**:
   - Sits strictly **above** the safety engine as an interpretation and communication layer.
   - Grounded in verified official guidance: **NDMA National Disaster Management Guidelines — Managing Crowds at Events and Venues of Mass Gathering (2014)** and operational procedures (`SOP-CFM-FLOW-01` through `05`).
   - Generates tactical briefs for Sector Magistrates, explainable rejection rationales, and calm public address announcements in English, Hindi, and Marathi.
   - **Hallucination Firewall**: Rejects any LLM output attempting to approve rejected actions, claim stampede certainty, or invent numbers.

5. **Human-in-the-Loop Lifecycle**:
   - Enforces legal state transitions: $\text{PROPOSED} \to \text{APPROVED} \to \text{DELIVERED} \to \text{ACKNOWLEDGED} \to \text{COMPLETED} \to \text{VERIFIED}$.
   - AI never actuates physical barricades or overrides human command.

6. **Post-Action Verification**:
   - Compares post-intervention sensor observations against projected rates.
   - Only physical camera evidence confirming rate stabilization can advance status to `VERIFIED`.

7. **Audit & Resilience**:
   - SQLite WAL mode local persistence with robust offline continuity and edge survivability.
   - Cryptographic SHA-256 seal on audit dossiers for statutory NDMA/Police review.

---

## 3. Hybrid Edge-to-Cloud Topology

| Component | Execution Plane | Technology | Failure Behavior |
| :--- | :--- | :--- | :--- |
| **Video Ingestion** | Local Edge | OpenCV DirectShow / V4L2 | Reverts to synthetic standby test pattern |
| **YOLOv8 Detection** | Local Edge | PyTorch / Ultralytics Edge | Local inference continues; 0 WAN dependency |
| **Decision Safety Layer** | Local Edge | Python deterministic state machine | Always active; cannot be disabled |
| **Incident Persistence** | Local Edge | SQLite WAL Mode | Fully durable across power restarts |
| **Command Center UI** | Cloud / Local | Flask 3.0 on Google Cloud Run | Stateless autoscaling (0 to 5 instances) |
| **Incident Copilot** | Google Cloud | Gemini (gemini-2.5-flash / configurable) | Falls back to deterministic local safety templates |
| **Knowledge Base** | Google Cloud / Edge | Grounded NDMA (2014) SOP Catalog | Read-only in-memory static catalog |

---

## 4. Software Verification vs. Field Deployment Distinction

> [!IMPORTANT]
> **Scientific Seam**: The 162 automated test cases verify software logic, deterministic physics models, and fault handling under simulated conditions. Real-world physical deployment at mass gatherings requires physical camera homography calibration, lighting validation, and official statutory sign-off from local disaster management authorities.
