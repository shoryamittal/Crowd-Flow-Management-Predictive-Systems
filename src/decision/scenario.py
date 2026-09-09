"""SIH 2026 Reference Demonstration Scenario.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf (Section 9)
Pre-configured deterministic scenario for evaluation and jury presentation.
"""
from __future__ import annotations

from typing import Any

from .forecast import FlowForecastEngine
from .models import (
    ActionCandidate,
    ActionType,
    CalibrationState,
    DecisionRecommendation,
    EvidenceStatus,
    QualityState,
    RouteConfig,
    RouteStatus,
    ZoneConfig,
    ZoneRole,
)
from .safety import DecisionSafetyEngine


def get_reference_zones() -> dict[str, ZoneConfig]:
    """Return configured zones for the SIH 2026 Reference Sector."""
    return {
        "Holding H": ZoneConfig(
            zone_id="Holding H",
            name="Holding Area H (Sector Concourse)",
            role=ZoneRole.HOLDING_AREA,
            configured_operating_limit=450.0,
            physical_max_capacity=600.0,
        ),
        "Approach A": ZoneConfig(
            zone_id="Approach A",
            name="Approach Corridor A",
            role=ZoneRole.APPROACH_CORRIDOR,
            configured_operating_limit=200.0,
            physical_max_capacity=300.0,
        ),
        "Bottleneck B": ZoneConfig(
            zone_id="Bottleneck B",
            name="Bottleneck B (North Staircase)",
            role=ZoneRole.BOTTLENECK,
            configured_operating_limit=180.0,
            physical_max_capacity=250.0,
        ),
        "Ghat G": ZoneConfig(
            zone_id="Ghat G",
            name="Ghat / Downstream Area G",
            role=ZoneRole.DISPERSAL_DESTINATION,
            configured_operating_limit=1000.0,
            physical_max_capacity=1500.0,
        ),
        "Relief R": ZoneConfig(
            zone_id="Relief R",
            name="Relief Corridor R (East Passage)",
            role=ZoneRole.RELIEF_CORRIDOR,
            configured_operating_limit=160.0,
            physical_max_capacity=220.0,
        ),
        "Exit E": ZoneConfig(
            zone_id="Exit E",
            name="Exit E (Perimeter Dispersal)",
            role=ZoneRole.EGRESS_EXIT,
            configured_operating_limit=500.0,
            physical_max_capacity=800.0,
        ),
    }


def get_reference_routes() -> dict[str, RouteConfig]:
    """Return configured routes for the SIH 2026 Reference Sector."""
    return {
        "Holding H->Approach A": RouteConfig(
            route_id="Route H->A",
            source_zone_id="Holding H",
            target_zone_id="Approach A",
            max_flow_capacity=5.0,
            permitted_direction="UNIDIRECTIONAL",
            status=RouteStatus.OPEN,
        ),
        "Approach A->Bottleneck B": RouteConfig(
            route_id="Route A->B",
            source_zone_id="Approach A",
            target_zone_id="Bottleneck B",
            max_flow_capacity=4.0,
            permitted_direction="UNIDIRECTIONAL",
            status=RouteStatus.OPEN,
        ),
        "Bottleneck B->Ghat G": RouteConfig(
            route_id="Route B->G",
            source_zone_id="Bottleneck B",
            target_zone_id="Ghat G",
            max_flow_capacity=2.5,
            permitted_direction="UNIDIRECTIONAL",
            status=RouteStatus.OPEN,
        ),
        "Bottleneck B->Relief R": RouteConfig(
            route_id="Route B->R",
            source_zone_id="Bottleneck B",
            target_zone_id="Relief R",
            max_flow_capacity=3.0,
            permitted_direction="UNIDIRECTIONAL",
            status=RouteStatus.OPEN,
        ),
        "Relief R->Exit E": RouteConfig(
            route_id="Route R->E",
            source_zone_id="Relief R",
            target_zone_id="Exit E",
            max_flow_capacity=2.0,
            permitted_direction="UNIDIRECTIONAL",
            status=RouteStatus.OPEN,
        ),
    }


def get_reference_candidates() -> list[ActionCandidate]:
    """Return pre-approved candidate interventions for evaluation."""
    return [
        ActionCandidate(
            candidate_id="NO_ACTION",
            action_type=ActionType.NO_ACTION,
            title="No Intervention (Baseline)",
            source_zone_id="Bottleneck B",
            staff_response_delay_seconds=8.0,
            planning_margin_seconds=5.0,
        ),
        ActionCandidate(
            candidate_id="DIVERT_TO_RELIEF_R",
            action_type=ActionType.PERMITTED_DIVERSION,
            title="Divert Flow to Relief Corridor R",
            source_zone_id="Bottleneck B",
            target_zone_id="Relief R",
            diverted_flow_rate=2.5,
            staff_response_delay_seconds=8.0,
            planning_margin_seconds=5.0,
        ),
        ActionCandidate(
            candidate_id="METER_UPSTREAM_H",
            action_type=ActionType.UPSTREAM_METERING,
            title="Upstream Metering at Holding Area H",
            source_zone_id="Bottleneck B",
            metered_inflow_rate=1.5,
            staff_response_delay_seconds=8.0,
            planning_margin_seconds=5.0,
        ),
    ]


def run_sih_reference_evaluation(
    b_inflow: float = 4.0,
    b_outflow: float = 2.0,
    b_initial: float = 120.0,
    r_initial: float = 80.0,
    h_initial: float = 100.0,
    horizon_seconds: float = 90.0,
) -> tuple[dict[str, Any], DecisionRecommendation]:
    """Execute the canonical SIH 2026 Reference Evaluation."""
    zones = get_reference_zones()
    routes = get_reference_routes()
    candidates = get_reference_candidates()

    current_counts = {
        "Holding H": h_initial,
        "Approach A": 50.0,
        "Bottleneck B": b_initial,
        "Ghat G": 250.0,
        "Relief R": r_initial,
        "Exit E": 40.0,
    }

    base_flows = {
        "Bottleneck B": {"inflow": b_inflow, "outflow": b_outflow},
        "Relief R": {"inflow": 0.0, "outflow": 0.5},
        "Holding H": {"inflow": 5.0, "outflow": 4.0},
    }

    forecast_engine = FlowForecastEngine(default_horizon_seconds=horizon_seconds)
    b_forecast = forecast_engine.forecast_zone(
        zone_id="Bottleneck B",
        current_count=b_initial,
        operating_limit=180.0,
        inflow_rate=b_inflow,
        outflow_rate=b_outflow,
        horizon_seconds=horizon_seconds,
        sensitivity_count_delta=10.0,   # [110, 130]
        sensitivity_growth_delta=0.5,   # [1.5, 2.5]
    )

    safety_engine = DecisionSafetyEngine(horizon_seconds=horizon_seconds)
    recommendation = safety_engine.evaluate_and_rank(
        candidates=candidates,
        zones=zones,
        routes=routes,
        current_zone_counts=current_counts,
        base_flows=base_flows,
        scenario_name="SYNTHETIC DEMONSTRATION SCENARIO",
        earliest_crossing_seconds=b_forecast.sensitivity_min_seconds,
    )

    forecast_summary = {
        "scenario_name": "SYNTHETIC DEMONSTRATION SCENARIO",
        "evidence_status": EvidenceStatus.SCENARIO.value,
        "horizon_seconds": horizon_seconds,
        "bottleneck_initial": b_initial,
        "bottleneck_limit": 180.0,
        "inflow_rate": b_inflow,
        "outflow_rate": b_outflow,
        "net_growth_rate": b_inflow - b_outflow,
        "crossing_time_seconds": b_forecast.modeled_limit_crossing_seconds,
        "predicted_at_90s": b_forecast.predicted_count_at_horizon,
        "sensitivity_min_seconds": b_forecast.sensitivity_min_seconds,
        "sensitivity_max_seconds": b_forecast.sensitivity_max_seconds,
    }

    return forecast_summary, recommendation
