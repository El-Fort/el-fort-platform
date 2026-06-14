import hmac
import hashlib
import time

def verify_signature(secret: bytes, timestamp: str, signature: str, body: bytes, window: int = 300) -> bool:
    try:
        if abs(time.time() - int(timestamp)) > window:
            return False
        expected = hmac.new(secret, timestamp.encode() + b'.' + body, hashlib.sha256).hexdigest()
        provided = signature.replace('v1=', '')
        return hmac.compare_digest(expected, provided)
    except Exception:
        return False
