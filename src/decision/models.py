"""Data contracts and domain models for Sentinel AI Decision Support System.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class _StringEnum(str, Enum):
    """Enum whose values serialize naturally in JSON-oriented consumers."""


class EvidenceStatus(_StringEnum):
    OBSERVED = "OBSERVED"        # Direct physical sensor / camera measurement
    CALCULATED = "CALCULATED"    # Deterministic calculation from defined inputs
    SCENARIO = "SCENARIO"        # Synthetic, calibrated, or operator scenario input
    PLANNED = "PLANNED"          # Future configuration or site-survey target


class QualityState(_StringEnum):
    LIVE = "LIVE"
    STALE = "STALE"
    CAMERA_LOST = "CAMERA_LOST"
    INPUT_RECOVERING = "INPUT_RECOVERING"


class CalibrationState(_StringEnum):
    UNCALIBRATED = "UNCALIBRATED"
    CALIBRATED = "CALIBRATED"


class ZoneRole(_StringEnum):
    HOLDING_AREA = "HOLDING_AREA"
    APPROACH_CORRIDOR = "APPROACH_CORRIDOR"
    BOTTLENECK = "BOTTLENECK"
    DISPERSAL_DESTINATION = "DISPERSAL_DESTINATION"
    RELIEF_CORRIDOR = "RELIEF_CORRIDOR"
    EGRESS_EXIT = "EGRESS_EXIT"


class RouteStatus(_StringEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNVERIFIED = "UNVERIFIED"


class ActionType(_StringEnum):
    NO_ACTION = "NO_ACTION"
    UPSTREAM_METERING = "UPSTREAM_METERING"
    PERMITTED_DIVERSION = "PERMITTED_DIVERSION"


class FeasibilityStatus(_StringEnum):
    FEASIBLE = "FEASIBLE"
    REJECTED = "REJECTED"


class ActionLifecycleState(_StringEnum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    DELIVERED = "DELIVERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(timezone.utc)


def _serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, (tuple, list)):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


@dataclass(frozen=True, slots=True)
class ZoneConfig:
    zone_id: str
    name: str
    role: ZoneRole
    configured_operating_limit: float
    physical_max_capacity: float
    unit: str = "people"

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class RouteConfig:
    route_id: str
    source_zone_id: str
    target_zone_id: str
    max_flow_capacity: float          # pax/s
    permitted_direction: str = "UNIDIRECTIONAL"
    status: RouteStatus = RouteStatus.OPEN
    last_verified_utc: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class ObservationSnapshot:
    """Conceptually represents an observation from Perception Engine."""
    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    observed_at_utc: datetime = field(default_factory=utc_now)
    frame_id: int = 0
    frame_age_ms: float = 0.0
    source: str = "camera_0"
    source_mode: str = "CAMERA"
    zone_id: str = "zone_b_bottleneck"
    observed_value: float = 0.0
    unit: str = "relative_occupancy_index"
    evidence_status: EvidenceStatus = EvidenceStatus.OBSERVED
    quality_state: QualityState = QualityState.LIVE
    calibration_state: CalibrationState = CalibrationState.UNCALIBRATED
    model_version: str = "yolov8s.pt"
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class ForecastSnapshot:
    """Output of the deterministic Flow Forecast Engine."""
    forecast_id: str = field(default_factory=lambda: str(uuid4()))
    zone_id: str = ""
    created_at_utc: datetime = field(default_factory=utc_now)
    evidence_snapshot_id: str = ""
    horizon_seconds: float = 90.0
    current_count: float = 0.0
    operating_limit: float = 0.0
    inflow_rate: float = 0.0
    outflow_rate: float = 0.0
    net_growth_rate: float = 0.0
    modeled_limit_crossing_seconds: float | None = None
    is_breached_now: bool = False
    predicted_count_at_horizon: float = 0.0
    sensitivity_min_seconds: float | None = None
    sensitivity_max_seconds: float | None = None
    calculation_validity: str = "VALID"
    invalidation_reason: str | None = None
    evidence_status: EvidenceStatus = EvidenceStatus.CALCULATED

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class ActionCandidate:
    candidate_id: str
    action_type: ActionType
    title: str
    source_zone_id: str
    target_zone_id: str | None = None
    diverted_flow_rate: float = 0.0
    metered_inflow_rate: float = 0.0
    staff_response_delay_seconds: float = 8.0
    planning_margin_seconds: float = 5.0

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class ActionEvaluation:
    candidate_id: str
    action_type: ActionType
    feasibility: FeasibilityStatus
    rejection_reasons: tuple[str, ...] = ()
    primary_zone_id: str = ""
    primary_zone_peak_count: float = 0.0
    primary_zone_horizon_count: float = 0.0
    affected_zones_summary: dict[str, Any] = field(default_factory=dict)
    added_waiting_cost: float = 0.0
    usable_response_window_seconds: float = 0.0
    recommendation_validity_seconds: float = 0.0
    evidence_status: EvidenceStatus = EvidenceStatus.CALCULATED

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class DecisionRecommendation:
    recommendation_id: str = field(default_factory=lambda: str(uuid4()))
    created_at_utc: datetime = field(default_factory=utc_now)
    scenario_name: str = "SCENARIO"
    selected_candidate_id: str | None = None
    action_type: ActionType | None = None
    status: str = "ACTIVE"
    valid_until_utc: datetime = field(default_factory=utc_now)
    validity_duration_seconds: float = 0.0
    summary_message: str = ""
    tradeoffs_description: str = ""
    evaluations: tuple[ActionEvaluation, ...] = ()
    evidence_badge: EvidenceStatus = EvidenceStatus.SCENARIO

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class ActionTransitionEvent:
    transition_id: str = field(default_factory=lambda: str(uuid4()))
    action_id: str = ""
    incident_id: str = ""
    from_state: ActionLifecycleState = ActionLifecycleState.PROPOSED
    to_state: ActionLifecycleState = ActionLifecycleState.APPROVED
    actor_id: str = "Operator"
    timestamp_utc: datetime = field(default_factory=utc_now)
    notes: str | None = None
    evidence_snapshot_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))
