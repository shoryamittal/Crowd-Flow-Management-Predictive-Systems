"""Integration test for the SIH 2026 Reference Demonstration Scenario.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf (Section 9 & 18.3)
Verifies exact arithmetic across all three candidates and sensitivity envelope.
"""
import pytest

from src.decision.models import (
    ActionType,
    FeasibilityStatus,
)
from src.decision.scenario import run_sih_reference_evaluation


def test_reference_scenario_exact_math():
    """GATE-09 & GATE-10: Exact arithmetic for worked synthetic scenario."""
    forecast, recommendation = run_sih_reference_evaluation()

    # 1. Baseline (No action)
    assert forecast["bottleneck_initial"] == 120.0
    assert forecast["bottleneck_limit"] == 180.0
    assert forecast["net_growth_rate"] == 2.0
    assert forecast["crossing_time_seconds"] == 30.0
    assert forecast["predicted_at_90s"] == 300.0

    # Sensitivity envelope
    # [110, 130] count, [1.5, 2.5] growth -> earliest: (180 - 130)/2.5 = 20.0
    assert pytest.approx(forecast["sensitivity_min_seconds"], 0.01) == 20.0
    # latest: (180 - 110)/1.5 = 46.67
    assert pytest.approx(forecast["sensitivity_max_seconds"], 0.01) == 46.67

    # 2. Candidate evaluations
    eval_by_type = {e.action_type: e for e in recommendation.evaluations}

    # Candidate: NO ACTION
    no_action = eval_by_type[ActionType.NO_ACTION]
    assert no_action.primary_zone_horizon_count == 300.0

    # Candidate: DIVERSION TO RELIEF R
    diversion = eval_by_type[ActionType.PERMITTED_DIVERSION]
    assert diversion.feasibility == FeasibilityStatus.REJECTED
    r_summary = diversion.affected_zones_summary["Relief R"]
    assert r_summary["initial"] == 80.0
    assert r_summary["limit"] == 160.0
    assert r_summary["net_growth_rate"] == 2.0
    assert r_summary["crossing_seconds"] == 48.0
    assert r_summary["horizon_count"] == 244.0
    assert any("exceeds configured operating limit at t = 48 s" in reason for reason in diversion.rejection_reasons)

    # Candidate: UPSTREAM METERING
    metering = eval_by_type[ActionType.UPSTREAM_METERING]
    assert metering.feasibility == FeasibilityStatus.FEASIBLE
    assert metering.primary_zone_peak_count == 136.0
    assert metering.primary_zone_horizon_count == 95.0
    assert metering.added_waiting_cost == 205.0

    h_summary = metering.affected_zones_summary["Holding H"]
    assert h_summary["initial"] == 100.0
    assert h_summary["horizon_count"] == 305.0
    assert h_summary["queue_added"] == 205.0
    assert h_summary["limit"] == 450.0

    # Response window: earliest crossing (20s) - delay (8s) - margin (5s) = 7s
    assert pytest.approx(metering.usable_response_window_seconds, 0.01) == 7.0
    assert pytest.approx(metering.recommendation_validity_seconds, 0.01) == 7.0

    # 3. Overall Recommendation
    assert recommendation.selected_candidate_id == "METER_UPSTREAM_H"
    assert recommendation.action_type == ActionType.UPSTREAM_METERING
    assert recommendation.status == "ACTIVE"
    assert "UPSTREAM METERING — FEASIBLE" in recommendation.summary_message
    assert "+205" in recommendation.tradeoffs_description
