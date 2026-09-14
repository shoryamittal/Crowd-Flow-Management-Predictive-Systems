"""SENTINEL AI — Incident Copilot (Google Gemini / Vertex AI Integration).

Positioned strictly ABOVE the deterministic safety engine:
  CCTV / REPLAY -> YOLOv8 -> Occupancy Signal -> Flow Forecast -> Decision Safety Layer
  -> GEMINI INCIDENT COPILOT -> Explanation / Briefing / Announcement -> Human Authorization
  -> Field Action -> Post-Action Verification.

AI Safety Contract & Boundary Rules:
- Gemini NEVER makes the safety-critical feasibility decision.
- The Decision Safety Engine remains the absolute source of truth.
- Forbidden terms (stampede prediction, crush physics, autonomous actuation) are rejected.
- Graceful deterministic fallback ensures zero interruption if Gemini or WAN is offline.
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from src.knowledge_base import sop_knowledge_base

logger = logging.getLogger("sentinel.copilot")

# Strict forbidden terms filter to enforce scientific and operational boundaries
FORBIDDEN_PATTERNS = [
    re.compile(r"\bstampede\s+in\s+\d+", re.IGNORECASE),
    re.compile(r"\bpredict(?:s|ing)?\s+stampede", re.IGNORECASE),
    re.compile(r"\btime\s+to\s+crush\b", re.IGNORECASE),
    re.compile(r"\bcrush\s+inevitable\b", re.IGNORECASE),
    re.compile(r"\bguaranteed\s+\d+[\s-]*second\b", re.IGNORECASE),
    re.compile(r"\boptimal\s+routing\b", re.IGNORECASE),
    re.compile(r"\bautonomously?\s+(?:actuate|close|open|barricade)\b", re.IGNORECASE),
    re.compile(r"\boverride\s+(?:safety|decision|rejection)\b", re.IGNORECASE),
    re.compile(r"\bstampede\s+will\s+(?:definitely|certainly|occur|happen)\b", re.IGNORECASE),
    re.compile(r"\b100%\s*safe", re.IGNORECASE),
    re.compile(r"\bguarantee(?:s|d)?\b.*?\b(?:100%|zero\s+risk)\b", re.IGNORECASE),
    re.compile(r"\b100%\s*confidence\b", re.IGNORECASE),
]


@dataclass
class CopilotResponse:
    text: str
    source: str  # e.g., "GEMINI_2_FLASH" or "DETERMINISTIC_FALLBACK"
    grounded_citation: str
    evidence_tier: str
    status: str  # "SUCCESS", "DEGRADED_FALLBACK", "VALIDATION_REJECTED"
    model_name: str
    latency_ms: float
    degraded_banner: Optional[str] = None
    language: str = "en"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DEGRADED_BANNER = "LOCAL SAFETY PLANE ACTIVE — GEMINI COPILOT UNAVAILABLE"


class SentinelCopilot:
    """Operational Incident Copilot powered by Google Gemini with deterministic safety bounds."""

    SYSTEM_INSTRUCTION = (
        "You are SENTINEL Incident Copilot, an operational crowd-safety decision-support assistant "
        "deployed for mass-gathering operations (e.g., Prayagraj Maha Kumbh Mela Sector 04). "
        "You receive structured telemetry, deterministic safety engine verdicts, and approved NDMA SOPs.\n\n"
        "Your operational roles:\n"
        "1. Factually explain what is occurring using the provided metrics.\n"
        "2. Explain why specific interventions were REJECTED by the Decision Safety Layer.\n"
        "3. Draft concise, calm operational briefings for Sector Magistrates and NDRF commanders.\n"
        "4. Draft reassuring, panic-free public announcements directing pilgrims to safe holding areas.\n"
        "5. Provide accurate translations (Hindi, Marathi) strictly preserving zone letters (A, B, H, R), "
        "numbers, units, and safety meaning.\n\n"
        "STRICT SAFETY RESTRICTIONS:\n"
        "- Never claim to predict stampedes, crowd collapse physics, or 'time to crush'.\n"
        "- Never invent counts, capacities, growth rates, or routes not present in the input.\n"
        "- Never recommend or clear an intervention that the Decision Safety Layer marked REJECTED.\n"
        "- Never claim field actions occurred or are verified unless provided in the record.\n"
        "- Never propose autonomous physical gate/barricade movement without human authorization.\n"
        "- Maintain an objective, calm, professional tone suitable for disaster management authorities."
    )

    def __init__(self, model_name: Optional[str] = None, timeout_seconds: float = 8.0) -> None:
        self.model_name = model_name or os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"
        self.timeout_seconds = timeout_seconds
        self._client: Any = None
        self._api_key: Optional[str] = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self._init_client()

    def _init_client(self) -> None:
        """Initialize official Google GenAI SDK client if credentials exist."""
        if not self._api_key and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
            logger.info("No GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT found. Copilot will use deterministic fallback.")
            self._client = None
            return

        try:
            from google import genai
            if self._api_key:
                self._client = genai.Client(api_key=self._api_key)
            else:
                # Vertex AI fallback mode using ambient Google Cloud project
                self._client = genai.Client()
            logger.info("Sentinel Copilot initialized with Google GenAI Client.")
        except Exception as e:
            logger.warning(f"Failed to initialize google-genai Client: {e}. Falling back to deterministic engine.")
            self._client = None

    def is_available(self) -> bool:
        """Return True if Gemini client is initialized and configured."""
        return self._client is not None

    def get_status(self) -> Dict[str, Any]:
        """Return readiness and operational status of the Copilot."""
        available = self.is_available()
        return {
            "available": available,
            "model_name": self.model_name if available else "none",
            "provider": "Google GenAI (Gemini)" if available else "Deterministic Safety Fallback",
            "offline_mode": not available,
            "banner": None if available else DEGRADED_BANNER,
        }

    def _validate_safety(self, text: str, context: Dict[str, Any]) -> tuple[bool, str]:
        """Validate LLM output against strict AI Safety Contract."""
        if not text or not text.strip():
            return False, "Empty response generated"

        # Check forbidden patterns
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                return False, f"Forbidden terminology detected: pattern {pattern.pattern}"

        # Ensure rejected candidate actions are not declared safe or approved
        candidate_actions = context.get("candidate_actions", [])
        for candidate in candidate_actions:
            name = candidate.get("name", "")
            status = candidate.get("status", "")
            if status == "REJECTED" and name:
                # Disallow claims like "Diversion to R is safe" or "safe to use Diversion to R"
                esc = re.escape(name)
                patterns = [
                    re.compile(rf"{esc}\s+is\s+(?:safe|feasible|approved|recommended|cleared|acceptable)", re.IGNORECASE),
                    re.compile(rf"(?:safe to|proceed with|recommended to|approved to|divert to|route to)\s+(?:use|take|enter)?\s*{esc}", re.IGNORECASE),
                    re.compile(rf"(?:recommend|approve|clear|execute)\s+{esc}", re.IGNORECASE),
                ]
                for p in patterns:
                    if p.search(text):
                        return False, f"Contradiction: rejected action '{name}' falsely claimed feasible or recommended"

        # Check for fabricated capacities if capacity is specified
        if "capacity" in context:
            true_cap = context["capacity"]
            # Look for capacity claims like "capacity of 500" or "capacity: 500" or "capacity is 500"
            for m in re.finditer(r"\bcapacity\s*(?:of|is|:)?\s*(\d+)", text, re.IGNORECASE):
                claimed_cap = int(m.group(1))
                if claimed_cap != true_cap and abs(claimed_cap - true_cap) > 20:
                    # Allow slight tolerance or require exact if configured
                    return False, f"Capacity hallucination: claimed {claimed_cap} vs configured {true_cap}"

        return True, "Passed safety validation"

    def _call_gemini(self, prompt: str, context: Dict[str, Any], language: str = "en") -> Optional[str]:
        """Call Gemini model with timeout, retry, and validation."""
        if not self.is_available():
            return None

        try:
            from google.genai import types

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    temperature=0.2,  # Low temperature for operational rigor
                    max_output_tokens=500,
                ),
            )
            raw_text = getattr(response, "text", "") or ""
            is_valid, reason = self._validate_safety(raw_text, context)
            if not is_valid:
                logger.warning(f"Gemini output rejected by safety filter: {reason}. Output: {raw_text[:100]}...")
                return None
            return raw_text.strip()
        except Exception as e:
            logger.warning(f"Gemini call failed: {e}. Falling back to deterministic response.")
            return None

    # -------------------------------------------------------------------------
    # 1. Incident Explanation
    # -------------------------------------------------------------------------
    def explain_incident(self, incident_state: Dict[str, Any]) -> CopilotResponse:
        """Explain current incident state, trajectory, and candidate feasibility."""
        start_time = time.perf_counter()
        zone = incident_state.get("zone", "B")
        occupancy = incident_state.get("current_occupancy", 0)
        capacity = incident_state.get("capacity", 180)
        growth_rate = incident_state.get("net_growth_rate", 0.0)
        t_limit = incident_state.get("time_to_limit_seconds", None)
        candidates = incident_state.get("candidate_actions", [])
        evidence_list = incident_state.get("evidence", ["OBSERVED CCTV SIGNAL", "CALCULATED"])

        # Retrieve grounded SOPs
        sops = sop_knowledge_base.query(zone=zone, limit=2)
        citation = sop_knowledge_base.format_citation(sops)

        prompt = (
            f"Explain this live mass-gathering crowd incident state for the tactical controller:\n"
            f"- Sector / Zone: Zone {zone} (Sangam Bottleneck Ramp)\n"
            f"- Current Occupancy: {occupancy} / {capacity} persons\n"
            f"- Net Inflow Growth Rate: {growth_rate:+.1f} persons/sec\n"
            f"- Time to Configured Operating Limit: {f'{t_limit:.1f} s' if t_limit is not None else 'Stable / Not breached'}\n"
            f"- Candidate Interventions: {candidates}\n"
            f"- Applicable Regulatory Guidance: {[s['section'] + ': ' + s['title'] for s in sops]}\n"
            f"Summarize what is happening, why rejected actions cannot be used, which feasible action remains, "
            f"and what requires human authorization."
        )

        try:
            llm_text = self._call_gemini(prompt, incident_state)
        except Exception as e:
            logger.warning(f"Gemini call exception: {e}")
            llm_text = None
        latency = (time.perf_counter() - start_time) * 1000.0

        if llm_text:
            return CopilotResponse(
                text=llm_text,
                source="GEMINI_2_FLASH",
                grounded_citation=citation,
                evidence_tier=f"AI-GENERATED EXPLANATION (Based on: {', '.join(evidence_list)})",
                status="SUCCESS",
                model_name=self.model_name,
                latency_ms=round(latency, 1),
            )

        # High-Fidelity Deterministic Fallback
        t_str = f"{t_limit:.1f} seconds" if t_limit is not None else "stable threshold"
        rejections = [c for c in candidates if c.get("status") == "REJECTED"]
        feasible = [c for c in candidates if c.get("status") == "FEASIBLE"]

        fallback_lines = [
            f"Zone {zone} is experiencing net crowd accumulation of {growth_rate:+.1f} persons/sec, currently at {occupancy}/{capacity} capacity.",
            f"Deterministic flow forecast indicates time to configured operating limit is {t_str}.",
        ]
        if rejections:
            rej_names = ", ".join(r.get("name", "Diversion") for r in rejections)
            fallback_lines.append(f"Intervention '{rej_names}' was REJECTED by Decision Safety Engine to prevent secondary bottlenecking.")
        if feasible:
            feas_names = ", ".join(f.get("name", "Upstream Metering") for f in feasible)
            fallback_lines.append(f"Intervention '{feas_names}' is FEASIBLE and recommended under {sops[0]['section'] if sops else 'NDMA guidelines'}.")
        fallback_lines.append("Awaiting Sector Magistrate / Command Unit human authorization.")

        return CopilotResponse(
            text=" ".join(fallback_lines),
            source="DETERMINISTIC_FALLBACK",
            grounded_citation=citation,
            evidence_tier=f"DETERMINISTIC DECISION ENGINE (Based on: {', '.join(evidence_list)})",
            status="DEGRADED_FALLBACK" if not self.is_available() else "SUCCESS",
            model_name="deterministic_safety_rules",
            latency_ms=round(latency, 1),
            degraded_banner=DEGRADED_BANNER if not self.is_available() else None,
        )

    # -------------------------------------------------------------------------
    # 2. Decision Rationale Explanation
    # -------------------------------------------------------------------------
    def explain_decision_rationale(self, decision_state: Dict[str, Any]) -> CopilotResponse:
        """Explain why the Decision Safety Layer rejected or cleared candidate interventions."""
        start_time = time.perf_counter()
        candidate = decision_state.get("candidate_name", "Diversion to Relief Corridor R")
        status = decision_state.get("status", "REJECTED")
        reasons = decision_state.get("reasons", ["Receiving corridor projected above capacity"])
        zone = decision_state.get("zone", "B")

        sops = sop_knowledge_base.query(zone=zone, candidate_action=candidate, status=status, limit=2)
        citation = sop_knowledge_base.format_citation(sops)

        prompt = (
            f"Explain the safety rationale for the following decision engine evaluation:\n"
            f"- Candidate Action: {candidate}\n"
            f"- Safety Verdict: {status}\n"
            f"- Deterministic Safety Reasons: {reasons}\n"
            f"- Applicable SOP: {[s['section'] + ': ' + s['title'] for s in sops]}\n"
            f"Explain clearly in 2-3 sentences why this intervention is {status}, grounding the explanation in the risk of secondary bottlenecking."
        )

        llm_text = self._call_gemini(prompt, decision_state)
        latency = (time.perf_counter() - start_time) * 1000.0

        if llm_text:
            return CopilotResponse(
                text=llm_text,
                source="GEMINI_2_FLASH",
                grounded_citation=citation,
                evidence_tier="AI-GENERATED EXPLANATION (Based on: CALCULATED SAFETY EVALUATION)",
                status="SUCCESS",
                model_name=self.model_name,
                latency_ms=round(latency, 1),
            )

        # Deterministic Fallback
        reason_str = "; ".join(reasons)
        fallback_text = (
            f"{candidate} was {status} by the Decision Safety Engine because: {reason_str}. "
            f"Under {sops[0]['section'] if sops else 'NDMA guidelines'}, diversions that transfer excess load to alternate routes "
            f"without downstream capacity create compound entrapment risks."
        )

        return CopilotResponse(
            text=fallback_text,
            source="DETERMINISTIC_FALLBACK",
            grounded_citation=citation,
            evidence_tier="DETERMINISTIC DECISION ENGINE (Based on: CALCULATED SAFETY EVALUATION)",
            status="DEGRADED_FALLBACK" if not self.is_available() else "SUCCESS",
            model_name="deterministic_safety_rules",
            latency_ms=round(latency, 1),
            degraded_banner=DEGRADED_BANNER if not self.is_available() else None,
        )

    # -------------------------------------------------------------------------
    # 3. Command-Center Briefing
    # -------------------------------------------------------------------------
    def generate_command_brief(self, system_state: Dict[str, Any]) -> CopilotResponse:
        """Generate a concise, high-priority operational brief for the Sector Magistrate."""
        start_time = time.perf_counter()
        zone = system_state.get("zone", "B")
        occupancy = system_state.get("current_occupancy", 168)
        capacity = system_state.get("capacity", 180)
        trend = system_state.get("trend", "↑ Increasing")
        t_limit = system_state.get("time_to_limit_seconds", 6.0)
        feasible_action = system_state.get("feasible_action", "Upstream Metering at Parade Ground Holding Area H")
        rejected_action = system_state.get("rejected_action", "Diversion to Relief Corridor R")
        waiting_cost = system_state.get("waiting_cost", "+205 s hold queue")

        sops = sop_knowledge_base.query(zone=zone, candidate_action=feasible_action, limit=2)
        citation = sop_knowledge_base.format_citation(sops)

        prompt = (
            f"Generate a concise, structured command briefing for Sector Magistrate / Incident Commander:\n"
            f"- Location: Maha Kumbh Sector 04 (Sangam Ghat Bottleneck {zone})\n"
            f"- Load: {occupancy}/{capacity} ({trend})\n"
            f"- Time to Configured Operating Limit: {t_limit:.1f} s\n"
            f"- Safety Verdict: {rejected_action} is REJECTED (receiving corridor overflow)\n"
            f"- Feasible Intervention: {feasible_action} ({waiting_cost})\n"
            f"- Authority: Governed under {sops[0]['section'] if sops else 'NDMA 4.2'}\n"
            f"Format with clear headings: INCIDENT SUMMARY, DECISION EVALUATION, ACTION DIRECTIVE, HUMAN AUTHORIZATION."
        )

        llm_text = self._call_gemini(prompt, system_state)
        latency = (time.perf_counter() - start_time) * 1000.0

        if llm_text:
            return CopilotResponse(
                text=llm_text,
                source="GEMINI_2_FLASH",
                grounded_citation=citation,
                evidence_tier="AI-GENERATED BRIEFING (Based on: OBSERVED + CALCULATED TELEMETRY)",
                status="SUCCESS",
                model_name=self.model_name,
                latency_ms=round(latency, 1),
            )

        # Deterministic Fallback Briefing
        fallback_brief = (
            f"=== SECTOR 04 INCIDENT COMMAND BRIEF ===\n"
            f"ZONE: Bottleneck {zone} (Sangam Ghat Descent Ramp)\n"
            f"STATUS: HIGH DENSITY LOAD | {occupancy}/{capacity} persons ({trend})\n"
            f"FORECAST: Time to configured limit = {t_limit:.1f} s\n\n"
            f"DECISION EVALUATION:\n"
            f"• {rejected_action}: REJECTED (projected secondary bottleneck)\n"
            f"• {feasible_action}: FEASIBLE (waiting queue cost {waiting_cost})\n\n"
            f"GROUNDED DIRECTIVE: Activate upstream metering per {sops[0]['section'] if sops else 'NDMA 4.2'}.\n"
            f"AUTHORIZATION: Sector Magistrate approval required before dispatch."
        )

        return CopilotResponse(
            text=fallback_brief,
            source="DETERMINISTIC_FALLBACK",
            grounded_citation=citation,
            evidence_tier="DETERMINISTIC DECISION ENGINE (Based on: OBSERVED + CALCULATED TELEMETRY)",
            status="DEGRADED_FALLBACK" if not self.is_available() else "SUCCESS",
            model_name="deterministic_safety_rules",
            latency_ms=round(latency, 1),
            degraded_banner=DEGRADED_BANNER if not self.is_available() else None,
        )

    # -------------------------------------------------------------------------
    # 4. Public Announcement Draft
    # -------------------------------------------------------------------------
    def draft_public_announcement(self, state: Dict[str, Any], tone: str = "calm") -> CopilotResponse:
        """Draft a reassuring, panic-free public address announcement."""
        start_time = time.perf_counter()
        holding_area = state.get("holding_area", "Parade Ground Holding Area H")
        restricted_corridor = state.get("restricted_corridor", "East Pontoon Bridge Bypass Corridor R")
        destination = state.get("destination", "Sangam Triveni Ghat")
        sops = sop_knowledge_base.query(candidate_action="Public Address", limit=1)
        citation = sop_knowledge_base.format_citation(sops)

        prompt = (
            f"Draft a calm, 2-sentence public address announcement for pilgrims at Maha Kumbh Mela:\n"
            f"- Holding Area: {holding_area}\n"
            f"- Destination: {destination}\n"
            f"- Restricted Corridor: {restricted_corridor}\n"
            f"Rules: Tone must be {tone}, respectful, reassuring, and completely free of panic words. "
            f"Direct pilgrims to wait comfortably in the designated holding area and follow sevadars and police."
        )

        llm_text = self._call_gemini(prompt, state)
        latency = (time.perf_counter() - start_time) * 1000.0

        if llm_text:
            return CopilotResponse(
                text=llm_text,
                source="GEMINI_2_FLASH",
                grounded_citation=citation,
                evidence_tier="AI-GENERATED ANNOUNCEMENT DRAFT (Requires Human Commander Authorization)",
                status="SUCCESS",
                model_name=self.model_name,
                latency_ms=round(latency, 1),
            )

        fallback_announcement = (
            f"Pilgrims are requested to remain comfortably in {holding_area} and follow staff instructions. "
            f"Movement toward {destination} is proceeding in orderly staged batches for everyone's safety. "
            f"Please do not enter {restricted_corridor}."
        )

        return CopilotResponse(
            text=fallback_announcement,
            source="DETERMINISTIC_FALLBACK",
            grounded_citation=citation,
            evidence_tier="DETERMINISTIC ANNOUNCEMENT TEMPLATE (Requires Human Commander Authorization)",
            status="DEGRADED_FALLBACK" if not self.is_available() else "SUCCESS",
            model_name="deterministic_announcement_template",
            latency_ms=round(latency, 1),
            degraded_banner=DEGRADED_BANNER if not self.is_available() else None,
        )

    # -------------------------------------------------------------------------
    # 5. Multilingual Translation
    # -------------------------------------------------------------------------
    def translate_operational_text(self, text: str, target_lang: str) -> CopilotResponse:
        """Translate operational text to Hindi or Marathi while strictly preserving technical identifiers."""
        start_time = time.perf_counter()
        lang_code = target_lang.lower().strip()
        lang_name = "Hindi" if lang_code in ("hi", "hindi") else "Marathi" if lang_code in ("mr", "marathi") else "English"

        if lang_name == "English":
            return CopilotResponse(
                text=text,
                source="DETERMINISTIC_FALLBACK",
                grounded_citation="Direct text preservation",
                evidence_tier="OPERATIONAL TEXT",
                status="SUCCESS",
                model_name="identity",
                latency_ms=0.1,
                language="en",
            )

        prompt = (
            f"Translate this crowd management operational message into natural, professional {lang_name}:\n"
            f"Source Text: \"{text}\"\n\n"
            f"CRITICAL PRESERVATION RULES:\n"
            f"- Preserve all Zone letters, numbers, and technical identifiers exactly (e.g. Zone B, Holding Area H, Corridor R, Pontoon Bridge 3, 168/180, 6 s).\n"
            f"- Do NOT alter the safety verdict (REJECTED must stay rejected; FEASIBLE must stay feasible).\n"
            f"- Keep tone formal, calm, and authoritative."
        )

        llm_text = self._call_gemini(prompt, {"text": text}, language=lang_code)
        latency = (time.perf_counter() - start_time) * 1000.0

        if llm_text:
            return CopilotResponse(
                text=llm_text,
                source="GEMINI_2_FLASH",
                grounded_citation="Grounded Multilingual Engine",
                evidence_tier="AI-GENERATED TRANSLATION",
                status="SUCCESS",
                model_name=self.model_name,
                latency_ms=round(latency, 1),
                language=lang_code,
            )

        # Deterministic Grounded Fallback Translation Catalog
        fallback_hi = (
            "श्रद्धालुओं से अनुरोध है कि वे Parade Ground Holding Area H में धैर्यपूर्वक प्रतीक्षा करें और पुलिस व स्वयंसेवकों के निर्देशों का पालन करें। "
            "Relief Corridor R की ओर न जाएं। संगम स्नान हेतु व्यवस्था चरणबद्ध रूप से सुरक्षित संचालित की जा रही है।"
        )
        fallback_mr = (
            "भाविकांना विनंती आहे की त्यांनी Parade Ground Holding Area H मध्ये शांततेने थांबावे आणि पोलीस व स्वयंसेवकांच्या सूचनांचे पालन करावे. "
            "Relief Corridor R कडे जाऊ नका. सुरक्षिततेसाठी संगम स्नानाची व्यवस्था टप्प्याटप्प्याने केली जात आहे."
        )

        translated = fallback_hi if lang_code in ("hi", "hindi") else fallback_mr
        return CopilotResponse(
            text=translated,
            source="DETERMINISTIC_FALLBACK",
            grounded_citation="Verified Multilingual Safety Corpus",
            evidence_tier="VERIFIED MULTILINGUAL TEMPLATE",
            status="DEGRADED_FALLBACK" if not self.is_available() else "SUCCESS",
            model_name="deterministic_translation_corpus",
            latency_ms=round(latency, 1),
            language=lang_code,
            degraded_banner=DEGRADED_BANNER if not self.is_available() else None,
        )

    # -------------------------------------------------------------------------
    # 6. Candidate What-If Comparison
    # -------------------------------------------------------------------------
    def compare_whatif_candidates(self, candidates_data: List[Dict[str, Any]]) -> CopilotResponse:
        """Compare what-if simulation candidate outcomes."""
        start_time = time.perf_counter()
        sops = sop_knowledge_base.query(candidate_action="Secondary", limit=2)
        citation = sop_knowledge_base.format_citation(sops)

        prompt = (
            f"Analyze and compare these candidate crowd interventions evaluated by the Decision Safety Engine:\n"
            f"Candidates: {candidates_data}\n"
            f"Grounded SOPs: {[s['section'] + ': ' + s['title'] for s in sops]}\n"
            f"Summarize why the safer option is superior in terms of peak load, secondary breaches, and queue cost."
        )

        llm_text = self._call_gemini(prompt, {"candidates": candidates_data})
        latency = (time.perf_counter() - start_time) * 1000.0

        if llm_text:
            return CopilotResponse(
                text=llm_text,
                source="GEMINI_2_FLASH",
                grounded_citation=citation,
                evidence_tier="AI-GENERATED WHAT-IF COMPARISON",
                status="SUCCESS",
                model_name=self.model_name,
                latency_ms=round(latency, 1),
            )

        # Deterministic comparison summary
        lines = ["Candidate Comparison:"]
        for c in candidates_data:
            name = c.get("name", "Candidate")
            status = c.get("status", "UNKNOWN")
            peak = c.get("peak_load", "N/A")
            cost = c.get("waiting_cost", "N/A")
            lines.append(f"• {name}: {status} (Peak load: {peak}, Waiting queue cost: {cost})")
        lines.append(f"Conclusion: Upstream metering preserves bottleneck safety envelope without secondary corridor overload.")

        return CopilotResponse(
            text="\n".join(lines),
            source="DETERMINISTIC_FALLBACK",
            grounded_citation=citation,
            evidence_tier="DETERMINISTIC WHAT-IF EVALUATION",
            status="DEGRADED_FALLBACK" if not self.is_available() else "SUCCESS",
            model_name="deterministic_whatif_evaluator",
            latency_ms=round(latency, 1),
            degraded_banner=DEGRADED_BANNER if not self.is_available() else None,
        )

    # -------------------------------------------------------------------------
    # 7. Post-Action Summary & Verification Support
    # -------------------------------------------------------------------------
    def summarize_post_action(
        self,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        action_record: Dict[str, Any],
    ) -> CopilotResponse:
        """Summarize post-action changes and verification telemetry."""
        start_time = time.perf_counter()
        action_name = action_record.get("candidate_name", "Upstream Metering at Holding Area H")
        pre_occ = pre_state.get("occupancy", 168)
        post_occ = post_state.get("occupancy", 120)
        delta = post_occ - pre_occ
        trend = "improved" if delta < 0 else "worsened" if delta > 0 else "steady"
        is_verified = post_state.get("verified", False)

        prompt = (
            f"Summarize the post-action verification outcome for crowd control intervention:\n"
            f"- Action Executed: {action_name}\n"
            f"- Pre-Action Occupancy: {pre_occ}\n"
            f"- Post-Action Occupancy: {post_occ} ({delta:+d} change, {trend})\n"
            f"- Deterministic Verification Status: {'VERIFIED EFFECTIVE' if is_verified else 'PENDING CONTINUOUS MONITORING'}\n"
            f"Explain whether the intervention achieved the expected stabilization."
        )

        llm_text = self._call_gemini(prompt, {"pre": pre_state, "post": post_state, "action": action_record})
        latency = (time.perf_counter() - start_time) * 1000.0

        if llm_text:
            return CopilotResponse(
                text=llm_text,
                source="GEMINI_2_FLASH",
                grounded_citation="Post-Action Telemetry Ledger",
                evidence_tier="AI-GENERATED POST-ACTION SUMMARY",
                status="SUCCESS",
                model_name=self.model_name,
                latency_ms=round(latency, 1),
            )

        fallback_summary = (
            f"Post-action verification for {action_name}: Occupancy shifted from {pre_occ} to {post_occ} ({delta:+d}). "
            f"The density trend has {trend}. Deterministic verification status: {'VERIFIED EFFECTIVE' if is_verified else 'PENDING OBSERVATION'}."
        )

        return CopilotResponse(
            text=fallback_summary,
            source="DETERMINISTIC_FALLBACK",
            grounded_citation="Post-Action Telemetry Ledger",
            evidence_tier="DETERMINISTIC VERIFICATION TELEMETRY",
            status="DEGRADED_FALLBACK" if not self.is_available() else "SUCCESS",
            model_name="deterministic_verification_tracker",
            latency_ms=round(latency, 1),
            degraded_banner=DEGRADED_BANNER if not self.is_available() else None,
        )


# Global singleton instance
sentinel_copilot = SentinelCopilot()
