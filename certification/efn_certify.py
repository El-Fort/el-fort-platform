#!/usr/bin/env python3
"""EFN partner-bank adapter conformance runner.

Stdlib-only by design so partner banks can run it in restricted environments.
"""
from __future__ import annotations

import argparse
import base64
import dataclasses
import datetime as dt
import hashlib
import hmac
import json
import sys
from decimal import Decimal
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable


@dataclasses.dataclass
class Config:
    suite: str = "local-ngn-v1"
    base_url: str = ""
    api_key: str = ""
    api_secret: str = ""
    source_account: str = "0123456789"
    source_account_name: str = "EFN Source Customer"
    destination_account: str = "9876543210"
    destination_account_name: str = "EFN Destination Customer"
    source_bank_code: str = "SRC"
    destination_bank_code: str = "DST"
    amount: str = "2500.00"
    currency: str = "NGN"
    timeout_seconds: int = 15


@dataclasses.dataclass
class Result:
    name: str
    passed: bool
    detail: str = ""


def canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sign(secret: str, timestamp: str, body: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), timestamp.encode("utf-8") + b"." + body, hashlib.sha256)
    return "v1=" + base64.b64encode(mac.digest()).decode("ascii")


def load_config(path: str | None, args: argparse.Namespace) -> Config:
    data: dict[str, Any] = {}
    if path:
        data = json.loads(Path(path).read_text())
    for field in dataclasses.fields(Config):
        value = getattr(args, field.name, None)
        if value is not None:
            data[field.name] = value
    return Config(**{k: v for k, v in data.items() if k in {f.name for f in dataclasses.fields(Config)}})


class Client:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.base_url = cfg.base_url.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None,
        idem_key: str | None,
        *,
        timestamp: str | None = None,
        secret: str | None = None,
        expect_status: tuple[int, ...] = (200,),
    ) -> tuple[int, dict[str, Any], str]:
        if not self.base_url:
            raise RuntimeError("--base-url is required unless using --self-test")
        body = canonical_json(payload or {}) if payload is not None else b""
        ts = timestamp or str(int(time.time()))
        signature = sign(secret if secret is not None else self.cfg.api_secret, ts, body)
        url = self.base_url + path
        headers = {
            "X-EFN-API-Key": self.cfg.api_key,
            "X-EFN-Timestamp": ts,
            "X-EFN-Signature": signature,
            "Content-Type": "application/json",
        }
        if idem_key:
            headers["Idempotency-Key"] = idem_key
        req = urllib.request.Request(url, data=body if payload is not None else None, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.cfg.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
                status = resp.status
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            status = exc.code
        if status not in expect_status:
            raise AssertionError(f"expected HTTP {expect_status}, got {status}: {raw[:300]}")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {}
        return status, parsed, raw


def efn_ref(suffix: str) -> str:
    return "EFNCERT" + dt.datetime.utcnow().strftime("%Y%m%d%H%M%S") + suffix


def authorization_payload(cfg: Config, ref: str) -> dict[str, Any]:
    return {
        "efn_reference": ref,
        "authorization_id": "",
        "uan": "000001123456789012",
        "source_account_number": cfg.source_account,
        "source_account_name": cfg.source_account_name,
        "source_bank_code": cfg.source_bank_code,
        "recipient_account_number": cfg.destination_account,
        "recipient_bank_code": cfg.destination_bank_code,
        "recipient_name": cfg.destination_account_name,
        "destination_rail": "efn_uan",
        "amount": cfg.amount,
        "currency": cfg.currency,
        "description": "EFN certification authorization",
        "auth_method": "fingerprint",
        "biometric_verified": True,
        "location_verified": True,
        "terminal_id": "EFN-CERT-TERM-001",
        "nonce": ref + "-nonce",
        "purpose": "certification",
        "requested_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }


def credit_payload(cfg: Config, ref: str) -> dict[str, Any]:
    return {
        "efn_reference": ref,
        "source_uan": "000001123456789012",
        "source_account_number": cfg.source_account,
        "source_account_name": cfg.source_account_name,
        "source_bank_code": cfg.source_bank_code,
        "destination_uan": "000002123456789019",
        "destination_account_number": cfg.destination_account,
        "destination_account_name": cfg.destination_account_name,
        "destination_bank_code": cfg.destination_bank_code,
        "amount": cfg.amount,
        "currency": cfg.currency,
        "description": "EFN certification credit",
        "auth_method": "fingerprint",
        "terminal_id": "EFN-CERT-TERM-001",
        "nonce": ref + "-credit-nonce",
        "purpose": "certification",
        "requested_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }


def assert_success_status(body: dict[str, Any], allowed: set[str]) -> None:
    if body.get("success") is not True:
        raise AssertionError(f"success=true required, got {body}")
    if body.get("status") not in allowed:
        raise AssertionError(f"status in {sorted(allowed)} required, got {body}")


def run_case(name: str, fn: Callable[[], None]) -> Result:
    try:
        fn()
        return Result(name, True)
    except Exception as exc:  # noqa: BLE001 - CLI should report all failures compactly.
        return Result(name, False, str(exc))


def run_self_test() -> list[Result]:
    vector_path = Path(__file__).with_name("test_vectors.json")
    vector = json.loads(vector_path.read_text())

    def check_vector() -> None:
        got = sign(vector["api_secret"], vector["timestamp"], vector["raw_body"].encode("utf-8"))
        if got != vector["expected_signature"]:
            raise AssertionError(f"signature mismatch: expected {vector['expected_signature']}, got {got}")

    def check_canonical_body() -> None:
        got = canonical_json(vector["body"]).decode("utf-8")
        if got != vector["raw_body"]:
            raise AssertionError(f"canonical JSON mismatch: {got}")

    return [
        run_case("self-test: canonical JSON", check_canonical_body),
        run_case("self-test: HMAC vector", check_vector),
    ]


def run_remote_suite(cfg: Config) -> list[Result]:
    client = Client(cfg)
    ref = efn_ref("001")
    auth_payload = authorization_payload(cfg, ref)
    auth_id_holder = {"authorization_id": ""}
    balance_holder = {
        "source_before": None,
        "source_after_capture": None,
        "dest_before": None,
        "dest_after_credit": None,
    }

    def resolve_account() -> None:
        payload = {
            "efn_reference": ref,
            "uan": auth_payload["uan"],
            "account_number": cfg.source_account,
            "bank_code": cfg.source_bank_code,
        }
        _, body, _ = client.request("POST", "/efn/v1/accounts/resolve", payload, ref + ":resolve")
        if body.get("success") is not True or body.get("status") != "active":
            raise AssertionError(f"active account resolve required, got {body}")

    def balance_inquiry() -> None:
        payload = {"efn_reference": ref, "account_number": cfg.source_account, "currency": cfg.currency}
        _, body, _ = client.request("POST", "/efn/v1/accounts/balance", payload, ref + ":balance-source-before")
        if body.get("success") is not True or body.get("currency") != cfg.currency:
            raise AssertionError(f"valid source balance response required, got {body}")
        balance_holder["source_before"] = Decimal(str(body.get("ledger_balance") or body.get("available_balance")))

    def destination_balance_before() -> None:
        payload = {"efn_reference": ref, "account_number": cfg.destination_account, "currency": cfg.currency}
        _, body, _ = client.request("POST", "/efn/v1/accounts/balance", payload, ref + ":balance-dest-before")
        if body.get("success") is not True or body.get("currency") != cfg.currency:
            raise AssertionError(f"valid destination balance response required, got {body}")
        balance_holder["dest_before"] = Decimal(str(body.get("ledger_balance") or body.get("available_balance")))

    def source_balance_after_capture() -> None:
        payload = {"efn_reference": ref, "account_number": cfg.source_account, "currency": cfg.currency}
        _, body, _ = client.request("POST", "/efn/v1/accounts/balance", payload, ref + ":balance-source-after-capture")
        if body.get("success") is not True:
            raise AssertionError(f"valid source post-capture balance response required, got {body}")
        balance_holder["source_after_capture"] = Decimal(str(body.get("ledger_balance") or body.get("available_balance")))
        expected = balance_holder["source_before"] - Decimal(cfg.amount)
        if balance_holder["source_after_capture"] != expected:
            raise AssertionError(f"source ledger was not debited by {cfg.amount}: expected {expected}, got {balance_holder['source_after_capture']}")

    def destination_balance_after_credit() -> None:
        payload = {"efn_reference": ref, "account_number": cfg.destination_account, "currency": cfg.currency}
        _, body, _ = client.request("POST", "/efn/v1/accounts/balance", payload, ref + ":balance-dest-after-credit")
        if body.get("success") is not True:
            raise AssertionError(f"valid destination post-credit balance response required, got {body}")
        balance_holder["dest_after_credit"] = Decimal(str(body.get("ledger_balance") or body.get("available_balance")))
        expected = balance_holder["dest_before"] + Decimal(cfg.amount)
        if balance_holder["dest_after_credit"] != expected:
            raise AssertionError(f"destination ledger was not credited by {cfg.amount}: expected {expected}, got {balance_holder['dest_after_credit']}")

    def bad_signature_rejected() -> None:
        client.request("POST", "/efn/v1/accounts/balance", {"efn_reference": ref, "account_number": cfg.source_account, "currency": cfg.currency}, ref + ":bad-signature", secret="bad_secret", expect_status=(401, 403))

    def stale_timestamp_rejected() -> None:
        stale = str(int(time.time()) - 86400)
        client.request("POST", "/efn/v1/accounts/balance", {"efn_reference": ref, "account_number": cfg.source_account, "currency": cfg.currency}, ref + ":stale", timestamp=stale, expect_status=(401, 403))

    def authorize() -> None:
        _, body, _ = client.request("POST", "/efn/v1/authorizations", auth_payload, ref + ":authorizations")
        assert_success_status(body, {"authorized"})
        auth_id = body.get("authorization_id")
        if not auth_id:
            raise AssertionError(f"authorization_id required, got {body}")
        auth_id_holder["authorization_id"] = auth_id

    def authorization_idempotent_replay() -> None:
        _, body, _ = client.request("POST", "/efn/v1/authorizations", auth_payload, ref + ":authorizations")
        assert_success_status(body, {"authorized"})
        if body.get("authorization_id") != auth_id_holder["authorization_id"]:
            raise AssertionError("idempotent authorization replay returned different authorization_id")

    def idempotency_conflict_rejected() -> None:
        changed = dict(auth_payload)
        changed["amount"] = "2501.00"
        client.request("POST", "/efn/v1/authorizations", changed, ref + ":authorizations", expect_status=(409, 422))

    def capture() -> None:
        path = "/efn/v1/authorizations/" + urllib.parse.quote(auth_id_holder["authorization_id"]) + "/capture"
        capture_payload = dict(auth_payload)
        capture_payload["authorization_id"] = auth_id_holder["authorization_id"]
        _, body, _ = client.request("POST", path, capture_payload, ref + ":capture")
        assert_success_status(body, {"completed"})

    def credit() -> None:
        _, body, _ = client.request("POST", "/efn/v1/credits", credit_payload(cfg, ref), ref + ":credits")
        assert_success_status(body, {"credited", "completed"})

    def transaction_status() -> None:
        path = "/efn/v1/transactions/" + urllib.parse.quote(ref)
        _, body, _ = client.request("GET", path, None, None)
        if body.get("success") is not True or body.get("efn_reference") != ref:
            raise AssertionError(f"transaction status for {ref} required, got {body}")

    def reversal() -> None:
        reversal_ref = efn_ref("002")
        reversal_auth = authorization_payload(cfg, reversal_ref)
        _, auth_body, _ = client.request("POST", "/efn/v1/authorizations", reversal_auth, reversal_ref + ":authorizations")
        assert_success_status(auth_body, {"authorized"})
        auth_id = auth_body["authorization_id"]
        path = "/efn/v1/authorizations/" + urllib.parse.quote(auth_id) + "/reversal"
        reversal_auth["authorization_id"] = auth_id
        _, body, _ = client.request("POST", path, reversal_auth, reversal_ref + ":reversal")
        assert_success_status(body, {"reversed"})

    def reconciliation_report() -> None:
        payload = {
            "report_id": ref + "-REPORT",
            "settlement_date": dt.date.today().isoformat(),
            "transactions": [{"efn_reference": ref, "bank_reference": "CERT-BANK-REF", "amount": cfg.amount, "currency": cfg.currency, "status": "completed"}],
        }
        _, body, _ = client.request("POST", "/efn/v1/reconciliation/report", payload, ref + ":reconciliation")
        if body.get("success") is not True:
            raise AssertionError(f"reconciliation success required, got {body}")

    cases = [
        ("remote: bad signature rejected", bad_signature_rejected),
        ("remote: stale timestamp rejected", stale_timestamp_rejected),
        ("remote: account resolve", resolve_account),
        ("remote: source balance before debit", balance_inquiry),
        ("remote: destination balance before credit", destination_balance_before),
        ("remote: authorization", authorize),
        ("remote: authorization idempotent replay", authorization_idempotent_replay),
        ("remote: idempotency conflict rejected", idempotency_conflict_rejected),
        ("remote: capture/debit", capture),
        ("remote: source ledger debited after capture", source_balance_after_capture),
        ("remote: destination credit", credit),
        ("remote: destination ledger credited after credit", destination_balance_after_credit),
        ("remote: transaction status", transaction_status),
        ("remote: reversal", reversal),
        ("remote: reconciliation report", reconciliation_report),
    ]
    return [run_case(name, fn) for name, fn in cases]


def print_results(results: list[Result]) -> int:
    failed = 0
    for result in results:
        marker = "PASS" if result.passed else "FAIL"
        print(f"[{marker}] {result.name}")
        if not result.passed:
            failed += 1
            print(f"       {result.detail}")
    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="EFN partner-bank adapter certification runner")
    parser.add_argument("--self-test", action="store_true", help="Validate local HMAC vectors only")
    parser.add_argument("--config", help="Path to JSON config")
    for field in dataclasses.fields(Config):
        arg = "--" + field.name.replace("_", "-")
        parser.add_argument(arg, type=type(field.default) if field.default is not None else str)
    args = parser.parse_args()

    results = run_self_test()
    if not args.self_test:
        cfg = load_config(args.config, args)
        results.extend(run_remote_suite(cfg))
    return print_results(results)


if __name__ == "__main__":
    sys.exit(main())
