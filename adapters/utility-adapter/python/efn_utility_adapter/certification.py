"""
EFN Utility Adapter self-certification client.

Run this against your running adapter server to verify EFN compliance
before submitting for EFN certification.

Usage:
    from efn_utility_adapter.certification import EFNCertificationClient

    client = EFNCertificationClient(
        base_url="http://localhost:8000",
        secret=b"your_efn_secret"
    )
    client.run_all()

Or run from command line:
    EFN_BASE_URL=http://localhost:8000 EFN_SECRET=your_secret python -m efn_utility_adapter.certification
"""

import hashlib
import hmac
import json
import time
import sys
from dataclasses import dataclass
from typing import Optional

try:
    import requests
except ImportError:
    raise ImportError("Install requests: pip install requests")


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str


class EFNCertificationClient:
    """
    Self-certification suite for EFN Utility Provider Adapters.

    Tests all three endpoints for:
    - Correct response structure
    - Proper HMAC authentication enforcement
    - Replay attack protection
    - Correct HTTP status codes
    """

    VALIDATE_ENDPOINT = "/efn/v1/utility/validate"
    DISPENSE_ENDPOINT = "/efn/v1/utility/dispense"
    STATUS_ENDPOINT = "/efn/v1/utility/transaction/{ref}/status"

    TEST_METER = "12345678901"
    TEST_EFN_REF = f"EFN-CERT-{int(time.time())}"

    def __init__(self, base_url: str, secret: bytes, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.secret = secret
        self.timeout = timeout
        self.results: list[TestResult] = []

    def _sign(self, body: bytes) -> dict:
        """Generate EFN-compliant HMAC authentication headers."""
        ts = str(int(time.time()))
        sig = "v1=" + hmac.new(self.secret, ts.encode() + b"." + body, hashlib.sha256).hexdigest()
        return {
            "X-EFN-Timestamp": ts,
            "X-EFN-Signature": sig,
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: dict, sign: bool = True) -> requests.Response:
        body = json.dumps(payload).encode()
        headers = self._sign(body) if sign else {"Content-Type": "application/json"}
        return requests.post(f"{self.base_url}{path}", data=body, headers=headers, timeout=self.timeout)

    def _get(self, path: str, sign: bool = True) -> requests.Response:
        body = b""
        headers = self._sign(body) if sign else {}
        return requests.get(f"{self.base_url}{path}", headers=headers, timeout=self.timeout)

    def _record(self, name: str, passed: bool, message: str):
        result = TestResult(name=name, passed=passed, message=message)
        self.results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}: {message}")

    # ─── Test Cases ───────────────────────────────────────────────────────────

    def test_validate_valid_customer(self):
        """Valid customer should return is_valid=true."""
        resp = self._post(self.VALIDATE_ENDPOINT, {
            "customer_ref": self.TEST_METER,
            "utility_category": "ELECTRICITY"
        })
        try:
            data = resp.json()
            passed = resp.status_code == 200 and data.get("is_valid") is True
            self._record("validate: valid customer", passed,
                         f"status={resp.status_code} is_valid={data.get('is_valid')}")
        except Exception as e:
            self._record("validate: valid customer", False, str(e))

    def test_validate_invalid_customer(self):
        """Invalid customer should return is_valid=false (not a server error)."""
        resp = self._post(self.VALIDATE_ENDPOINT, {
            "customer_ref": "INVALID_METER_XXXX",
            "utility_category": "ELECTRICITY"
        })
        try:
            data = resp.json()
            passed = resp.status_code == 200 and data.get("is_valid") is False
            self._record("validate: invalid customer", passed,
                         f"status={resp.status_code} is_valid={data.get('is_valid')}")
        except Exception as e:
            self._record("validate: invalid customer", False, str(e))

    def test_dispense_valid(self):
        """Valid dispense request should return a value_token."""
        resp = self._post(self.DISPENSE_ENDPOINT, {
            "customer_ref": self.TEST_METER,
            "amount": 5000.0,
            "currency": "NGN",
            "efn_reference": self.TEST_EFN_REF
        })
        try:
            data = resp.json()
            passed = (resp.status_code == 200
                      and data.get("status") == "success"
                      and bool(data.get("value_token")))
            self._record("dispense: valid payment", passed,
                         f"status={resp.status_code} token={'present' if data.get('value_token') else 'MISSING'}")
        except Exception as e:
            self._record("dispense: valid payment", False, str(e))

    def test_dispense_idempotency(self):
        """Duplicate efn_reference should return same token, not an error."""
        payload = {
            "customer_ref": self.TEST_METER,
            "amount": 5000.0,
            "currency": "NGN",
            "efn_reference": self.TEST_EFN_REF  # same reference as above
        }
        resp1 = self._post(self.DISPENSE_ENDPOINT, payload)
        resp2 = self._post(self.DISPENSE_ENDPOINT, payload)
        try:
            d1, d2 = resp1.json(), resp2.json()
            passed = (resp1.status_code == 200 and resp2.status_code == 200
                      and d1.get("value_token") == d2.get("value_token"))
            self._record("dispense: idempotency", passed,
                         f"tokens match: {d1.get('value_token') == d2.get('value_token')}")
        except Exception as e:
            self._record("dispense: idempotency", False, str(e))

    def test_transaction_status(self):
        """Transaction status should return status and value_token."""
        path = self.STATUS_ENDPOINT.replace("{ref}", self.TEST_EFN_REF)
        resp = self._get(path)
        try:
            data = resp.json()
            passed = resp.status_code == 200 and bool(data.get("status"))
            self._record("status: query transaction", passed,
                         f"status={resp.status_code} tx_status={data.get('status')}")
        except Exception as e:
            self._record("status: query transaction", False, str(e))

    def test_missing_signature(self):
        """Requests without HMAC headers must return 401."""
        resp = self._post(self.VALIDATE_ENDPOINT, {
            "customer_ref": self.TEST_METER,
            "utility_category": "ELECTRICITY"
        }, sign=False)
        passed = resp.status_code == 401
        self._record("security: missing signature → 401", passed,
                     f"got status={resp.status_code} (expected 401)")

    def test_invalid_signature(self):
        """Requests with wrong HMAC must return 401."""
        body = json.dumps({"customer_ref": self.TEST_METER, "utility_category": "ELECTRICITY"}).encode()
        headers = {
            "X-EFN-Timestamp": str(int(time.time())),
            "X-EFN-Signature": "v1=deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "Content-Type": "application/json",
        }
        resp = requests.post(f"{self.base_url}{self.VALIDATE_ENDPOINT}",
                             data=body, headers=headers, timeout=self.timeout)
        passed = resp.status_code == 401
        self._record("security: invalid signature → 401", passed,
                     f"got status={resp.status_code} (expected 401)")

    def test_replay_attack(self):
        """Requests with timestamp older than 5 minutes must return 401."""
        body = json.dumps({"customer_ref": self.TEST_METER, "utility_category": "ELECTRICITY"}).encode()
        old_ts = str(int(time.time()) - 600)  # 10 minutes ago
        sig = "v1=" + hmac.new(self.secret, old_ts.encode() + b"." + body, hashlib.sha256).hexdigest()
        headers = {
            "X-EFN-Timestamp": old_ts,
            "X-EFN-Signature": sig,
            "Content-Type": "application/json",
        }
        resp = requests.post(f"{self.base_url}{self.VALIDATE_ENDPOINT}",
                             data=body, headers=headers, timeout=self.timeout)
        passed = resp.status_code == 401
        self._record("security: replay attack → 401", passed,
                     f"got status={resp.status_code} (expected 401)")

    # ─── Run All ──────────────────────────────────────────────────────────────

    def run_all(self) -> bool:
        """
        Run all certification tests and print a summary.
        Returns True if all tests pass.
        """
        print(f"\n{'═'*60}")
        print("  EFN Utility Adapter Certification Suite")
        print(f"  Target: {self.base_url}")
        print(f"{'═'*60}\n")

        print("Endpoint Tests:")
        self.test_validate_valid_customer()
        self.test_validate_invalid_customer()
        self.test_dispense_valid()
        self.test_dispense_idempotency()
        self.test_transaction_status()

        print("\nSecurity Tests:")
        self.test_missing_signature()
        self.test_invalid_signature()
        self.test_replay_attack()

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        all_pass = passed == total

        print(f"\n{'═'*60}")
        print(f"  Result: {passed}/{total} tests passed")
        if all_pass:
            print("  🎉 CERTIFIED — Ready to submit to EFN")
        else:
            print("  ⚠️  FAILED — Fix issues before submitting")
        print(f"{'═'*60}\n")

        return all_pass


if __name__ == "__main__":
    import os
    base_url = os.environ.get("EFN_BASE_URL", "http://localhost:8000")
    secret = os.environ.get("EFN_SECRET", "").encode()
    if not secret:
        print("Error: Set EFN_SECRET environment variable")
        sys.exit(1)
    client = EFNCertificationClient(base_url=base_url, secret=secret)
    ok = client.run_all()
    sys.exit(0 if ok else 1)
