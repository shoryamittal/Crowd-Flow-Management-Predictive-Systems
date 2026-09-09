"""Unit and restart tests for offline action and recommendation persistence.

Authority: Sentinel_AI_SIH2026_Final_Strategy_Report.pdf (Section 7, 18.5)
"""
import json
from uuid import uuid4

from src.persistence import IncidentJournal


def test_offline_action_persistence_and_restart(tmp_path):
    """GATE-13 & GATE-14: Action transitions survive connection closing and process restart."""
    db_path = tmp_path / "offline_action_test.db"

    # Instance 1: Create journal and advance an action
    j1 = IncidentJournal(db_path)
    j1.initialize()

    action_id = f"act-{uuid4()}"
    incident_id = f"inc-{uuid4()}"
    t1_id = str(uuid4())
    t2_id = str(uuid4())

    j1.record_action_transition(
        transition_id=t1_id,
        action_id=action_id,
        incident_id=incident_id,
        from_state="PROPOSED",
        to_state="APPROVED",
        actor_id="ShiftSupervisor_Patel",
        timestamp_utc="2026-09-09T17:00:00Z",
    )
    j1.record_action_transition(
        transition_id=t2_id,
        action_id=action_id,
        incident_id=incident_id,
        from_state="APPROVED",
        to_state="DELIVERED",
        actor_id="Dispatcher",
        timestamp_utc="2026-09-09T17:00:05Z",
    )
    assert j1.get_latest_action_state(action_id) == "DELIVERED"

    # Also save a DecisionRecommendation
    rec_id = f"rec-{uuid4()}"
    j1.save_recommendation(
        recommendation_id=rec_id,
        incident_id=incident_id,
        created_at_utc="2026-09-09T17:00:00Z",
        selected_candidate_id="METER_UPSTREAM_H",
        action_type="UPSTREAM_METERING",
        feasibility_status="FEASIBLE",
        valid_until_utc="2026-09-09T17:00:07Z",
        summary_message="UPSTREAM METERING — FEASIBLE FOR CURRENT 90 s ANALYSIS WINDOW",
        tradeoffs_description="Bottleneck peak 136; Holding queue +205",
        evaluations_json=json.dumps([{"candidate_id": "METER_UPSTREAM_H", "feasibility": "FEASIBLE"}]),
    )

    # Simulate process death & reboot: open brand new IncidentJournal on same db_path
    j2 = IncidentJournal(db_path)
    j2.initialize()

    # Verify state survived without corruption or alteration
    assert j2.get_latest_action_state(action_id) == "DELIVERED"
    transitions = j2.list_action_transitions(action_id=action_id)
    assert len(transitions) == 2
    assert transitions[0].to_state == "APPROVED"
    assert transitions[1].to_state == "DELIVERED"
    assert transitions[0].actor_id == "ShiftSupervisor_Patel"

    saved_rec = j2.get_recommendation(rec_id)
    assert saved_rec is not None
    assert saved_rec.selected_candidate_id == "METER_UPSTREAM_H"
    assert saved_rec.feasibility_status == "FEASIBLE"
    assert len(saved_rec.evaluations) == 1

    # Continue lifecycle in new process: DELIVERED -> ACKNOWLEDGED
    t3_id = str(uuid4())
    j2.record_action_transition(
        transition_id=t3_id,
        action_id=action_id,
        incident_id=incident_id,
        from_state="DELIVERED",
        to_state="ACKNOWLEDGED",
        actor_id="RPF_Marshal",
        timestamp_utc="2026-09-09T17:00:15Z",
    )
    assert j2.get_latest_action_state(action_id) == "ACKNOWLEDGED"
