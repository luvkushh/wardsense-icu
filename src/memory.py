"""Hindsight Memory Engine Interface for SiteSense RFI Agent.
Manages persistent agent memory using the official hindsight-client SDK with
temporal knowledge graphs, directives, and fallback simulation for offline evaluation.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.config import (
    HINDSIGHT_API_KEY,
    HINDSIGHT_BASE_URL,
    HINDSIGHT_BANK_ID,
    USE_LIVE_HINDSIGHT
)
from src.models import RFIDocument

logger = logging.getLogger("sitesense.memory")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class LocalHindsightMemorySimulator:
    """High-fidelity local in-memory fallback mimicking Vectorize Hindsight's

    temporal, entity, and directive memory features when live credentials are not set.
    """
    def __init__(self, bank_id: str):
        self.bank_id = bank_id
        self.memories: List[Dict[str, Any]] = []
        self.directives: List[Dict[str, Any]] = []
        logger.info(f"Initialized Local Hindsight Memory Simulator for bank: {bank_id}")

    def retain(self, content: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        mem_id = f"mem_{len(self.memories) + 1}_{datetime.now().strftime('%H%M%S')}"
        item = {
            "id": mem_id,
            "bank_id": self.bank_id,
            "text": content,
            "metadata": metadata or {},
            "tags": tags or [],
            "timestamp": datetime.now().isoformat()
        }
        self.memories.append(item)
        logger.info(f"[HINDSIGHT LOCAL] Retained memory {mem_id} with tags: {tags}")
        return {"status": "success", "id": mem_id, "bank_id": self.bank_id}

    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Simulate semantic + keyword recall across retained memories."""
        query_words = set(query.lower().replace(",", " ").replace("-", " ").replace("?", " ").split())
        scored_memories = []

        for mem in self.memories:
            text = mem["text"].lower()
            tags = " ".join(mem.get("tags", [])).lower()
            combined = f"{text} {tags}"
            
            score = 0
            for w in query_words:
                if len(w) > 2 and w in combined:
                    score += 1
                    # Give bonus weight for structural grid / level matches
                    if w.startswith("grid") or w.startswith("level") or w in ["b4", "b-4", "c2", "c-2", "e3", "e-3"]:
                        score += 3
                    if w in ["drill", "coring", "penetration", "busway", "tension", "fire"]:
                        score += 2

            if score > 0:
                scored_memories.append((score, mem))

        # Sort by score descending
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, mem in scored_memories[:limit]:
            results.append({
                "id": mem["id"],
                "text": mem["text"],
                "score": float(score),
                "tags": mem.get("tags", []),
                "metadata": mem.get("metadata", {})
            })
        logger.info(f"[HINDSIGHT LOCAL] Recalled {len(results)} memories for query: '{query}'")
        return results

    def create_directive(self, name: str, content: str, priority: int = 0):
        directive = {
            "id": f"dir_{len(self.directives)+1}",
            "name": name,
            "content": content,
            "priority": priority
        }
        self.directives.append(directive)
        logger.info(f"[HINDSIGHT LOCAL] Created Directive: {name} (Priority {priority})")
        return directive


class HindsightMemoryManager:
    """Manages agent memory by delegating to official Vectorize Hindsight

    or the high-fidelity simulator.
    """
    def __init__(self, bank_id: Optional[str] = None):
        self.bank_id = bank_id or HINDSIGHT_BANK_ID
        self.use_live = USE_LIVE_HINDSIGHT
        self.client = None
        self.local_sim = LocalHindsightMemorySimulator(self.bank_id)

        if self.use_live:
            try:
                from hindsight_client import Hindsight
                self.client = Hindsight(
                    base_url=HINDSIGHT_BASE_URL,
                    api_key=HINDSIGHT_API_KEY
                )
                logger.info(f"Connected to Vectorize Hindsight Cloud: {HINDSIGHT_BASE_URL} (Bank: {self.bank_id})")
                self._ensure_bank_exists()
            except Exception as e:
                logger.warning(f"Could not connect to live Hindsight service: {e}. Falling back to high-fidelity local simulator.")
                self.use_live = False

    def _ensure_bank_exists(self):
        """Ensure the Hindsight bank is provisioned with proper agent mission."""
        if not self.use_live or not self.client:
            return
        try:
            self.client.create_bank(
                bank_id=self.bank_id,
                name="Omega Tower Construction RFI Memory",
                mission="Prevent costly construction rework and safety hazards by recalling past RFIs, structural changes, and MEP alterations.",
                background="Commercial skyscraper project under fast-track design-build construction."
            )
            logger.info(f"Verified/created Hindsight bank: {self.bank_id}")
        except Exception as e:
            # Bank might already exist or permission granted
            logger.debug(f"Bank creation response: {e}")

    def retain_rfi(self, rfi: RFIDocument) -> Dict[str, Any]:
        """Store an RFI into Hindsight memory bank."""
        content = rfi.to_hindsight_content()
        metadata = {
            "rfi_id": rfi.id,
            "title": rfi.title,
            "level": rfi.level,
            "grid": rfi.grid_location,
            "discipline": rfi.discipline.value,
            "hazard_level": rfi.hazard_level.value,
            "cost_risk": str(rfi.rework_cost_risk)
        }
        tags = rfi.tags + [rfi.id.lower(), rfi.level.lower().replace(" ", "-"), rfi.grid_location.lower().replace(" ", "-")]

        # Always update local simulator for instant inspection
        self.local_sim.retain(content=content, metadata=metadata, tags=tags)

        if self.use_live and self.client:
            try:
                logger.info(f"Calling client.retain() on Hindsight Cloud for {rfi.id}...")
                resp = self.client.retain(
                    bank_id=self.bank_id,
                    content=content,
                    metadata={k: str(v) for k, v in metadata.items()},
                    tags=tags,
                    document_id=rfi.id
                )
                return {"status": "retained_cloud", "id": getattr(resp, "id", rfi.id), "rfi_id": rfi.id}
            except Exception as e:
                logger.error(f"Error during Hindsight cloud retain: {e}")
                return {"status": "retained_local_fallback", "rfi_id": rfi.id, "error": str(e)}

        return {"status": "retained_local", "rfi_id": rfi.id}

    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recall relevant past memories from Hindsight."""
        if self.use_live and self.client:
            try:
                logger.info(f"Calling client.recall() on Hindsight Cloud with query: '{query}'")
                resp = self.client.recall(
                    bank_id=self.bank_id,
                    query=query,
                    max_tokens=2048
                )
                results = []
                memories_list = getattr(resp, "results", []) or []
                for item in memories_list:
                    results.append({
                        "id": getattr(item, "id", "cloud_mem"),
                        "text": getattr(item, "text", str(item)),
                        "score": getattr(item, "score", 0.95),
                        "tags": getattr(item, "tags", []),
                        "metadata": getattr(item, "metadata", {})
                    })
                if results:
                    return results
            except Exception as e:
                logger.error(f"Error recalling from Hindsight cloud: {e}. Falling back to local simulator.")

        return self.local_sim.recall(query=query, limit=limit)

    def reflect(self, query: str) -> Optional[str]:
        """Synthesize high-level reasoning across stored memories using Hindsight reflect."""
        if self.use_live and self.client:
            try:
                logger.info(f"Calling client.reflect() on Hindsight Cloud...")
                resp = self.client.reflect(
                    bank_id=self.bank_id,
                    query=query,
                    budget="low"
                )
                return getattr(resp, "text", str(resp))
            except Exception as e:
                logger.error(f"Error during reflect: {e}")
        return None

    def list_all_memories(self) -> List[Dict[str, Any]]:
        """List currently retained memories for dashboard visualizer."""
        return self.local_sim.memories
