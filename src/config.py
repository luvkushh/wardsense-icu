"""Configuration and live runtime settings for WardSense ICU."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "wardsense.db"


class RuntimeConfig:
    """Mutable runtime configuration supporting live UI updates for Hindsight Cloud & Groq."""

    def __init__(self) -> None:
        self.hindsight_api_key: str = os.getenv("HINDSIGHT_API_KEY", "").strip()
        self.hindsight_base_url: str = os.getenv(
            "HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io"
        ).strip()
        self.hindsight_bank_id: str = os.getenv(
            "HINDSIGHT_BANK_ID", "wardsense_icu_clinical_bank"
        ).strip()
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
        self.default_model: str = os.getenv("DEFAULT_MODEL", "openai/gpt-oss-120b").strip()
        self.fallback_model: str = os.getenv("FALLBACK_MODEL", "qwen/qwen3-32b").strip()
        self.jwt_secret: str = os.getenv(
            "JWT_SECRET", "wardsense-clinical-continuity-secret-key-2026"
        )
        self.port: int = int(os.getenv("PORT", "8000"))
        self.host: str = os.getenv("HOST", "0.0.0.0")

    def update_credentials(
        self,
        hindsight_api_key: str | None = None,
        hindsight_base_url: str | None = None,
        hindsight_bank_id: str | None = None,
        groq_api_key: str | None = None,
        default_model: str | None = None,
    ) -> None:
        if hindsight_api_key is not None:
            self.hindsight_api_key = hindsight_api_key.strip()
        if hindsight_base_url is not None and hindsight_base_url.strip():
            self.hindsight_base_url = hindsight_base_url.strip()
        if hindsight_bank_id is not None and hindsight_bank_id.strip():
            self.hindsight_bank_id = hindsight_bank_id.strip()
        if groq_api_key is not None:
            self.groq_api_key = groq_api_key.strip()
        if default_model is not None and default_model.strip():
            self.default_model = default_model.strip()
        self._persist_to_env()

    def _persist_to_env(self) -> None:
        env_content = (
            "# Hindsight Cloud Configuration\n"
            f"HINDSIGHT_API_KEY={self.hindsight_api_key}\n"
            f"HINDSIGHT_BASE_URL={self.hindsight_base_url}\n"
            f"HINDSIGHT_BANK_ID={self.hindsight_bank_id}\n\n"
            "# Groq Fast LLM Configuration\n"
            f"GROQ_API_KEY={self.groq_api_key}\n"
            f"DEFAULT_MODEL={self.default_model}\n"
            f"FALLBACK_MODEL={self.fallback_model}\n\n"
            "# Security & Server Configuration\n"
            f"JWT_SECRET={self.jwt_secret}\n"
            f"PORT={self.port}\n"
            f"HOST={self.host}\n"
        )
        try:
            ENV_PATH.write_text(env_content, encoding="utf-8")
        except Exception:
            pass


settings = RuntimeConfig()
