# SENTINEL AI: EDGE SPECIFICATIONS & DISASTER CONTINUITY ARCHITECTURE
## Smart India Hackathon 2026 -- Disaster Management (SIH26206)

---

## 1. Edge Computer Vision Pipeline (Zero-Cloud Dependency)

- Model: YOLOv8n (Nano) person detector with customized spatial anchor boxes.
- Inference Resolution: 960x960 px input canvas for high-recall crowd detection at distance.
- Latency Budget: ~38ms - 75ms per frame on edge hardware (Intel Core / Jetson Orin Nano).
- Post-Processing Containment Filter: Custom Intersection-over-Smaller (IoS) containment filter that eliminates phantom double-counts for close-up bodies while preserving adjacent devotees.
- Grid Discretization: 4x6 planar tessellation (24 discrete spatial cells) covering the monitored corridor.

---

## 2. Deterministic Flow Dynamics & Conservation Equations

Sentinel AI does not treat crowd density as a black box. It applies fundamental fluid-dynamic mass-conservation physics:

  dN_i / dt = Q_in,i - Q_out,i

Where:
- N_i: Instantaneous population in corridor zone i.
- Q_in,i: Real-time inflow rate (persons/second).
- Q_out,i: Real-time outflow rate (persons/second).

### Time to Operating Limit (T_limit) Formulation:

  T_limit = (C_i - N_i(t)) / max(0.1, Q_in,i - Q_out,i)

Where C_i is the maximum safe operating capacity of zone i.

### Sensitivity Envelope:
To prevent brittle false alarms caused by temporary camera occlusions, Sentinel AI evaluates an uncertainty envelope [T_min, T_max] across a +/-15% flow variance:
- T_min = (C_i - N_i) / (1.15 * (Q_in - Q_out))
- T_max = (C_i - N_i) / (0.85 * (Q_in - Q_out))

---

## 3. Decision Safety Layer & Secondary Bottleneck Prevention

The core scientific differentiator of Sentinel AI is its proactive diversion safety check:

When an upstream bottleneck triggers a diversion proposal, Sentinel AI simulates downstream impact before authorizing movement:

  N_receiving(t + delta_t) = N_receiving(t) + integral(Q_diverted + Q_existing - Q_discharge) d_tau

If N_receiving exceeds C_receiving at any point during delta_t, the proposed diversion is REJECTED AS DANGEROUS.

Example:
- Candidate Action: 'Divert Triveni flow to Pontoon Bridge 4'
- Simulation Result: Secondary bottleneck breach in 48 seconds (108% Pontoon capacity).
- Safety Layer Decision: REJECTED (Unsafe transfer of risk).
- Counter-Directive: Engage upstream holding buffer at Parade Ground; pace inflow to 1.5 pax/s.

---

## 4. Zero-WAN Offline Durability (SQLite WAL + SyncWorker)

- Local Journal: SQLite in WAL (Write-Ahead Logging) mode with PRAGMA synchronous = NORMAL.
- Idempotency Guarantee: Every incident candidate is assigned an immutable UUIDv4 upon generation.
- State Machine: PENDING -> SYNCING -> SYNCED or RETRYABLE_FAILURE.
- Conflict Handling: Server-side idempotency boundary rejects conflicting payloads for existing IDs while accepting identical duplicates cleanly.
