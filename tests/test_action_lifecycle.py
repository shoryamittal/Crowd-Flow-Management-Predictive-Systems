"""Unit tests for Human Operator Action Lifecycle.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf (Section 6, 18.4)
"""
import pytest
from uuid import uuid4

from src.persistence import IncidentJournal


@pytest.fixture
def journal(tmp_path):
    j = IncidentJournal(tmp_path / "test_lifecycle.db")
    j.initialize()
    return j


def test_action_lifecycle_legal_progression(journal):
    """Enforce legal transition sequence: PROPOSED -> APPROVED -> DELIVERED -> ACKNOWLEDGED -> COMPLETED -> VERIFIED."""
    action_id = f"act-{uuid4()}"
    incident_id = f"inc-{uuid4()}"

    # 1. Proposed -> Approved
    res = journal.record_action_transition(
        transition_id=str(uuid4()),
        action_id=action_id,
        incident_id=incident_id,
        from_state="PROPOSED",
        to_state="APPROVED",
        actor_id="Operator_Sharma",
        timestamp_utc="2026-09-09T16:00:00Z",
        notes="Approved upstream metering",
    )
    assert res is True
    assert journal.get_latest_action_state(action_id) == "APPROVED"

    # 2. Approved -> Delivered
    res = journal.record_action_transition(
        transition_id=str(uuid4()),
        action_id=action_id,
        incident_id=incident_id,
        from_state="APPROVED",
        to_state="DELIVERED",
        actor_id="System_Dispatch",
        timestamp_utc="2026-09-09T16:00:02Z",
    )
    assert res is True
    assert journal.get_latest_action_state(action_id) == "DELIVERED"

    # 3. Delivered -> Acknowledged
    res = journal.record_action_transition(
        transition_id=str(uuid4()),
        action_id=action_id,
        incident_id=incident_id,
        from_state="DELIVERED",
        to_state="ACKNOWLEDGED",
        actor_id="RPF_Constable_Verma",
        timestamp_utc="2026-09-09T16:00:08Z",
        notes="Radio acknowledgement from Gate 2",
    )
    assert res is True
    assert journal.get_latest_action_state(action_id) == "ACKNOWLEDGED"

    # 4. Acknowledged -> Completed
    res = journal.record_action_transition(
        transition_id=str(uuid4()),
        action_id=action_id,
        incident_id=incident_id,
        from_state="ACKNOWLEDGED",
        to_state="COMPLETED",
        actor_id="RPF_Constable_Verma",
        timestamp_utc="2026-09-09T16:00:45Z",
        notes="Barriers in place, metering active",
    )
    assert res is True
    assert journal.get_latest_action_state(action_id) == "COMPLETED"

    # 5. Completed -> Verified (requires post-action observation)
    res = journal.record_action_transition(
        transition_id=str(uuid4()),
        action_id=action_id,
        incident_id=incident_id,
        from_state="COMPLETED",
        to_state="VERIFIED",
        actor_id="Perception_Engine",
        timestamp_utc="2026-09-09T16:01:10Z",
        evidence_snapshot_id="snap-cctv-trend-negative-001",
        notes="Bottleneck count reduced from 136 to 98",
    )
    assert res is True
    assert journal.get_latest_action_state(action_id) == "VERIFIED"

    # Verify chronological transition history
    history = journal.list_action_transitions(action_id=action_id)
    assert len(history) == 5
    states = [h.to_state for h in history]
    assert states == ["APPROVED", "DELIVERED", "ACKNOWLEDGED", "COMPLETED", "VERIFIED"]


def test_illegal_transitions_raise_value_error(journal):
    """GATE-06: Dispatch does not auto-acknowledge; illegal skips are rejected."""
    action_id = f"act-{uuid4()}"
    incident_id = f"inc-{uuid4()}"

    # Cannot skip PROPOSED -> ACKNOWLEDGED directly
    with pytest.raises(ValueError) as exc:
        journal.record_action_transition(
            transition_id=str(uuid4()),
            action_id=action_id,
            incident_id=incident_id,
            from_state="PROPOSED",
            to_state="ACKNOWLEDGED",
            actor_id="Operator",
            timestamp_utc="2026-09-09T16:00:00Z",
        )
    assert "Illegal action transition" in str(exc.value)

    # Cannot skip DELIVERED -> COMPLETED without ACKNOWLEDGED
    with pytest.raises(ValueError) as exc:
        journal.record_action_transition(
            transition_id=str(uuid4()),
            action_id=action_id,
            incident_id=incident_id,
            from_state="DELIVERED",
            to_state="COMPLETED",
            actor_id="Operator",
            timestamp_utc="2026-09-09T16:00:00Z",
        )
    assert "Illegal action transition" in str(exc.value)


def test_verification_requires_subsequent_observation(journal):
    """GATE-15: Completed does not imply verified; post-action observation required."""
    action_id = f"act-{uuid4()}"
    incident_id = f"inc-{uuid4()}"

    with pytest.raises(ValueError) as exc:
        journal.record_action_transition(
            transition_id=str(uuid4()),
            action_id=action_id,
            incident_id=incident_id,
            from_state="COMPLETED",
            to_state="VERIFIED",
            actor_id="Operator",
            timestamp_utc="2026-09-09T16:00:00Z",
            evidence_snapshot_id=None,  # Missing evidence!
        )
    assert "requires a valid post-action evidence_snapshot_id" in str(exc.value)


def test_transition_idempotency(journal):
    """Replaying the same transition_id is an idempotent no-op."""
    action_id = f"act-{uuid4()}"
    incident_id = f"inc-{uuid4()}"
    tid = str(uuid4())

    res1 = journal.record_action_transition(
        transition_id=tid,
        action_id=action_id,
        incident_id=incident_id,
        from_state="PROPOSED",
        to_state="APPROVED",
        actor_id="Operator",
        timestamp_utc="2026-09-09T16:00:00Z",
    )
    assert res1 is True

    # Same transition_id again
    res2 = journal.record_action_transition(
        transition_id=tid,
        action_id=action_id,
        incident_id=incident_id,
        from_state="PROPOSED",
        to_state="APPROVED",
        actor_id="Operator",
        timestamp_utc="2026-09-09T16:00:00Z",
    )
    assert res2 is False  # Idempotent no-op
