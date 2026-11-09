"""Groq LLM Engine with Function-Calling Error Recovery (openai/gpt-oss-120b & qwen/qwen3-32b)."""
import json
import re
import time
from typing import Any
import httpx
from src.config import settings


CLINICAL_VERDICT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "emit_clinical_order_verdict",
            "description": "Evaluate a proposed ICU medication order against recalled Hindsight shift memories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "verdict": {
                        "type": "string",
                        "description": "Clinical safety verdict, e.g. BLOCKED — SEVERE CONTRAINDICATION or APPROVED — SAFE PROTOCOL",
                    },
                    "clinical_why": {
                        "type": "string",
                        "description": "Explanation citing the exact past shift observation recalled from Hindsight memory",
                    },
                    "safe_alternative": {
                        "type": "string",
                        "description": "Recommended safe alternative medication protocol for the incoming shift",
                    },
                },
                "required": ["verdict", "clinical_why", "safe_alternative"],
            },
        },
    }
]


class GroqClinicalLLM:
    """
    Fast LLM Reasoning Engine powered by Groq Cloud.
    Supports recommended models:
      - `openai/gpt-oss-120b`
      - `qwen/qwen3-32b`
      - `llama-3.3-70b-versatile`
    Includes multi-stage Function-Calling (`tools`) Error Recovery & JSON repair middleware.
    """

    GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

    def _extract_json_safely(self, text: str) -> dict[str, Any] | None:
        """Repair and extract JSON object from model output or malformed function call."""
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            pass
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return None

    def generate_clinical_decision(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback_response: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute Groq LLM inference with function-calling (`tools`), automatic model fallback
        (`openai/gpt-oss-120b` -> `qwen/qwen3-32b` -> deterministic clinical reasoning),
        and `tool_use_failed` JSON repair recovery.
        """
        if not settings.groq_api_key:
            out = dict(fallback_response)
            out["llm_provider"] = "Deterministic Clinical Reasoning (Add GROQ_API_KEY for live Groq inference)"
            out["model_used"] = settings.default_model
            out["function_call_recovered"] = False
            return out

        models_to_try = [
            settings.default_model,
            settings.fallback_model,
            "llama-3.3-70b-versatile",
        ]
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        }

        for model_name in models_to_try:
            t0 = time.perf_counter()
            try:
                payload: dict[str, Any] = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "tools": CLINICAL_VERDICT_TOOLS,
                    "tool_choice": "auto",
                    "temperature": 0.1,
                    "max_tokens": 700,
                }
                with httpx.Client(timeout=12.0) as client:
                    resp = client.post(self.GROQ_CHAT_URL, headers=headers, json=payload)

                # Stage 1 Function-Calling Error Recovery: recover from tool_use_failed or schema error
                recovered_flag = False
                if resp.status_code == 400 and ("tool_use_failed" in resp.text or "failed_generation" in resp.text):
                    recovered_flag = True
                    try:
                        err_json = resp.json().get("error", {})
                        failed_gen = err_json.get("failed_generation", "")
                        repaired = self._extract_json_safely(failed_gen)
                        if repaired and "verdict" in repaired:
                            merged = dict(fallback_response)
                            merged.update(repaired)
                            merged["llm_provider"] = "Groq Cloud LPU (Recovered Tool Call)"
                            merged["model_used"] = model_name
                            merged["llm_latency_ms"] = round((time.perf_counter() - t0) * 1000.0, 1)
                            merged["function_call_recovered"] = True
                            return merged
                    except Exception:
                        pass

                    # Retry without strict tool schema using JSON mode
                    payload.pop("tools", None)
                    payload.pop("tool_choice", None)
                    payload["response_format"] = {"type": "json_object"}
                    with httpx.Client(timeout=12.0) as client:
                        resp = client.post(self.GROQ_CHAT_URL, headers=headers, json=payload)

                if resp.status_code == 200:
                    data = resp.json()
                    msg = data["choices"][0]["message"]
                    parsed = None
                    if msg.get("tool_calls"):
                        args_str = msg["tool_calls"][0].get("function", {}).get("arguments", "")
                        parsed = self._extract_json_safely(args_str)
                    if not parsed and msg.get("content"):
                        parsed = self._extract_json_safely(msg["content"])
                    if parsed:
                        merged = dict(fallback_response)
                        merged.update(parsed)
                        merged["llm_provider"] = "Groq Cloud LPU"
                        merged["model_used"] = model_name
                        merged["llm_latency_ms"] = round((time.perf_counter() - t0) * 1000.0, 1)
                        merged["function_call_recovered"] = recovered_flag
                        return merged
            except Exception:
                continue

        out = dict(fallback_response)
        out["llm_provider"] = "Clinical Fallback (Groq Retry Guard Active)"
        out["model_used"] = settings.default_model
        out["function_call_recovered"] = True
        return out


llm_engine = GroqClinicalLLM()
