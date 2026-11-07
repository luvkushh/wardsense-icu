"""Configuration management for SiteSense RFI Agent."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Hindsight Settings
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "").strip()
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io").strip()
HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "omega_tower_construction_rfis").strip()

# LLM Providers (Groq or OpenAI)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile").strip()

# Server Settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Check whether live Hindsight credentials are provided
USE_LIVE_HINDSIGHT = bool(HINDSIGHT_API_KEY and HINDSIGHT_API_KEY != "your-api-key")
