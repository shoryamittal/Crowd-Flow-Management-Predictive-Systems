"""
Frontend & API Contract Verification Tests for Sentinel AI SIH 2026
Verifies:
1. Evidence provenance badges (OBSERVED, CALCULATED, SCENARIO, PLANNED) exist in index.html.
2. Complete absence of forbidden claims and terminology (e.g., 'time to crush', 'optimal routing').
3. T_limit conservation formula and sensitivity envelope are explicitly displayed in UI.
4. Decision Safety Layer and 6-stage Operator Action Lifecycle components exist.
5. deploy.py dispatch does not claim auto-acknowledgement (ack_received=False).
"""

from pathlib import Path
import pytest

INDEX_HTML_PATH = Path(__file__).resolve().parent.parent / "templates" / "index.html"
DEPLOY_PY_PATH = Path(__file__).resolve().parent.parent / "deploy.py"


@pytest.fixture(scope="module")
def index_html() -> str:
    assert INDEX_HTML_PATH.exists(), f"File not found: {INDEX_HTML_PATH}"
    return INDEX_HTML_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def deploy_py() -> str:
    assert DEPLOY_PY_PATH.exists(), f"File not found: {DEPLOY_PY_PATH}"
    return DEPLOY_PY_PATH.read_text(encoding="utf-8")


def test_evidence_provenance_badges_present(index_html: str):
    """Verify that all four provenance contract tiers exist in the UI."""
    assert "badge-observed" in index_html
    assert "badge-calculated" in index_html
    assert "badge-scenario" in index_html
    assert "badge-planned" in index_html
    assert "signal-provenance-badge" in index_html
    assert "OBSERVED CCTV SIGNAL" in index_html
    assert "SCENARIO / CALIBRATED INPUT" in index_html


def test_forbidden_terminology_absent(index_html: str):
    """Enforce complete absence of banned marketing and panic terminology."""
    forbidden_terms = [
        "time to crush",
        "time-to-crush",
        "predicts stampedes",
        "predict stampede",
        "optimal routing",
        "100% effective",
        "90-second warning",
        "crush forecasting",
        "critical crush",
        "mass crush",
    ]
    lowered = index_html.lower()
    for term in forbidden_terms:
        assert term not in lowered, f"Forbidden term '{term}' found in templates/index.html"


def test_flow_forecast_and_t_limit_formula_present(index_html: str):
    """Verify deterministic flow forecast and conservation formula are visible to operators."""
    assert "T_limit = (C - N) / g" in index_html or "(C - N) / g" in index_html
    assert "Deterministic Flow Forecast" in index_html
    assert "Sensitivity Envelope" in index_html
    assert "calc-tlimit-val" in index_html
    assert "calc-envelope-val" in index_html


def test_decision_safety_layer_cards_present(index_html: str):
    """Verify Decision Safety Layer evaluation structure with rejected and feasible actions."""
    assert "decision-safety-container" in index_html
    assert "DECISION SAFETY LAYER" in index_html
    assert "Divert to Relief Route R" in index_html
    assert "Upstream Metering" in index_html
    assert "REJECTED" in index_html
    assert "FEASIBLE" in index_html
    assert "Secondary bottleneck transfer" in index_html or "Capacity breach in 48s" in index_html


def test_action_lifecycle_stepper_present(index_html: str):
    """Verify 6-stage lifecycle stepper is rendered in UI."""
    assert "lc-step-PROPOSED" in index_html
    assert "lc-step-APPROVED" in index_html
    assert "lc-step-DELIVERED" in index_html
    assert "lc-step-ACKNOWLEDGED" in index_html
    assert "lc-step-COMPLETED" in index_html
    assert "lc-step-VERIFIED" in index_html


def test_deploy_dispatch_acknowledgement_compliance(deploy_py: str):
    """Enforce that deploy.py dispatch does NOT assume automated field acknowledgment."""
    # When an action is dispatched, ack_received MUST NOT be True
    assert '"ack_received": False' in deploy_py
    assert '"ack_received": True' not in deploy_py

    # Verify decision endpoints are registered
    assert "/api/decision/observation" in deploy_py
    assert "/api/decision/scenario/load" in deploy_py
    assert "/api/decision/evaluate" in deploy_py
    assert "/api/operator/action/transition" in deploy_py
