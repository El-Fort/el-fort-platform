import time, json, hmac, hashlib
from efn_utility_adapter.security import verify_signature

def test_signature():
    secret = b"test_secret"
    ts = str(int(time.time()))
    body = json.dumps({"customer_ref": "123"}).encode()
    sig = "v1=" + hmac.new(secret, ts.encode() + b'.' + body, hashlib.sha256).hexdigest()
    assert verify_signature(secret, ts, sig, body) is True
    assert verify_signature(secret, ts, "v1=bad", body) is False
