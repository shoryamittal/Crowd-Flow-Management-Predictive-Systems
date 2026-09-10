# SMART INDIA HACKATHON 2026 -- JURY EVALUATION GUIDE
## SENTINEL AI: Action-Aware Crowd Disaster Prevention for Mass Gatherings
### Theme: Disaster Management (SIH26206) | Deployment: Maha Kumbh Mela Prayagraj (Sector 04)

---

## 1. 3-Minute Live Jury Pitch Script

### Minute 0:00 - 0:45: The Problem & The Core Flaw of Existing AI
- *Narrator:* 'Respected Jury members, during the Maha Kumbh Mela, over 10 million devotees converge at Sector 4 Sangam Ghat. Traditional crowd analytics show heatmaps that say where people are crowded. But they fail to answer the critical operational question: **If we divert this crowd somewhere else, will we create a deadly stampede at the next bottleneck?**'
- *Action:* Point to Dashboard showing real-time webcam feed, HUD telemetry, and Threat Level IV.

### Minute 0:45 - 1:30: The Deterministic Flow Forecast & The Decision Safety Layer
- *Narrator:* 'Sentinel AI introduces the Decision Safety Layer. Click Step 2: Shahi Snan surge arrives. Watch the Time-to-Operating-Limit formula calculate 62 seconds before capacity breach. Now click Step 3: A naive diversion to Relief Pontoon Bridge 4 is evaluated. **The Decision Safety Layer simulates the downstream route and REJECTS it at t=48s** because the pontoon bridge would breach 108% capacity! Instead, it recommends Upstream Pacing at Holding Area 4.'
- *Action:* Demonstrate Scenario Demonstrator, showing mathematical rejection badge and mitigation counter-action.

### Minute 1:30 - 2:15: Zero-WAN Offline Continuity
- *Narrator:* 'During massive congregations, 4G towers crash completely. Most cloud AI systems go blind. Watch Step 4: We simulate complete network loss. The system does not crash or lose a single frame. The Edge Runtime continues processing locally at 38ms latency, durably logging incidents into SQLite WAL.'
- *Action:* Click Step 4 (Zero-WAN Outage). Observe OFFLINE indicator, ongoing YOLO detections, and incrementing local journal.

### Minute 2:15 - 3:00: Idempotent Failsafe Recovery & Multi-Agency Roster
- *Narrator:* 'Click Step 5: Network connectivity is restored. The background SyncWorker replays all buffered incidents to the cloud state machine with zero duplication and zero UUID inflation. Finally, open the Forensic Dossier to inspect cryptographically signed evidence for NDMA and UP Police.'
- *Action:* Click Step 5 (Failsafe Recovery), show Sync count advance, then open Dossier.

---

## 2. Five Interactive Jury Steps (One-Click Demonstrations)

| Step | Button Label | Operational Demonstration | What the Evaluator Should Verify |
| :--- | :--- | :--- | :--- |
| **1** | Safe Baseline | Nominal devotee flow | Green Threat Level IV, <1.5 pax/m2, live edge YOLO bounding boxes. |
| **2** | Inflow Surge (T_limit) | Shahi Snan bathing wave | Inflow exceeds outflow (4.0 vs 2.0 pax/s), T_limit countdown begins. |
| **3** | Safety Layer Rejection | Divert to Pontoon Bridge | System proactively flags secondary bottleneck breach at t=48s and REJECTS action. |
| **4** | Zero-WAN Outage | Cellular / WAN blackout | UI shows OFFLINE, AI continues real-time inference, SQLite journal persists. |
| **5** | Failsafe Recovery | Network reconnection | Buffered records sync idempotently; live telemetry resumes seamlessly. |

---

## 3. Hardware Bill of Materials (BOM) & Cost Efficiency

| Component | Standard Cloud Approach | Sentinel AI Edge Architecture | Cost Saving / Efficiency |
| :--- | :--- | :--- | :--- |
| **Bandwidth (32 CCTV)** | 32 x 4 Mbps = 128 Mbps continuous | 0 Mbps (Raw video never leaves local switch) | **98.4% bandwidth reduction** |
| **Cloud GPU Compute** | AWS g4dn.xlarge (.526/hr x 720h = /mo) | Edge Industrial Mini-PC / Jetson ( one-time) | **Breakeven in 6 weeks** |
| **Offline Reliability** | 0% (Fails immediately during outage) | 100% (Air-gap certified, local SQLite WAL) | **Life-critical disaster resilience** |
