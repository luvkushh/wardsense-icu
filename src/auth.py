"""Authentication, Password Hashing, and JWT Session Management for WardSense ICU."""
import base64
import hashlib
import hmac
import json
import time
from typing import Any
from src.config import settings


def hash_password(password: str, salt: str = "wardsense_clinical_salt_2026") -> str:
    """Hash password using PBKDF2-HMAC-SHA256."""
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return dk.hex()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify plaintext password against stored PBKDF2 hash."""
    expected = hash_password(password)
    return hmac.compare_digest(expected, password_hash)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_jwt_token(payload: dict[str, Any], expires_in_seconds: int = 86400) -> str:
    """Generate a signed HS256 JWT token without external C-extension dependencies."""
    header = {"alg": "HS256", "typ": "JWT"}
    body = dict(payload)
    body["iat"] = int(time.time())
    body["exp"] = int(time.time()) + expires_in_seconds

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    body_b64 = _b64url_encode(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{body_b64}".encode("ascii")

    signature = hmac.new(
        settings.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    sig_b64 = _b64url_encode(signature)
    return f"{header_b64}.{body_b64}.{sig_b64}"


def decode_jwt_token(token: str) -> dict[str, Any] | None:
    """Verify and decode an HS256 JWT token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, body_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{body_b64}".encode("ascii")
        expected_sig = hmac.new(
            settings.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_b64url_encode(expected_sig), sig_b64):
            return None
        payload = json.loads(_b64url_decode(body_b64).decode("utf-8"))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
