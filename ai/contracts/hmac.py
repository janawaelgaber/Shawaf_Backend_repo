"""SCRUM-28. Path is the path only. The body hash is the hex sha256 of the raw bytes."""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path


def body_sha256_hex(raw_body: bytes) -> str:
    return hashlib.sha256(raw_body).hexdigest()


def string_to_sign(timestamp: str, method: str, path: str, raw_body: bytes) -> str:
    return "\n".join([timestamp, method, path, body_sha256_hex(raw_body)])


def sign(secret: str, timestamp: str, method: str, path: str, raw_body: bytes) -> str:
    payload = string_to_sign(timestamp, method, path, raw_body).encode()
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def vector_path() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "hmac_test_vector.json"
