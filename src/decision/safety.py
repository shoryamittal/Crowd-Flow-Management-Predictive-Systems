"""Decision Safety Engine (Decision Safety Layer) for Sentinel AI.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf (Section 4.6, 4.7, 9)
Core Principle: Before recommending that people are moved, simulate all affected
connected zones and reject any action that transfers congestion into another
constrained zone.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from .models import (
    ActionCandidate,
    ActionEvaluation,
    ActionType,
    DecisionRecommendation,
    EvidenceStatus,
    FeasibilityStatus,
    QualityState,
    RouteConfig,
    RouteStatus,
    ZoneConfig,
    utc_now,
)


class DecisionSafetyEngine:
    """Evaluates candidate interventions against hard safety constraints across connected zones."""

    def __init__(self, horizon_seconds: float = 90.0) -> None:
        self.horizon_seconds = horizon_seconds

    def evaluate_candidate(
        self,
        candidate: ActionCandidate,
        zones: dict[str, ZoneConfig],
        routes: dict[str, RouteConfig],
        current_zone_counts: dict[str, float],
        base_flows: dict[str, dict[str, float]],  # zone_id -> {"inflow": float, "outflow": float}
        quality_states: dict[str, QualityState] | None = None,
        earliest_crossing_seconds: float | None = None,
    ) -> ActionEvaluation:
        """Simulate all affected zones for a single candidate action and check constraints."""
        rejection_reasons: list[str] = []
        affected_zones: dict[str, Any] = {}
        primary_zone_id = candidate.source_zone_id
        target_zone_id = candidate.target_zone_id

        # Quality check
        if quality_states:
            for z_id in (primary_zone_id, target_zone_id):
                if z_id and quality_states.get(z_id) in (QualityState.STALE, QualityState.CAMERA_LOST):
                    rejection_reasons.append(f"Observation for zone '{z_id}' is STALE or CAMERA_LOST.")

        # Route checks for diversion
        if candidate.action_type == ActionType.PERMITTED_DIVERSION:
            if not target_zone_id:
                rejection_reasons.append("Diversion target zone unspecified.")
            else:
                route_key = f"{primary_zone_id}->{target_zone_id}"
                route = routes.get(route_key)
                if not route:
                    # Look for any matching route
                    matching = [r for r in routes.values() if r.source_zone_id == primary_zone_id and r.target_zone_id == target_zone_id]
                    route = matching[0] if matching else None

                if not route:
                    rejection_reasons.append(f"No configured route from '{primary_zone_id}' to '{target_zone_id}'.")
                else:
                    if route.status == RouteStatus.CLOSED:
                        rejection_reasons.append(f"Route '{route.route_id}' is CLOSED.")
                    elif route.status == RouteStatus.UNVERIFIED:
                        rejection_reasons.append(f"Route '{route.route_id}' is UNVERIFIED.")
                    if route.permitted_direction != "UNIDIRECTIONAL" and route.permitted_direction != "BIDIRECTIONAL":
                        rejection_reasons.append(f"Route '{route.route_id}' has unpermitted flow direction.")

        # Perform deterministic trajectory evaluation
        delay = candidate.staff_response_delay_seconds
        margin = candidate.planning_margin_seconds
        horizon = self.horizon_seconds

        # Base parameters for primary bottleneck
        b_count = current_zone_counts.get(primary_zone_id, 0.0)
        b_limit = zones[primary_zone_id].configured_operating_limit if primary_zone_id in zones else 180.0
        b_inflow = base_flows.get(primary_zone_id, {}).get("inflow", 4.0)
        b_outflow = base_flows.get(primary_zone_id, {}).get("outflow", 2.0)
        b_net = b_inflow - b_outflow

        primary_peak = b_count
        primary_horizon = b_count
        added_waiting_cost = 0.0
        usable_response_window = 0.0

        if candidate.action_type == ActionType.NO_ACTION:
            # Constant rate projection
            primary_peak = b_count + (b_net * horizon)
            primary_horizon = primary_peak
            if b_net > 0:
                t_crossing = (b_limit - b_count) / b_net if b_count < b_limit else 0.0
                usable_response_window = max(0.0, t_crossing - delay - margin)
            else:
                t_crossing = None
                usable_response_window = horizon

            affected_zones[primary_zone_id] = {
                "initial": b_count,
                "horizon_count": primary_horizon,
                "peak_count": primary_peak,
                "limit": b_limit,
                "breaches_limit": primary_horizon > b_limit,
                "crossing_seconds": t_crossing,
            }
            if primary_horizon > b_limit:
                rejection_reasons.append(f"Primary zone '{primary_zone_id}' breaches operating limit (Count: {primary_horizon:.1f} at {horizon:.0f}s; Limit: {b_limit:.0f}).")

        elif candidate.action_type == ActionType.UPSTREAM_METERING:
            # During delay (0 to delay): accumulation continues at base rate
            count_at_delay = b_count + (b_net * delay)
            primary_peak = max(b_count, count_at_delay)

            # After delay (delay to horizon): inflow throttled to metered_inflow_rate
            remaining_time = max(0.0, horizon - delay)
            metered_inflow = candidate.metered_inflow_rate if candidate.metered_inflow_rate > 0 else 1.5
            metered_net = metered_inflow - b_outflow  # e.g., 1.5 - 2.0 = -0.5

            primary_horizon = max(0.0, count_at_delay + (metered_net * remaining_time))

            # Upstream holding area simulation
            holding_zone_id = "zone_h_holding" if "zone_h_holding" in zones else "Holding H"
            if holding_zone_id not in zones:
                # Find any holding area
                for z in zones.values():
                    if z.role.value == "HOLDING_AREA":
                        holding_zone_id = z.zone_id
                        break

            h_initial = current_zone_counts.get(holding_zone_id, 100.0)
            h_limit = zones[holding_zone_id].configured_operating_limit if holding_zone_id in zones else 450.0

            # Withheld flow per second: base_inflow - metered_inflow
            withheld_rate = max(0.0, b_inflow - metered_inflow)  # e.g. 4.0 - 1.5 = 2.5
            added_waiting_cost = withheld_rate * remaining_time  # e.g. 2.5 * 82 = 205
            h_horizon = h_initial + added_waiting_cost

            # Earliest breach window calculation (using sensitivity min if provided, else nominal crossing)
            t_base_crossing = (b_limit - b_count) / b_net if (b_net > 0 and b_count < b_limit) else 30.0
            effective_crossing = earliest_crossing_seconds if earliest_crossing_seconds is not None else t_base_crossing
            usable_response_window = max(0.0, effective_crossing - delay - margin)

            affected_zones[primary_zone_id] = {
                "initial": b_count,
                "horizon_count": primary_horizon,
                "peak_count": primary_peak,
                "limit": b_limit,
                "breaches_limit": primary_peak > b_limit,
            }
            affected_zones[holding_zone_id] = {
                "initial": h_initial,
                "horizon_count": h_horizon,
                "queue_added": added_waiting_cost,
                "limit": h_limit,
                "breaches_limit": h_horizon > h_limit,
            }

            # Check holding capacity constraint
            if h_horizon > h_limit:
                rejection_reasons.append(f"Upstream holding area '{holding_zone_id}' exceeds capacity (Count: {h_horizon:.1f}; Limit: {h_limit:.0f}).")
            if primary_peak > b_limit:
                rejection_reasons.append(f"Peak count in '{primary_zone_id}' exceeds limit during response delay (Peak: {primary_peak:.1f}; Limit: {b_limit:.0f}).")

        elif candidate.action_type == ActionType.PERMITTED_DIVERSION:
            # During delay (0 to delay): base flow continues
            count_at_delay = b_count + (b_net * delay)
            primary_peak = max(b_count, count_at_delay)
            remaining_time = max(0.0, horizon - delay)

            # Divert withheld rate into Relief Corridor R
            diverted_rate = candidate.diverted_flow_rate if candidate.diverted_flow_rate > 0 else 2.5
            b_reduced_inflow = b_inflow - diverted_rate
            primary_horizon = max(0.0, count_at_delay + ((b_reduced_inflow - b_outflow) * remaining_time))

            # Relief corridor evaluation
            r_id = target_zone_id or "zone_r_relief"
            r_initial = current_zone_counts.get(r_id, 80.0)
            r_limit = zones[r_id].configured_operating_limit if r_id in zones else 160.0
            r_clearance = base_flows.get(r_id, {}).get("outflow", 0.5)

            # Net addition in R after delay = diverted_rate - clearance
            r_net_growth = diverted_rate - r_clearance  # e.g., 2.5 - 0.5 = +2.0
            r_horizon = r_initial + (r_net_growth * remaining_time)

            r_crossing_time = None
            if r_net_growth > 0:
                time_to_add = (r_limit - r_initial) / r_net_growth
                r_crossing_time = delay + time_to_add

            affected_zones[primary_zone_id] = {
                "initial": b_count,
                "horizon_count": primary_horizon,
                "peak_count": primary_peak,
                "limit": b_limit,
                "breaches_limit": False,
            }
            affected_zones[r_id] = {
                "initial": r_initial,
                "horizon_count": r_horizon,
                "limit": r_limit,
                "net_growth_rate": r_net_growth,
                "crossing_seconds": r_crossing_time,
                "breaches_limit": r_horizon > r_limit,
            }

            if r_horizon > r_limit:
                rejection_reasons.append(
                    f"Receiving corridor '{r_id}' exceeds configured operating limit at t = {r_crossing_time:.0f} s (Projected: {r_horizon:.1f}, Limit: {r_limit:.0f})."
                )

        feasibility = FeasibilityStatus.FEASIBLE if not rejection_reasons else FeasibilityStatus.REJECTED
        validity_duration = usable_response_window if usable_response_window > 0 else 7.0

        return ActionEvaluation(
            candidate_id=candidate.candidate_id,
            action_type=candidate.action_type,
            feasibility=feasibility,
            rejection_reasons=tuple(rejection_reasons),
            primary_zone_id=primary_zone_id,
            primary_zone_peak_count=primary_peak,
            primary_zone_horizon_count=primary_horizon,
            affected_zones_summary=affected_zones,
            added_waiting_cost=added_waiting_cost,
            usable_response_window_seconds=usable_response_window,
            recommendation_validity_seconds=validity_duration,
            evidence_status=EvidenceStatus.CALCULATED,
        )

    def evaluate_and_rank(
        self,
        candidates: list[ActionCandidate],
        zones: dict[str, ZoneConfig],
        routes: dict[str, RouteConfig],
        current_zone_counts: dict[str, float],
        base_flows: dict[str, dict[str, float]],
        quality_states: dict[str, QualityState] | None = None,
        scenario_name: str = "SIH_REFERENCE_SCENARIO",
        earliest_crossing_seconds: float | None = None,
    ) -> DecisionRecommendation:
        """Evaluate all candidate actions and rank remaining feasible actions."""
        evaluations: list[ActionEvaluation] = []
        for cand in candidates:
            ev = self.evaluate_candidate(
                candidate=cand,
                zones=zones,
                routes=routes,
                current_zone_counts=current_zone_counts,
                base_flows=base_flows,
                quality_states=quality_states,
                earliest_crossing_seconds=earliest_crossing_seconds,
            )
            evaluations.append(ev)

        # Stage 1: Filter feasible candidates
        feasible = [e for e in evaluations if e.feasibility == FeasibilityStatus.FEASIBLE]

        if not feasible:
            return DecisionRecommendation(
                scenario_name=scenario_name,
                selected_candidate_id=None,
                action_type=None,
                status="NO_FEASIBLE_OPTION_FOUND",
                valid_until_utc=utc_now(),
                validity_duration_seconds=0.0,
                summary_message="NO FEASIBLE OPTION FOUND — All candidate actions violate connected-zone safety constraints.",
                tradeoffs_description="Every pre-approved intervention causes secondary corridor overload or exceeds holding capacity. Engage manual field coordination protocol.",
                evaluations=tuple(evaluations),
                evidence_badge=EvidenceStatus.SCENARIO,
            )

        # Stage 2: Rank feasible by (1) lowest primary zone horizon count, (2) lowest waiting cost
        feasible.sort(key=lambda x: (x.primary_zone_horizon_count, x.added_waiting_cost))
        best = feasible[0]

        valid_duration = best.recommendation_validity_seconds
        valid_until = utc_now() + timedelta(seconds=valid_duration)

        summary = f"{best.action_type.value.replace('_', ' ')} — FEASIBLE FOR CURRENT {self.horizon_seconds:.0f} s ANALYSIS WINDOW"
        tradeoffs = f"Bottleneck count reduced to {best.primary_zone_horizon_count:.0f} (peak {best.primary_zone_peak_count:.0f}); added holding queue: +{best.added_waiting_cost:.0f} pax. Recommendation valid for {valid_duration:.0f} s under current assumptions."

        return DecisionRecommendation(
            scenario_name=scenario_name,
            selected_candidate_id=best.candidate_id,
            action_type=best.action_type,
            status="ACTIVE",
            valid_until_utc=valid_until,
            validity_duration_seconds=valid_duration,
            summary_message=summary,
            tradeoffs_description=tradeoffs,
            evaluations=tuple(evaluations),
            evidence_badge=EvidenceStatus.SCENARIO,
        )
