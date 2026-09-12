"""Unit and integration tests for Decision Safety Layer.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf (Section 18.2)
"""
import pytest

from src.decision.models import (
    ActionType,
    FeasibilityStatus,
    QualityState,
    RouteConfig,
    RouteStatus,
)
from src.decision.safety import DecisionSafetyEngine
from src.decision.scenario import (
    get_reference_candidates,
    get_reference_routes,
    get_reference_zones,
)


@pytest.fixture
def safety_setup():
    zones = get_reference_zones()
    routes = get_reference_routes()
    candidates = get_reference_candidates()
    counts = {
        "Holding H": 100.0,
        "Approach A": 50.0,
        "Bottleneck B": 120.0,
        "Ghat G": 250.0,
        "Relief R": 80.0,
        "Exit E": 40.0,
    }
    flows = {
        "Bottleneck B": {"inflow": 4.0, "outflow": 2.0},
        "Relief R": {"inflow": 0.0, "outflow": 0.5},
        "Holding H": {"inflow": 5.0, "outflow": 4.0},
    }
    engine = DecisionSafetyEngine(horizon_seconds=90.0)
    return engine, zones, routes, candidates, counts, flows


def test_receiving_overload_rejects_diversion(safety_setup):
    """GATE-03: Receiving area exceeding limit rejects diversion."""
    engine, zones, routes, candidates, counts, flows = safety_setup
    div_cand = [c for c in candidates if c.action_type == ActionType.PERMITTED_DIVERSION][0]

    eval_result = engine.evaluate_candidate(
        candidate=div_cand,
        zones=zones,
        routes=routes,
        current_zone_counts=counts,
        base_flows=flows,
    )
    assert eval_result.feasibility == FeasibilityStatus.REJECTED
    assert any("exceeds configured operating limit at t = 48 s" in r for r in eval_result.rejection_reasons)


def test_closed_route_rejected(safety_setup):
    """GATE-01: A closed route is never recommended."""
    engine, zones, routes, candidates, counts, flows = safety_setup
    routes["Bottleneck B->Relief R"] = RouteConfig(
        route_id="Route B->R",
        source_zone_id="Bottleneck B",
        target_zone_id="Relief R",
        max_flow_capacity=3.0,
        status=RouteStatus.CLOSED,
    )
    div_cand = [c for c in candidates if c.action_type == ActionType.PERMITTED_DIVERSION][0]

    eval_result = engine.evaluate_candidate(
        candidate=div_cand,
        zones=zones,
        routes=routes,
        current_zone_counts=counts,
        base_flows=flows,
    )
    assert eval_result.feasibility == FeasibilityStatus.REJECTED
    assert any("CLOSED" in r for r in eval_result.rejection_reasons)


def test_unverified_route_rejected(safety_setup):
    """GATE-02: An unverified route is never recommended."""
    engine, zones, routes, candidates, counts, flows = safety_setup
    routes["Bottleneck B->Relief R"] = RouteConfig(
        route_id="Route B->R",
        source_zone_id="Bottleneck B",
        target_zone_id="Relief R",
        max_flow_capacity=3.0,
        status=RouteStatus.UNVERIFIED,
    )
    div_cand = [c for c in candidates if c.action_type == ActionType.PERMITTED_DIVERSION][0]

    eval_result = engine.evaluate_candidate(
        candidate=div_cand,
        zones=zones,
        routes=routes,
        current_zone_counts=counts,
        base_flows=flows,
    )
    assert eval_result.feasibility == FeasibilityStatus.REJECTED
    assert any("UNVERIFIED" in r for r in eval_result.rejection_reasons)


def test_holding_capacity_overload_rejects_metering(safety_setup):
    """Holding area near capacity rejects upstream metering."""
    engine, zones, routes, candidates, counts, flows = safety_setup
    # Set holding area initial to 400 with limit 450; +205 will breach it
    counts["Holding H"] = 400.0
    meter_cand = [c for c in candidates if c.action_type == ActionType.UPSTREAM_METERING][0]

    eval_result = engine.evaluate_candidate(
        candidate=meter_cand,
        zones=zones,
        routes=routes,
        current_zone_counts=counts,
        base_flows=flows,
    )
    assert eval_result.feasibility == FeasibilityStatus.REJECTED
    assert any("holding area" in r.lower() and "capacity" in r.lower() for r in eval_result.rejection_reasons)


def test_all_constraints_violated_returns_no_feasible(safety_setup):
    """GATE-11: If all candidate actions violate constraints, return NO FEASIBLE OPTION FOUND."""
    engine, zones, routes, candidates, counts, flows = safety_setup
    # Break both: Holding H already at 440 (metering fails); Relief R at 150 (diversion fails)
    counts["Holding H"] = 440.0
    counts["Relief R"] = 150.0

    rec = engine.evaluate_and_rank(
        candidates=candidates,
        zones=zones,
        routes=routes,
        current_zone_counts=counts,
        base_flows=flows,
    )
    assert rec.status == "NO_FEASIBLE_OPTION_FOUND"
    assert rec.selected_candidate_id is None
    assert "NO FEASIBLE OPTION FOUND" in rec.summary_message


def test_stale_observation_rejects_candidate(safety_setup):
    """GATE-05: Stale observation feeding candidate route triggers rejection."""
    engine, zones, routes, candidates, counts, flows = safety_setup
    div_cand = [c for c in candidates if c.action_type == ActionType.PERMITTED_DIVERSION][0]

    eval_result = engine.evaluate_candidate(
        candidate=div_cand,
        zones=zones,
        routes=routes,
        current_zone_counts=counts,
        base_flows=flows,
        quality_states={"Relief R": QualityState.STALE},
    )
    assert eval_result.feasibility == FeasibilityStatus.REJECTED
    assert any("STALE" in r for r in eval_result.rejection_reasons)
