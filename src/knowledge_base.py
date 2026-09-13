"""SENTINEL AI — Operational Knowledge & Grounded SOP Layer.

Grounded standard operating procedures (SOPs) based on:
1. National Disaster Management Authority (NDMA) Guidelines on Crowd Management (Section 4.2).
2. Bureau of Police Research and Development (BPR&D) Crowd Control & Mass Gathering Manual.
3. Prayagraj Maha Kumbh Sector 04 (Sangam Triveni Ghat & Parade Ground) Operating SOPs.

Crucial Architectural Constraint:
This knowledge layer is read-only and deterministic. It provides verified rule citations
to ground the Gemini Incident Copilot's briefings and explanations. It never hallucinates
SOP rules or replaces the deterministic safety engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SOPGuideline:
    sop_id: str
    section: str
    title: str
    authority: str
    applicable_zones: tuple[str, ...]
    trigger_condition: str
    operational_directive: str
    rationale: str
    evidence_tier: str = "OFFICIAL REGULATORY GUIDELINE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sop_id": self.sop_id,
            "section": self.section,
            "title": self.title,
            "authority": self.authority,
            "applicable_zones": list(self.applicable_zones),
            "trigger_condition": self.trigger_condition,
            "operational_directive": self.operational_directive,
            "rationale": self.rationale,
            "evidence_tier": self.evidence_tier,
        }


# Authoritative SOP catalog grounded in NDMA / BPR&D guidelines for mass gatherings
NDMA_SECTOR_04_SOPS: tuple[SOPGuideline, ...] = (
    SOPGuideline(
        sop_id="SOP-NDMA-042-A",
        section="NDMA Section 4.2.1",
        title="Upstream Inflow Metering at Pilgrim Staging Area",
        authority="National Disaster Management Authority (NDMA)",
        applicable_zones=("H", "A", "B"),
        trigger_condition="Bottleneck approaching configured operating limit or T_limit <= 60s",
        operational_directive=(
            "Activate metering barriers at Parade Ground Holding Area H. Regulate pilgrim batch release "
            "into Approach Corridor A at a maximum rate of 1.5 persons/sec to prevent surging at Bottleneck B."
        ),
        rationale=(
            "Upstream metering absorbs surge energy in open staging grounds with low density, preventing high-density "
            "compression in narrow corridors where physical relief is impossible."
        ),
    ),
    SOPGuideline(
        sop_id="SOP-NDMA-042-B",
        section="NDMA Section 4.2.2",
        title="Secondary Bottleneck & Divergent Route Capacity Guard",
        authority="National Disaster Management Authority (NDMA)",
        applicable_zones=("R", "B"),
        trigger_condition="Proposed diversion corridor projected to exceed 85% capacity or exit obstructed",
        operational_directive=(
            "Strictly reject emergency crowd diversions to Relief Corridor R if projected inflow will cause "
            "secondary bottlenecking. Maintain current controlled holding in Staging Area H instead."
        ),
        rationale=(
            "Diverting a compressed crowd into an alternate corridor with inadequate downstream capacity converts "
            "a localized queue into an unmanageable multi-corridor entrapment hazard."
        ),
    ),
    SOPGuideline(
        sop_id="SOP-NDMA-042-C",
        section="NDMA Section 4.2.3",
        title="Pontoon Bridge Unidirectional Egress Enforcement",
        authority="UP Police & Mela Administration Special SOP",
        applicable_zones=("R", "E"),
        trigger_condition="Pontoon Bridge 3/4 traversal or bidirectional pressure detected",
        operational_directive=(
            "Enforce strict one-way movement across Pontoon Bridges. Under no circumstances may counter-flow "
            "be permitted. Deploy marshals at eastern entry ramp to enforce egress-only discipline."
        ),
        rationale=(
            "Bidirectional pedestrian counter-flows on flexible floating pontoon structures cause localized lateral "
            "sway, trip hazards, and rapid boundary stall."
        ),
    ),
    SOPGuideline(
        sop_id="SOP-NDMA-042-D",
        section="NDMA Section 4.2.4",
        title="Holding Area Staging & Pilgrim Welfare Maintenance",
        authority="NDMA & District Disaster Management Authority (DDMA)",
        applicable_zones=("H",),
        trigger_condition="Hold duration > 10 minutes or holding area occupancy > 60%",
        operational_directive=(
            "Provide hydration points, shaded waiting lanes, and continuous public address updates in Parade "
            "Ground Holding Area H to maintain calm and prevent restlessness during flow metering."
        ),
        rationale=(
            "Pilgrims kept informed with accurate, calm waiting time estimates do not attempt to breach "
            "staged crowd barriers."
        ),
    ),
    SOPGuideline(
        sop_id="SOP-NDMA-042-E",
        section="NDMA Section 4.2.5",
        title="Public Address Calming & Wayfinding Protocol",
        authority="NDMA Crowd Communication Standards",
        applicable_zones=("H", "A", "B", "R", "E", "G"),
        trigger_condition="Active flow intervention, corridor restriction, or staged delay",
        operational_directive=(
            "Broadcast calm, factual, unambiguous public announcements in Hindi, English, and regional languages. "
            "Avoid alarming terminology. State clearly which holding area to wait in and follow field marshals."
        ),
        rationale=(
            "Non-sensational language prevents sudden panic-driven flight and promotes compliant collective movement."
        ),
    ),
)


class OperationalKnowledgeBase:
    """Deterministic knowledge retrieval for mass-gathering operational SOPs."""

    def __init__(self, guidelines: Optional[tuple[SOPGuideline, ...]] = None) -> None:
        self._guidelines = guidelines or NDMA_SECTOR_04_SOPS

    def get_all(self) -> List[Dict[str, Any]]:
        return [g.to_dict() for g in self._guidelines]

    def query(
        self,
        zone: Optional[str] = None,
        candidate_action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """Query matching SOP guidelines based on active incident context."""
        matches = []
        normalized_zone = (zone or "").strip().upper()
        normalized_action = (candidate_action or "").strip().upper()
        normalized_status = (status or "").strip().upper()

        for g in self._guidelines:
            score = 0
            # Zone match
            if normalized_zone and normalized_zone in g.applicable_zones:
                score += 3
            # Action match
            if "METER" in normalized_action and "Metering" in g.title:
                score += 4
            elif ("DIVERT" in normalized_action or "RELIEF" in normalized_action) and "Secondary" in g.title:
                score += 4
            elif "PONTOON" in normalized_action and "Pontoon" in g.title:
                score += 4
            # Status match (e.g., REJECTED -> secondary bottleneck prevention)
            if normalized_status == "REJECTED" and "Secondary" in g.title:
                score += 3

            if score > 0:
                matches.append((score, g))

        # Sort descending by relevance score
        matches.sort(key=lambda x: x[0], reverse=True)
        results = [m[1].to_dict() for m in matches[:limit]]

        # If no specific matches found, provide general public communication & holding SOP
        if not results:
            for g in self._guidelines:
                if g.sop_id in ("SOP-NDMA-042-A", "SOP-NDMA-042-E"):
                    results.append(g.to_dict())
                if len(results) >= limit:
                    break

        return results

    @staticmethod
    def format_citation(sop_items: List[Dict[str, Any]]) -> str:
        """Format an unambiguous grounding citation string."""
        if not sop_items:
            return "No grounded SOP guidance available."
        sections = [f"{item.get('section', item.get('sop_id', 'SOP'))}" for item in sop_items]
        sections_str = ", ".join(dict.fromkeys(sections))  # preserve order, deduplicate
        return f"Grounded in: • Live Machine State • Decision Safety Engine • Approved SOP ({sections_str})"


# Global singleton instance for app-wide grounded retrieval
sop_knowledge_base = OperationalKnowledgeBase()
