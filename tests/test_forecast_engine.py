"""Unit tests for Flow Forecast Engine.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf (Section 18.1)
"""
import pytest

from src.decision.forecast import (
    FlowForecastEngine,
    calculate_limit_crossing,
    calculate_sensitivity_envelope,
)
from src.decision.models import CalibrationState, QualityState


def test_positive_growth_crossing():
    """T_limit = (C - N) / g for positive net growth."""
    # N=120, C=180, g=2.0 -> (180 - 120) / 2 = 30.0 s
    t_limit = calculate_limit_crossing(current_count=120.0, operating_limit=180.0, net_growth_rate=2.0)
    assert t_limit == 30.0


def test_current_breach():
    """If N >= C, immediately report 0.0 (current breach)."""
    assert calculate_limit_crossing(current_count=180.0, operating_limit=180.0, net_growth_rate=2.0) == 0.0
    assert calculate_limit_crossing(current_count=195.0, operating_limit=180.0, net_growth_rate=2.0) == 0.0


def test_zero_growth_produces_no_countdown():
    """Non-growing queue produces NO invented countdown (None)."""
    assert calculate_limit_crossing(current_count=120.0, operating_limit=180.0, net_growth_rate=0.0) is None


def test_negative_growth_produces_no_countdown():
    """Negative growth (clearing queue) produces no limit crossing within horizon."""
    assert calculate_limit_crossing(current_count=120.0, operating_limit=180.0, net_growth_rate=-1.5) is None


def test_stale_camera_invalidates_forecast():
    """Camera failure or stale frames must invalidate dependent forecast."""
    engine = FlowForecastEngine()
    snap = engine.forecast_zone(
        zone_id="Bottleneck B",
        current_count=120.0,
        operating_limit=180.0,
        inflow_rate=4.0,
        outflow_rate=2.0,
        quality_state=QualityState.STALE,
    )
    assert snap.calculation_validity == "FORECAST_UNAVAILABLE"
    assert snap.modeled_limit_crossing_seconds is None
    assert "STALE" in (snap.invalidation_reason or "")


def test_inconsistent_units_produces_unavailable():
    """Uncalibrated occupancy proxy cannot masquerade as people."""
    engine = FlowForecastEngine()
    snap = engine.forecast_zone(
        zone_id="Bottleneck B",
        current_count=0.75,
        operating_limit=1.0,
        inflow_rate=0.1,
        outflow_rate=0.05,
        unit="relative_occupancy_index",
    )
    assert snap.calculation_validity == "FORECAST_UNAVAILABLE"
    assert "unit" in (snap.invalidation_reason or "").lower()


def test_overloaded_zone_is_not_clipped():
    """An overloaded simulated zone must NOT be artificially clipped at its limit."""
    engine = FlowForecastEngine()
    snap = engine.forecast_zone(
        zone_id="Bottleneck B",
        current_count=120.0,
        operating_limit=180.0,
        inflow_rate=4.0,
        outflow_rate=2.0,
        horizon_seconds=90.0,
    )
    # N(90) = 120 + (4 - 2)*90 = 300
    assert snap.predicted_count_at_horizon == 300.0
    assert snap.predicted_count_at_horizon > snap.operating_limit


def test_network_conservation_and_transfer_symmetry():
    """Inter-zone transfers must be symmetrical: departure from A, arrival at B."""
    engine = FlowForecastEngine()
    zones = {
        "A": {"initial_count": 100.0, "external_inflow": 0.0, "external_outflow": 0.0},
        "B": {"initial_count": 50.0, "external_inflow": 0.0, "external_outflow": 0.0},
    }
    transfers = [{"from_zone": "A", "to_zone": "B", "rate": 5.0}]

    trajectories = engine.simulate_zone_network(zones=zones, transfers=transfers, horizon_seconds=10.0, dt=1.0)

    # In 10s at 5/s, 50 people transfer from A to B
    assert trajectories["A"][-1] == 50.0
    assert trajectories["B"][-1] == 100.0
    # Total people conserved
    assert trajectories["A"][-1] + trajectories["B"][-1] == 150.0


def test_outflow_cannot_exceed_available_people():
    """Physical outflow cannot exceed people present in the source zone."""
    engine = FlowForecastEngine()
    zones = {
        "A": {"initial_count": 10.0, "external_inflow": 0.0, "external_outflow": 0.0},
        "B": {"initial_count": 0.0, "external_inflow": 0.0, "external_outflow": 0.0},
    }
    # Requesting 20/s from a zone with only 10 people
    transfers = [{"from_zone": "A", "to_zone": "B", "rate": 20.0}]

    trajectories = engine.simulate_zone_network(zones=zones, transfers=transfers, horizon_seconds=1.0, dt=1.0)
    assert trajectories["A"][-1] == 0.0
    assert trajectories["B"][-1] == 10.0


def test_sensitivity_envelope():
    """Sensitivity range under stated assumptions [20.0, 46.7] seconds."""
    t_min, t_max = calculate_sensitivity_envelope(
        count_range=(110.0, 130.0),
        growth_range=(1.5, 2.5),
        operating_limit=180.0,
    )
    # Earliest: (180 - 130) / 2.5 = 20.0
    assert pytest.approx(t_min, 0.01) == 20.0
    # Latest: (180 - 110) / 1.5 = 46.666...
    assert pytest.approx(t_max, 0.01) == 46.67
