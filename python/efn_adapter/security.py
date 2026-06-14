import base64
import hashlib
import hmac
import time


REPLAY_WINDOW = 300  # seconds


def verify_signature(api_secret: str, timestamp: str, raw_body: bytes, signature: str) -> bool:
    """Verify EFN gateway signature and timestamp freshness."""
    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        return False

    if abs(time.time() - ts) > REPLAY_WINDOW:
        return False

    message = timestamp.encode() + b"." + raw_body
    expected = "v1=" + base64.b64encode(
        hmac.new(api_secret.encode(), message, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)
