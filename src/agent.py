"""Zero-Rework RFI Intelligence Agent.
Combines Vectorize Hindsight Agent Memory with Groq LLM reasoning and
construction engineering domain logic to prevent catastrophic job-site errors.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from src.models import (
    RFIDocument,
    WorkerQueryRequest,
    WorkerQueryResponse,
    HazardLevel,
    ComparisonItem
)
from src.memory import HindsightMemoryManager
from src.dataset import INITIAL_RFIS, BENCHMARK_SCENARIOS
from src.config import GROQ_API_KEY, DEFAULT_MODEL, USE_LIVE_GROQ

logger = logging.getLogger("sitesense.agent")


class SiteSenseRFIAgent:
    """Intelligent Construction Site Safety & RFI Agent powered by Hindsight Memory and Groq."""

    def __init__(self, memory_manager: Optional[HindsightMemoryManager] = None):
        self.memory = memory_manager or HindsightMemoryManager()
        self.rfis: Dict[str, RFIDocument] = {}
        self.initialize_knowledge_base()

    def initialize_knowledge_base(self):
        """Pre-populate the Hindsight memory bank with project RFIs."""
        logger.info(f"Retaining {len(INITIAL_RFIS)} initial RFIs into Hindsight Memory...")
        for rfi in INITIAL_RFIS:
            self.rfis[rfi.id] = rfi
            self.memory.retain_rfi(rfi)

    def add_rfi(self, rfi: RFIDocument) -> Dict[str, Any]:
        """Dynamically ingest a new field RFI and retain in Hindsight."""
        self.rfis[rfi.id] = rfi
        resp = self.memory.retain_rfi(rfi)
        logger.info(f"New RFI [{rfi.id}] retained in memory: {rfi.title}")
        return resp

    def get_all_rfis(self) -> List[RFIDocument]:
        return list(self.rfis.values())

    def _normalize(self, text: str) -> str:
        return text.lower().replace("-", "").replace(" ", "").replace("_", "")

    def _synthesize_with_groq(
        self,
        query: WorkerQueryRequest,
        matched_rfis: List[RFIDocument],
        base_resp: WorkerQueryResponse
    ) -> WorkerQueryResponse:
        """Use Groq LLM (llama-3.3-70b-versatile / qwen3-32b / gpt-oss-120b) to synthesize

        rigorous engineering advice based on memories recalled from Hindsight.
        """
        if not USE_LIVE_GROQ or not matched_rfis:
            return base_resp

        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)

            system_prompt = (
                "You are the Senior Safety & Structural Engineer on Omega Tower. "
                "Evaluate the field worker query against historical RFIs recalled from Hindsight agent memory. "
                "Respond in valid JSON format with keys: "
                "'verdict' (short authoritative uppercase verdict with emoji), "
                "'hazard_details' (clear engineering explanation of the clash, tendon or busway depth, and risks), "
                "'recommended_alternative' (exact pre-approved safe sleeve or modified procedure), "
                "'rework_cost_prevented' (number)."
            )

            rfi_context = "\n\n".join([
                f"[{r.id}] {r.title} (Approved: {r.date_issued})\n"
                f"Discipline: {r.discipline.value} | Location: {r.level}, {r.grid_location}\n"
                f"Approved Resolution: {r.approved_resolution}\n"
                f"Hazard Rating: {r.hazard_level.value}\n"
                f"Directives: {'; '.join(r.critical_directives)}\n"
                f"Rework Risk: ${r.rework_cost_risk}"
                for r in matched_rfis
            ])

            user_msg = (
                f"FIELD WORKER QUESTION: \"{query.question}\"\n"
                f"LOCATION: {query.level or 'Not specified'}, {query.grid_location or 'Not specified'}\n\n"
                f"RECALLED HINDSIGHT MEMORIES:\n{rfi_context}"
            )

            completion = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            res_json = json.loads(completion.choices[0].message.content)
            base_resp.verdict = res_json.get("verdict", base_resp.verdict)
            base_resp.hazard_details = res_json.get("hazard_details", base_resp.hazard_details)
            base_resp.recommended_alternative = res_json.get("recommended_alternative", base_resp.recommended_alternative)
            if "rework_cost_prevented" in res_json:
                base_resp.rework_cost_prevented = float(res_json["rework_cost_prevented"])

            logger.info("Successfully synthesized safety verdict using Groq LLM.")
            return base_resp

        except Exception as e:
            logger.warning(f"Groq LLM reasoning bypassed (using deterministic engine): {e}")
            return base_resp

    def evaluate_worker_query(self, query: WorkerQueryRequest) -> WorkerQueryResponse:
        """Process field worker question, query Hindsight, and evaluate hazard risk."""
        full_query_text = f"{query.question} {query.level or ''} {query.grid_location or ''} {query.action_type or ''}"
        
        # 1. Recall relevant memories from Hindsight
        memories = self.memory.recall(query=full_query_text, limit=4)
        
        # Extract location hints if provided
        q_grid = self._normalize(query.grid_location) if query.grid_location else ""
        q_level = self._normalize(query.level) if query.level else ""
        
        # Find which RFIs were matched and geographically relevant
        matched_rfis: List[RFIDocument] = []
        for mem in memories:
            rfi_id_meta = mem.get("metadata", {}).get("rfi_id")
            candidate_rfis = []
            if rfi_id_meta and rfi_id_meta in self.rfis:
                candidate_rfis.append(self.rfis[rfi_id_meta])
            else:
                for rfi_id, rfi_obj in self.rfis.items():
                    if rfi_id.lower() in mem.get("text", "").lower():
                        candidate_rfis.append(rfi_obj)

            for cand in candidate_rfis:
                cand_grid = self._normalize(cand.grid_location)
                cand_level = self._normalize(cand.level)
                
                # If specific location requested, ensure location matches
                location_match = True
                if q_grid and cand_grid != q_grid:
                    location_match = False
                if q_level and cand_level != q_level:
                    # Allow vertical shear/structural dependencies across floor if specifically tagged
                    if not ("seismic" in cand.tags or "structural" in cand.tags and cand_grid == q_grid):
                        location_match = False

                if location_match and cand not in matched_rfis:
                    matched_rfis.append(cand)

        # Fallback direct grid check
        if not matched_rfis and q_grid:
            for rfi_obj in self.rfis.values():
                if self._normalize(rfi_obj.grid_location) == q_grid:
                    if not q_level or self._normalize(rfi_obj.level) == q_level:
                        matched_rfis.append(rfi_obj)

        # 2. If no modifications clash with this location, report safe to proceed
        if not matched_rfis:
            return WorkerQueryResponse(
                status=HazardLevel.SAFE_PROCEED,
                verdict="PROCEED WITH STANDARD SPECIFICATIONS",
                summary_message="No conflicting architectural modifications or safety directives found in Hindsight memory for this location.",
                hazard_details="Base drawing specifications apply. Standard inspection and safety PPE required.",
                recalled_rfis=[],
                critical_directives=["Follow standard project specifications and wear required PPE."],
                recommended_alternative="Proceed at planned location following base drawing specifications.",
                rework_cost_prevented=0.0,
                hindsight_memory_hits=len(memories),
                stateless_contrast="Both stateless and memory agents allow work here, as no modifications exist."
            )

        # 3. Assess highest severity
        has_critical = any(r.hazard_level == HazardLevel.CRITICAL_STOP_WORK for r in matched_rfis)
        has_caution = any(r.hazard_level == HazardLevel.CAUTION_VERIFY for r in matched_rfis)

        status = HazardLevel.CRITICAL_STOP_WORK if has_critical else (
            HazardLevel.CAUTION_VERIFY if has_caution else HazardLevel.SAFE_PROCEED
        )

        all_directives: List[str] = []
        total_risk_prevented = 0.0
        rfi_summaries = []

        for rfi in matched_rfis:
            all_directives.extend(rfi.critical_directives)
            total_risk_prevented += rfi.rework_cost_risk
            rfi_summaries.append({
                "id": rfi.id,
                "title": rfi.title,
                "date": rfi.date_issued,
                "discipline": rfi.discipline.value,
                "grid": rfi.grid_location,
                "level": rfi.level,
                "resolution": rfi.approved_resolution,
                "hazard_level": rfi.hazard_level.value,
                "risk_cost": rfi.rework_cost_risk
            })

        primary_rfi = matched_rfis[0]
        if "post-tension" in primary_rfi.tags or "b4" in self._normalize(primary_rfi.grid_location):
            alternative = (
                "DO NOT DRILL AT GRID B-4. Divert all conduit/pipe penetrations to designated "
                "MEP Chase sleeve at Grid B-6 (authorized per RFI-108)."
            )
            verdict = "🚨 CRITICAL STRUCTURAL HAZARD: STOP WORK IMMEDIATELY"
            hazard_details = (
                f"Severing risk: Post-tension tendons under 33,000 lbs force embedded at 110mm depth "
                f"per {primary_rfi.id}. Coring here could trigger slab failure and severe personnel injury."
            )
        elif "electrical" in primary_rfi.tags or "c2" in self._normalize(primary_rfi.grid_location):
            alternative = (
                "Limit all drywall fasteners to 25mm depth maximum. If drilling deeper than 25mm is required, "
                "schedule an electrical shutdown with Site Operations."
            )
            verdict = "⚡ ARC FLASH HAZARD: HIGH VOLTAGE BUSWAY IN CAVITY"
            hazard_details = (
                f"Energized 480V/800A bus duct rerouted horizontally behind drywall at +2800mm AFF per {primary_rfi.id}. "
                f"Long anchors risk phase-to-ground flashover."
            )
        elif "fire-safety" in primary_rfi.tags or "e3" in self._normalize(primary_rfi.grid_location):
            alternative = (
                "Install UL System W-L-1054 intumescent firestop collars for any sleeve. "
                "Record sleeve serial in the Firestop Submittal Log."
            )
            verdict = "🔥 FIRE CODE WARNING: 2-HOUR RATED BARRIER"
            hazard_details = (
                f"Partition upgraded to 2-hour fire wall per {primary_rfi.id}. Unsealed penetrations "
                f"will fail occupancy inspection and prevent building handover."
            )
        else:
            alternative = primary_rfi.approved_resolution
            verdict = f"FIELD DIRECTIVE ACTIVE: {primary_rfi.id}"
            hazard_details = f"Field revision recorded on {primary_rfi.date_issued} by {primary_rfi.discipline.value}."

        stateless_contrast = (
            f"A stateless AI reading initial drawings would approve this work because the original blueprint Rev-0 "
            f"did not show the modification. Hindsight recalled {primary_rfi.id} from memory, preventing "
            f"an estimated ${total_risk_prevented:,.2f} rework catastrophe."
        )

        base_resp = WorkerQueryResponse(
            status=status,
            verdict=verdict,
            summary_message=(
                f"Hindsight retrieved {len(matched_rfis)} relevant RFI records for {primary_rfi.level}, {primary_rfi.grid_location}. "
                f"Directives apply."
            ),
            hazard_details=hazard_details,
            recalled_rfis=rfi_summaries,
            critical_directives=all_directives[:4],
            recommended_alternative=alternative,
            rework_cost_prevented=total_risk_prevented,
            hindsight_memory_hits=len(memories),
            stateless_contrast=stateless_contrast
        )

        # Synthesize with Groq LLM if configured
        return self._synthesize_with_groq(query, matched_rfis, base_resp)

    def get_benchmarks(self) -> List[ComparisonItem]:
        return BENCHMARK_SCENARIOS
