"""Full integration test suite for the EFN Utility Adapter (Python/FastAPI)."""
import hashlib
import hmac
import json
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from efn_utility_adapter import EFNUtilityAdapter
from efn_utility_adapter.models import (
    DispenseRequest,
    DispenseResponse,
    TransactionStatusResponse,
    ValidateRequest,
    ValidateResponse,
)
from efn_utility_adapter.fastapi_router import make_router

SECRET = b"test_secret_key_for_ci"
TEST_METER = "12345678901"
TEST_REF = "EFN-TEST-REF-001"

# ─── Mock Adapter ────────────────────────────────────────────────────────────

class MockAdapter(EFNUtilityAdapter):
    def validate_customer(self, req: ValidateRequest) -> ValidateResponse:
        if req.customer_ref == TEST_METER:
            return ValidateResponse(
                is_valid=True,
                customer_name="Test User",
                customer_address="1 Test Street",
                minimum_amount=500.0,
                outstanding_balance=0.0,
            )
        return ValidateResponse(is_valid=False)

    def dispense_value(self, req: DispenseRequest) -> DispenseResponse:
        return DispenseResponse(
            status="success",
            dispense_ref=f"UTL-{req.efn_reference[:8]}",
            value_token="1234-5678-9012-3456-7890",
            receipt_details={"units": "62.50 kWh"},
        )

    def transaction_status(self, efn_reference: str) -> TransactionStatusResponse:
        return TransactionStatusResponse(
            status="success", value_token="1234-5678-9012-3456-7890"
        )


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(make_router(MockAdapter(), SECRET))
    return TestClient(app)


def _sign(body: bytes) -> dict:
    ts = str(int(time.time()))
    sig = "v1=" + hmac.new(SECRET, ts.encode() + b"." + body, hashlib.sha256).hexdigest()
    return {"X-EFN-Timestamp": ts, "X-EFN-Signature": sig, "Content-Type": "application/json"}


# ─── Validate Tests ──────────────────────────────────────────────────────────

class TestValidate:
    def test_valid_customer_returns_200(self, client):
        payload = json.dumps({"customer_ref": TEST_METER, "utility_category": "ELECTRICITY"}).encode()
        resp = client.post("/efn/v1/utility/validate", content=payload, headers=_sign(payload))
        assert resp.status_code == 200
        assert resp.json()["is_valid"] is True
        assert resp.json()["customer_name"] == "Test User"

    def test_invalid_customer_returns_is_valid_false(self, client):
        payload = json.dumps({"customer_ref": "UNKNOWN", "utility_category": "WATER"}).encode()
        resp = client.post("/efn/v1/utility/validate", content=payload, headers=_sign(payload))
        assert resp.status_code == 200
        assert resp.json()["is_valid"] is False

    def test_missing_signature_returns_401(self, client):
        payload = json.dumps({"customer_ref": TEST_METER, "utility_category": "ELECTRICITY"}).encode()
        resp = client.post("/efn/v1/utility/validate", content=payload,
                           headers={"Content-Type": "application/json"})
        assert resp.status_code == 401

    def test_invalid_signature_returns_401(self, client):
        payload = json.dumps({"customer_ref": TEST_METER, "utility_category": "ELECTRICITY"}).encode()
        headers = {
            "X-EFN-Timestamp": str(int(time.time())),
            "X-EFN-Signature": "v1=deadbeef" * 8,
            "Content-Type": "application/json",
        }
        resp = client.post("/efn/v1/utility/validate", content=payload, headers=headers)
        assert resp.status_code == 401

    def test_expired_timestamp_returns_401(self, client):
        payload = json.dumps({"customer_ref": TEST_METER, "utility_category": "ELECTRICITY"}).encode()
        old_ts = str(int(time.time()) - 600)  # 10 min ago
        sig = "v1=" + hmac.new(SECRET, old_ts.encode() + b"." + payload, hashlib.sha256).hexdigest()
        headers = {"X-EFN-Timestamp": old_ts, "X-EFN-Signature": sig, "Content-Type": "application/json"}
        resp = client.post("/efn/v1/utility/validate", content=payload, headers=headers)
        assert resp.status_code == 401


# ─── Dispense Tests ──────────────────────────────────────────────────────────

class TestDispense:
    def test_valid_dispense_returns_token(self, client):
        payload = json.dumps({
            "customer_ref": TEST_METER,
            "amount": 5000.0,
            "currency": "NGN",
            "efn_reference": TEST_REF,
        }).encode()
        resp = client.post("/efn/v1/utility/dispense", content=payload, headers=_sign(payload))
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["value_token"]
        assert data["dispense_ref"]

    def test_dispense_requires_auth(self, client):
        payload = json.dumps({
            "customer_ref": TEST_METER, "amount": 1000.0,
            "currency": "NGN", "efn_reference": TEST_REF,
        }).encode()
        resp = client.post("/efn/v1/utility/dispense", content=payload,
                           headers={"Content-Type": "application/json"})
        assert resp.status_code == 401


# ─── Status Tests ─────────────────────────────────────────────────────────────

class TestStatus:
    def test_status_returns_transaction(self, client):
        headers = _sign(b"")
        resp = client.get(f"/efn/v1/utility/transaction/{TEST_REF}/status", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["value_token"]
