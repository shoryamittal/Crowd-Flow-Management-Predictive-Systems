# SENTINEL-AI — Safety Guardrails & Deterministic Decision Engine

## 1. The Core Scientific Boundary

In safety-critical disaster management, **neural networks must never make unconstrained decisions**. SENTINEL-AI enforces strict boundaries:
- **No Stampede Prediction**: No computer vision system can predict individual human panic, tripping, or physical crowd collapse. SENTINEL-AI explicitly disclaims stampede prediction.
- **Inspectable Conservation Physics**: The system calculates the **Time to Configured Operating Limit ($T_{\text{limit}}$)** using transparent fluid-dynamic mass conservation equations:
  $$T_{\text{limit}} = \frac{C - N}{g}$$
  where $C$ is the engineered capacity, $N$ is current occupancy, and $g = \text{inflow} - \text{outflow}$.

---

## 2. Decision Safety Layer (The Differentiator)

Before any crowd diversion or metering action is presented to human operators, the **Decision Safety Engine** (`src/decision/safety.py`) evaluates candidate interventions across all connected corridors over a 90-second horizon.

### Evaluation Criteria:
1. **Secondary Bottleneck Check**: Does moving crowd volume from Zone A to Zone B cause Zone B to breach its configured limit? If yes $\to$ **REJECTED**.
2. **Route Status**: Is the route `CLOSED`, `UNVERIFIED`, or obstructed? If yes $\to$ **REJECTED**.
3. **Directionality Enforcement**: Does the action propose flow counter to one-way designated egress? If yes $\to$ **REJECTED**.
4. **Holding Area Buffer**: Does holding pilgrims upstream exceed the reservoir capacity of the staging area? If yes $\to$ **REJECTED**.

---

## 3. Human-in-the-Loop State Machine

Physical actions require human authorization. The backend logic strictly enforces the legal transition graph:

```
[ PROPOSED ] ──► [ APPROVED ] ──► [ DELIVERED ] ──► [ ACKNOWLEDGED ] ──► [ COMPLETED ] ──► [ VERIFIED ]
```

### Enforced Transition Rules (`src/persistence.py`):
- `PROPOSED` cannot skip directly to `VERIFIED`.
- `ACKNOWLEDGED` cannot precede `DELIVERED`.
- `COMPLETED` cannot precede `ACKNOWLEDGED`.
- `VERIFIED` **strictly requires** a post-action evidence snapshot (`evidence_snapshot_id`) confirming rate stabilization.
- Generative AI / Gemini cannot modify or mutate lifecycle state.

---

## 4. 25-Scenario Red-Team Fault Tolerance

The test suite [`tests/test_redteam_25.py`](file:///c:/Users/SHORYA%20MITTAL/OneDrive/Attachments/Project/SIH/tests/test_redteam_25.py) verifies system robustness across 25 adversarial failure modes:

| # | Fault Mode | System Defense / Response |
| :--- | :--- | :--- |
| **01** | Broken camera returning zero | Forecast marked `INVALID`; never falsely declares GREEN. |
| **02** | Stale camera feed (>5s) | Quality drops to `STALE`; $T_{\text{limit}}$ automatically invalidated. |
| **03** | Receiving corridor overload | Downstream simulation flags breach at $t=48\text{s}$ $\to$ `REJECTED`. |
| **04** | Closed route diversion | Route status check flags `CLOSED` $\to$ `REJECTED`. |
| **05** | Wrong direction flow | Unidirectional constraint check blocks counter-flow $\to$ `REJECTED`. |
| **06** | Holding-area overflow | Staging capacity exceeded $\to$ Upstream metering `REJECTED`. |
| **07** | Invalid / missing calibration | Marked `UNCALIBRATED`; suppresses false $\text{pax}/\text{m}^2$ density. |
| **08** | All candidate interventions unsafe | Returns `NO_FEASIBLE_OPTION_FOUND`; escalates to manual protocol. |
| **09** | Gemini invented crowd count | Safety firewall rejects counts not in structured input context. |
| **10** | Gemini invented capacity | Safety firewall validates capacity numbers against configuration. |
| **11** | Gemini invented route | Safety firewall blocks routes outside configured corridor graph. |
| **12** | Gemini changed deterministic decision | Firewall blocks claims that a `REJECTED` candidate is safe/approved. |
| **13** | Gemini claimed stampede certainty | Filter blocks sensational claims like "stampede will definitely occur". |
| **14** | Gemini generated forbidden confidence | Suppresses claims like "100% safe" or "guaranteed zero risk". |
| **15** | Prompt injection attack | System instruction contract strictly outranks untrusted input. |
| **16** | Malicious RAG source | Only verified NDMA / BPR&D SOP catalog entries are queryable. |
| **17** | Gemini timeout / failure | Immediate fallback to deterministic NDMA rule templates. |
| **18** | Gemini unavailable | Operates in offline mode with explicit banner in UI. |
| **19** | WAN blackout | Local YOLO detection and SQLite WAL journaling continue 100%. |
| **20** | Database process restart | SQLite WAL crash recovery restores exact state without corruption. |
| **21** | Illegal lifecycle transition | State machine rejects illegal jumps (e.g. PROPOSED to VERIFIED). |
| **22** | Scenario data mislabeled | Evidence status strictly distinguishes `OBSERVED` vs `SCENARIO`. |
| **23** | Multilingual instruction reversal | Translations in Hindi/Marathi strictly preserve negative polarity. |
| **24** | Verification without evidence | State machine blocks `VERIFIED` unless post-action snapshot exists. |
| **25** | Unauthorized operator approval | Transitions enforce authenticated actor role. |
