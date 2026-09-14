# SENTINEL-AI — Scientific Seam, Calibration & Operational Limitations

## 1. Scientific Seam & Non-Claims

In strict compliance with disaster management ethics and Indian regulatory standards (NDMA, BPR&D, NIDM), SENTINEL-AI explicitly defines its operational boundaries:

### What SENTINEL-AI Is NOT:
1. **NOT a Stampede Predictor**:
   - Individual human biomechanics, tripping, panic propagation, and turbulent crowd collapse cannot be reliably predicted by computer vision.
   - The system calculates the **Time to Configured Operating Limit ($T_{\text{limit}}$)** under explicit, transparent mass-conservation assumptions.
2. **NOT an Autonomous Control System**:
   - SENTINEL-AI does not actuate physical turnstiles, gates, or barricades.
   - All interventions require human authorization by the **Station Director / RPF Duty Officer or Incident Commander**.
3. **NOT an Unchecked LLM Decision-Maker**:
   - Google Gemini sits strictly **above** the deterministic safety engine. It translates machine state into natural-language briefs and public announcements; it **never** makes feasibility or capacity clearance decisions.
4. **NOT "Fully Field Validated"**:
   - The primary demonstration scenario is an **engineered operational model** calibrated to the topology and expected arrival rates of Central Junction Terminal at the Central Railway Station Junction Terminal.
   - Physical field deployment requires site-specific camera surveying, lens distortion correction, and homography calibration.

---

## 2. Calibration Discipline & Homography Requirements

To convert 2D video pixel counts into metric spatial density ($\text{passengers}/\text{m}^2$):
- **Perspective Distortion**: High-angle CCTV cameras exhibit severe perspective foreshortening. A cluster of 10 people far from the camera occupies fewer pixels than 2 people close to the lens.
- **Site Calibration Requirement**: Prior to operational deployment, an optical homography matrix $H$ must be calibrated using four known ground-plane surveyor points.
- **System Safeguard**: In the absence of an active homography matrix, the system flags the feed as `UNCALIBRATED` and reports headcounts or relative occupancy indices rather than fabricated $\text{pax}/\text{m}^2$ values.

---

## 3. Generalization & Scalability

While the prototype specifically models the **High-Density Railway Station (Central Junction Terminal — Central Junction Terminal (Platforms 1-4 & Main FOB))**, the core safety engine is **100% configuration-driven**:

```
Corridor Network Configuration:
├── Zones (IDs, Names, Configured Limits, Physical Capacities)
├── Routes (Source Zone, Target Zone, Flow Capacities, Directionality)
└── Candidate Interventions (Source, Target, Diverted Rate, Delay Margin)
```

The exact same mathematical core generalizes to:
- **Railway Stations & Passenger Foot-Over-Bridges (FOBs)**
- **Mass Rapid Transit (Metro) Platforms & Turnstile Plazas**
- **Stadium Egress Concourses**
- **Passengerage Hill Corridors (e.g. Vaishno Devi, Sabarimala)**

---

## 4. Failure Modes & Graceful Degradation

| Failure Mode | Direct System Consequence | Fail-Safe Behavior |
| :--- | :--- | :--- |
| **Camera Feed Frozen / Cable Cut** | Frame age exceeds 5.0 seconds | Quality drops to `CAMERA_LOST`; $T_{\text{limit}}$ calculation halts; alert logged. |
| **Complete Internet / WAN Outage** | Cloud Run connection drops | Edge runtime continues local YOLO inference and SQLite WAL logging with 0 frame drop. |
| **Gemini API Timeout / Quota Limit** | LLM fails to return response within 8.0s | Instant fallback to deterministic NDMA rule templates with UI offline indicator. |
| **Corridor Barricaded Unexpectedly** | Route marked `CLOSED` in registry | Safety engine rejects all routing proposals traversing the blocked corridor. |
| **Corridors Saturated Simultaneously** | No safe diversion path exists | System declares `NO_FEASIBLE_OPTION_FOUND` and advises upstream holding area pacing. |
