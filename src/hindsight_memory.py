"""Vectorize Hindsight Cloud SDK Integration & Hybrid Clinical Memory Engine."""
from concurrent.futures import ThreadPoolExecutor
import json
import time
import uuid
from datetime import datetime
from typing import Any

from src.config import settings
from src.database import (
    get_connection,
    get_patient_memories,
    record_telemetry,
)

try:
    from hindsight_client import Hindsight
    HINDSIGHT_SDK_AVAILABLE = True
except ImportError:
    Hindsight = None  # type: ignore
    HINDSIGHT_SDK_AVAILABLE = False

_CLOUD_EXECUTOR = ThreadPoolExecutor(max_workers=4)


class WardSenseMemoryEngine:
    """
    Production wrapper around Vectorize Hindsight Cloud (`hindsight-client`).
    Executes real `client.retain()` and `client.recall()` operations against
    `https://api.hindsight.vectorize.io` when `HINDSIGHT_API_KEY` is configured,
    while maintaining a synchronized local clinical SQLite mirror for zero-downtime
    ICU reliability.
    """

    def __init__(self) -> None:
        self._client: Any = None
        self._last_key: str = ""
        self._last_url: str = ""

    def _get_cloud_client(self) -> Any:
        """Initialize or return the official Hindsight Cloud SDK client."""
        if not HINDSIGHT_SDK_AVAILABLE or not settings.hindsight_api_key:
            return None
        if (
            self._client is None
            or self._last_key != settings.hindsight_api_key
            or self._last_url != settings.hindsight_base_url
        ):
            try:
                self._client = Hindsight(
                    base_url=settings.hindsight_base_url,
                    api_key=settings.hindsight_api_key,
                )
                self._last_key = settings.hindsight_api_key
                self._last_url = settings.hindsight_base_url
            except Exception:
                self._client = None
        return self._client

    def get_status(self) -> dict[str, Any]:
        """Return live Hindsight Cloud connectivity and memory bank telemetry."""
        cloud_ready = bool(HINDSIGHT_SDK_AVAILABLE and settings.hindsight_api_key)
        all_memories = get_patient_memories()
        synced_count = sum(1 for m in all_memories if m.get("cloud_synced"))
        return {
            "sdk_installed": HINDSIGHT_SDK_AVAILABLE,
            "cloud_configured": cloud_ready,
            "mode": "HINDSIGHT_CLOUD_ACTIVE" if cloud_ready else "HYBRID_LOCAL_MIRROR",
            "base_url": settings.hindsight_base_url,
            "bank_id": settings.hindsight_bank_id,
            "total_memories": len(all_memories),
            "cloud_synced_memories": synced_count,
            "promo_code_hint": "MEMHACK99 ($50 free credits at https://ui.hindsight.vectorize.io)",
        }

    def retain_shift_observation(
        self,
        patient_id: str,
        shift_number: int,
        author_name: str,
        author_role: str,
        category: str,
        severity: str,
        content: str,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Retain a clinical shift observation into Vectorize Hindsight Cloud (`client.retain`)
        and persist in the local clinical audit table.
        """
        t0 = time.perf_counter()
        memory_id = f"MEM-{patient_id.split('-')[-1]}-S{shift_number:02d}-{uuid.uuid4().hex[:4].upper()}"
        shift_label = f"Shift #{shift_number} ({datetime.now().strftime('%H:%M IST')} Live Note)"
        tags_list = tags or [patient_id, category, severity, f"Shift-{shift_number}"]
        created_at = datetime.now().isoformat()

        cloud_synced = 0
        cloud_response_meta: dict[str, Any] = {}
        mode = "LOCAL_MIRROR"

        client = self._get_cloud_client()
        structured_content = (
            f"[{patient_id} | {shift_label} | {category} | Severity: {severity} | By: {author_name}] "
            f"{content}"
        )
        context_str = f"ICU Shift Handoff Memory • Patient {patient_id} • Category: {category}"

        if client is not None:
            try:
                resp = _CLOUD_EXECUTOR.submit(
                    client.retain,
                    bank_id=settings.hindsight_bank_id,
                    content=structured_content,
                    context=context_str,
                ).result(timeout=12.0)
                cloud_synced = 1
                mode = "HINDSIGHT_CLOUD"
                cloud_response_meta = {"cloud_status": "retained", "response": str(resp)[:200]}
            except Exception as exc:
                mode = "HINDSIGHT_CLOUD_FALLBACK"
                cloud_response_meta = {"cloud_error_handled": str(exc)[:160]}

        conn = get_connection()
        conn.execute(
            """
            INSERT INTO memories (
                memory_id, patient_id, shift_number, shift_label,
                author_name, author_role, category, severity,
                content, tags_json, cloud_synced, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                patient_id,
                shift_number,
                shift_label,
                author_name,
                author_role,
                category,
                severity,
                content,
                json.dumps(tags_list),
                cloud_synced,
                created_at,
            ),
        )
        # Also auto-create a follow-up shift task if CRITICAL or WARNING
        if severity in ("CRITICAL", "WARNING"):
            task_id = f"TSK-{uuid.uuid4().hex[:4].upper()}"
            conn.execute(
                """
                INSERT INTO shift_tasks (
                    task_id, patient_id, shift_origin, title, priority, status, clinical_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    patient_id,
                    f"Shift #{shift_number} ({author_name})",
                    f"[{category}] Verify follow-up: {content[:85]}...",
                    "CRITICAL" if severity == "CRITICAL" else "HIGH",
                    "PENDING",
                    f"Retained in Hindsight Bank ({memory_id}) during Shift #{shift_number}.",
                ),
            )
        conn.commit()
        conn.close()

        latency_ms = (time.perf_counter() - t0) * 1000.0
        payload_log = {
            "sdk_call": "client.retain()",
            "bank_id": settings.hindsight_bank_id,
            "memory_id": memory_id,
            "patient_id": patient_id,
            "shift_number": shift_number,
            "severity": severity,
            "content": structured_content,
            "context": context_str,
            **cloud_response_meta,
        }
        record_telemetry(
            operation="client.retain",
            bank_id=settings.hindsight_bank_id,
            patient_id=patient_id,
            mode=mode,
            latency_ms=latency_ms,
            summary=f"Retained {severity} {category} note for {patient_id} ({shift_label})",
            payload=payload_log,
        )

        return {
            "memory_id": memory_id,
            "patient_id": patient_id,
            "shift_number": shift_number,
            "shift_label": shift_label,
            "author_name": author_name,
            "category": category,
            "severity": severity,
            "content": content,
            "tags": tags_list,
            "mode": mode,
            "latency_ms": round(latency_ms, 2),
            "bank_id": settings.hindsight_bank_id,
        }

    def recall_patient_context(
        self,
        patient_id: str,
        query: str,
        max_shift: int | None = None,
    ) -> dict[str, Any]:
        """
        Execute `client.recall()` against Vectorize Hindsight Cloud and enrich with
        temporal shift provenance for clinical safety verification.
        """
        t0 = time.perf_counter()
        client = self._get_cloud_client()
        mode = "LOCAL_MIRROR"
        cloud_results: list[str] = []
        cloud_meta: dict[str, Any] = {}

        if client is not None:
            try:
                resp = _CLOUD_EXECUTOR.submit(
                    client.recall,
                    bank_id=settings.hindsight_bank_id,
                    query=f"Patient {patient_id}: {query}",
                ).result(timeout=12.0)
                mode = "HINDSIGHT_CLOUD"
                if hasattr(resp, "results") and resp.results:
                    cloud_results = [ getattr(r, "text", str(r)) for r in resp.results ]
                else:
                    cloud_results = [str(resp)[:300]]
                cloud_meta = {"cloud_recall_hits": len(cloud_results)}
            except Exception as exc:
                mode = "HINDSIGHT_CLOUD_FALLBACK"
                cloud_meta = {"cloud_error_handled": str(exc)[:160]}

        memories = get_patient_memories(patient_id=patient_id, max_shift=max_shift)

        # Rank memories by relevance to query terms + severity
        query_words = [
            w.lower()
            for w in query.replace("(", " ").replace(")", " ").split()
            if len(w) >= 3
        ]
        scored_memories = []
        for m in memories:
            haystack = (
                f"{m['content']} {m['category']} {' '.join(m['tags'])}"
            ).lower()
            keyword_hits = sum(1 for w in query_words if w in haystack)
            severity_boost = 3 if m["severity"] == "CRITICAL" else (2 if m["severity"] == "WARNING" else 1)
            score = keyword_hits * 2 + severity_boost
            m_copy = dict(m)
            m_copy["relevance_score"] = score
            scored_memories.append(m_copy)

        scored_memories.sort(
            key=lambda x: (x["relevance_score"], x["shift_number"]), reverse=True
        )

        latency_ms = (time.perf_counter() - t0) * 1000.0
        payload_log = {
            "sdk_call": "client.recall()",
            "bank_id": settings.hindsight_bank_id,
            "patient_id": patient_id,
            "query": query,
            "max_shift_filter": max_shift,
            "recalled_count": len(scored_memories),
            "top_memory_id": scored_memories[0]["memory_id"] if scored_memories else None,
            **cloud_meta,
        }
        record_telemetry(
            operation="client.recall",
            bank_id=settings.hindsight_bank_id,
            patient_id=patient_id,
            mode=mode,
            latency_ms=latency_ms,
            summary=f"Recalled {len(scored_memories)} temporal shift memories for {patient_id}",
            payload=payload_log,
        )

        return {
            "patient_id": patient_id,
            "query": query,
            "mode": mode,
            "bank_id": settings.hindsight_bank_id,
            "latency_ms": round(latency_ms, 2),
            "memories": scored_memories,
            "cloud_results": cloud_results,
        }

    def sync_all_to_hindsight_cloud(self) -> dict[str, Any]:
        """Push all unsynced local ICU shift memories directly to Hindsight Cloud."""
        client = self._get_cloud_client()
        if client is None:
            return {
                "success": False,
                "synced": 0,
                "message": "Hindsight Cloud API Key not configured yet. Add HINDSIGHT_API_KEY (Promo code: MEMHACK99 at ui.hindsight.vectorize.io).",
            }

        memories = get_patient_memories()
        synced_now = 0
        errors: list[str] = []
        conn = get_connection()

        for m in memories:
            if m.get("cloud_synced"):
                continue
            t0 = time.perf_counter()
            structured = (
                f"[{m['patient_id']} | {m['shift_label']} | {m['category']} | "
                f"Severity: {m['severity']} | By: {m['author_name']}] {m['content']}"
            )
            try:
                _CLOUD_EXECUTOR.submit(
                    client.retain,
                    bank_id=settings.hindsight_bank_id,
                    content=structured,
                    context=f"ICU Clinical Handoff Memory • {m['patient_id']}",
                ).result(timeout=12.0)
                conn.execute(
                    "UPDATE memories SET cloud_synced = 1 WHERE memory_id = ?",
                    (m["memory_id"],),
                )
                synced_now += 1
                latency_ms = (time.perf_counter() - t0) * 1000.0
                record_telemetry(
                    operation="client.retain (cloud-sync)",
                    bank_id=settings.hindsight_bank_id,
                    patient_id=m["patient_id"],
                    mode="HINDSIGHT_CLOUD",
                    latency_ms=latency_ms,
                    summary=f"Cloud-synced memory {m['memory_id']} to {settings.hindsight_bank_id}",
                    payload={"memory_id": m["memory_id"], "bank_id": settings.hindsight_bank_id},
                )
            except Exception as exc:
                errors.append(f"{m['memory_id']}: {str(exc)[:100]}")

        conn.commit()
        conn.close()
        return {
            "success": len(errors) == 0,
            "synced": synced_now,
            "bank_id": settings.hindsight_bank_id,
            "errors": errors,
            "message": f"Successfully synced {synced_now} ICU shift memories to Hindsight Cloud ({settings.hindsight_bank_id}).",
        }


memory_engine = WardSenseMemoryEngine()
