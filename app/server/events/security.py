"""
Security and Webhook HMAC Verification Utilities
"""
import hmac
import hashlib
from typing import Optional


def verify_hmac_signature(
    payload_bytes: bytes,
    secret: str,
    signature_header: Optional[str],
    algorithm: str = "sha256"
) -> bool:
    """
    Verifies an HMAC signature against payload bytes.
    Accepts signature headers formatted as 'sha256=hash' or raw hex string.
    """
    if not secret:
        # If no secret is configured, bypass signature check
        return True
    if not signature_header:
        return False

    clean_sig = signature_header.strip()
    if "=" in clean_sig:
        prefix, clean_sig = clean_sig.split("=", 1)
        if prefix.lower() in ("sha256", "sha1"):
            algorithm = prefix.lower()

    if algorithm == "sha256":
        hasher = hashlib.sha256
    elif algorithm == "sha1":
        hasher = hashlib.sha1
    else:
        hasher = hashlib.sha256

    expected_sig = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hasher
    ).hexdigest()

    return hmac.compare_digest(expected_sig.lower(), clean_sig.lower())
