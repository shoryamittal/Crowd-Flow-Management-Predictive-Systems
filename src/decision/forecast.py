"""Flow Forecast Engine for Sentinel AI Decision Support.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf (Section 8)
Mathematical principle: Conservation of people with deterministic rate integration.
"""
from __future__ import annotations

from typing import Any

from .models import (
    CalibrationState,
    EvidenceStatus,
    ForecastSnapshot,
    QualityState,
)


def calculate_limit_crossing(
    current_count: float,
    operating_limit: float,
    net_growth_rate: float,
) -> float | None:
    """Calculate T_limit = (C - N) / g.

    Returns:
        0.0 if already breached (N >= C).
        None if growth rate <= 0 (no modeled crossing).
        Seconds until limit crossing if g > 0 and N < C.
    """
    if current_count >= operating_limit:
        return 0.0
    if net_growth_rate <= 0.0:
        return None
    return (operating_limit - current_count) / net_growth_rate


def calculate_sensitivity_envelope(
    count_range: tuple[float, float],
    growth_range: tuple[float, float],
    operating_limit: float,
) -> tuple[float | None, float | None]:
    """Calculate sensitivity envelope [T_min, T_max] under explicit parameter assumptions.

    Termed: 'Sensitivity range under stated assumptions' (NEVER '95% confidence').
    """
    n_min, n_max = count_range
    g_min, g_max = growth_range

    # Earliest crossing occurs at highest count and highest growth rate
    t_earliest = None
    if g_max > 0:
        if n_max >= operating_limit:
            t_earliest = 0.0
        else:
            t_earliest = (operating_limit - n_max) / g_max

    # Latest crossing occurs at lowest count and lowest growth rate
    t_latest = None
    if g_min > 0:
        if n_min >= operating_limit:
            t_latest = 0.0
        else:
            t_latest = (operating_limit - n_min) / g_min

    return (t_earliest, t_latest)


class FlowForecastEngine:
    """Deterministic, inspectable conservation model for short-horizon zone forecasting."""

    def __init__(self, default_horizon_seconds: float = 90.0) -> None:
        self.default_horizon_seconds = default_horizon_seconds

    def forecast_zone(
        self,
        zone_id: str,
        current_count: float,
        operating_limit: float,
        inflow_rate: float,
        outflow_rate: float,
        horizon_seconds: float | None = None,
        evidence_snapshot_id: str = "",
        quality_state: QualityState = QualityState.LIVE,
        calibration_state: CalibrationState = CalibrationState.CALIBRATED,
        unit: str = "people",
        sensitivity_count_delta: float | None = None,
        sensitivity_growth_delta: float | None = None,
    ) -> ForecastSnapshot:
        """Run single zone forecast with deterministic rate projection."""
        horizon = horizon_seconds if horizon_seconds is not None else self.default_horizon_seconds

        # 1. Failure checks: Stale inputs or missing calibration
        if quality_state in (QualityState.STALE, QualityState.CAMERA_LOST):
            return ForecastSnapshot(
                zone_id=zone_id,
                evidence_snapshot_id=evidence_snapshot_id,
                horizon_seconds=horizon,
                current_count=current_count,
                operating_limit=operating_limit,
                inflow_rate=inflow_rate,
                outflow_rate=outflow_rate,
                net_growth_rate=inflow_rate - outflow_rate,
                modeled_limit_crossing_seconds=None,
                calculation_validity="FORECAST_UNAVAILABLE",
                invalidation_reason="Observation input is STALE or CAMERA_LOST",
                evidence_status=EvidenceStatus.CALCULATED,
            )

        if unit not in ("people", "pax"):
            return ForecastSnapshot(
                zone_id=zone_id,
                evidence_snapshot_id=evidence_snapshot_id,
                horizon_seconds=horizon,
                current_count=current_count,
                operating_limit=operating_limit,
                inflow_rate=inflow_rate,
                outflow_rate=outflow_rate,
                net_growth_rate=inflow_rate - outflow_rate,
                modeled_limit_crossing_seconds=None,
                calculation_validity="FORECAST_UNAVAILABLE",
                invalidation_reason=f"Inconsistent or uncalibrated unit: '{unit}'. Requires 'people'.",
                evidence_status=EvidenceStatus.CALCULATED,
            )

        # 2. Deterministic calculations
        net_growth = inflow_rate - outflow_rate
        is_breached = current_count >= operating_limit
        crossing_time = calculate_limit_crossing(current_count, operating_limit, net_growth)

        # Conservation projection over horizon without artificial clipping
        predicted_at_horizon = current_count + (net_growth * horizon)
        if predicted_at_horizon < 0.0:
            predicted_at_horizon = 0.0

        # Sensitivity envelope if deltas provided
        t_min, t_max = None, None
        if sensitivity_count_delta is not None and sensitivity_growth_delta is not None:
            c_min = max(0.0, current_count - sensitivity_count_delta)
            c_max = current_count + sensitivity_count_delta
            g_min = net_growth - sensitivity_growth_delta
            g_max = net_growth + sensitivity_growth_delta
            t_min, t_max = calculate_sensitivity_envelope((c_min, c_max), (g_min, g_max), operating_limit)

        return ForecastSnapshot(
            zone_id=zone_id,
            evidence_snapshot_id=evidence_snapshot_id,
            horizon_seconds=horizon,
            current_count=current_count,
            operating_limit=operating_limit,
            inflow_rate=inflow_rate,
            outflow_rate=outflow_rate,
            net_growth_rate=net_growth,
            modeled_limit_crossing_seconds=crossing_time,
            is_breached_now=is_breached,
            predicted_count_at_horizon=predicted_at_horizon,
            sensitivity_min_seconds=t_min,
            sensitivity_max_seconds=t_max,
            calculation_validity="VALID",
            invalidation_reason=None,
            evidence_status=EvidenceStatus.CALCULATED,
        )

    def simulate_zone_network(
        self,
        zones: dict[str, dict[str, Any]],
        transfers: list[dict[str, Any]],
        horizon_seconds: float = 90.0,
        dt: float = 1.0,
    ) -> dict[str, list[float]]:
        """Run multi-zone discrete time-step conservation simulation.

        Guarantees:
        - Transfers from A to B: symmetrical departure from A and arrival at B.
        - Outflow cannot exceed people available in A.
        - Overloaded zones are NOT clipped at operating limits.
        - Deterministic math, zero stochastic random calls.
        """
        # Initialize state series
        timesteps = int(horizon_seconds / dt)
        trajectories: dict[str, list[float]] = {
            z_id: [float(z_data["initial_count"])] for z_id, z_data in zones.items()
        }

        current_counts = {z_id: float(z_data["initial_count"]) for z_id, z_data in zones.items()}

        for step in range(timesteps):
            t = step * dt
            # Step net changes
            deltas: dict[str, float] = {z_id: 0.0 for z_id in zones}

            # 1. External arrivals / departures
            for z_id, z_data in zones.items():
                ext_in = z_data.get("external_inflow", 0.0)
                ext_out = z_data.get("external_outflow", 0.0)
                # Max outflow cannot exceed available people in dt
                actual_ext_out = min(ext_out, current_counts[z_id] / dt)
                deltas[z_id] += (ext_in - actual_ext_out) * dt

            # 2. Inter-zone transfers (symmetrical)
            for tr in transfers:
                src = tr["from_zone"]
                dst = tr["to_zone"]
                requested_rate = tr["rate"]
                # Outflow clamp
                available = current_counts[src] / dt
                actual_rate = min(requested_rate, available)

                deltas[src] -= actual_rate * dt
                deltas[dst] += actual_rate * dt

            # Update and record
            for z_id in zones:
                current_counts[z_id] = max(0.0, current_counts[z_id] + deltas[z_id])
                trajectories[z_id].append(current_counts[z_id])

        return trajectories
