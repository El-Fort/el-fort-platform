#!/usr/bin/env python3
"""Local mock EFN partner-bank adapter for certification and development.

Implements the local-ngn-v1 adapter endpoints with in-memory accounts,
idempotency storage, authorization holds, capture/debit, credits, reversals,
transaction status, and reconciliation report acceptance.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

API_KEY = "efn_sandbox_bank_key"
API_SECRET = "sandbox_secret"
REPLAY_WINDOW_SECONDS = 300

accounts: dict[str, dict[str, Any]] = {
    "0123456789": {"name": "EFN SOURCE CUSTOMER", "currency": "NGN", "available": 1000000.00, "ledger": 1000000.00, "status": "active"},
    "9876543210": {"name": "EFN DESTINATION CUSTOMER", "currency": "NGN", "available": 250000.00, "ledger": 250000.00, "status": "active"},
    "5780123456": {"name": "MOCK STANBIC VIRTUAL USER", "currency": "NGN", "available": 500000.00, "ledger": 500000.00, "status": "active"},
    "221123456": {"name": "MOCK VIRTUAL ID ACCOUNT", "currency": "NGN", "available": 300000.00, "ledger": 300000.00, "status": "active"},
    "wallet_12345": {"name": "MOCK WALLET ACCOUNT", "currency": "NGN", "available": 150000.00, "ledger": 150000.00, "status": "active"},
}
authorizations: dict[str, dict[str, Any]] = {}
transactions: dict[str, dict[str, Any]] = {}
idempotency: dict[str, dict[str, Any]] = {}
reconciliation_reports: dict[str, dict[str, Any]] = {}


def ensure_account(account_number: str | None) -> dict[str, Any] | None:
    if not account_number:
        return None
    clean_number = str(account_number).strip()
    if clean_number not in accounts:
        # Check if it matches virtual ID or wallet format
        if clean_number.startswith("578") or clean_number.startswith("221") or "wallet" in clean_number or clean_number.startswith("wallet_"):
            accounts[clean_number] = {
                "name": f"MOCK WALLET USER {clean_number[-4:]}" if "wallet" in clean_number else f"MOCK VIRTUAL ID USER {clean_number[-4:]}",
                "currency": "NGN",
                "available": 500000.00,
                "ledger": 500000.00,
                "status": "active"
            }
    return accounts.get(clean_number)


def canonical_response(status: int, payload: dict[str, Any]) -> tuple[int, bytes]:
    return status, json.dumps(payload, separators=(",", ":")).encode("utf-8")


def sign(secret: str, timestamp: str, body: bytes) -> str:
    mac = hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256)
    return "v1=" + base64.b64encode(mac.digest()).decode("ascii")


def verify_headers(handler: BaseHTTPRequestHandler, body: bytes) -> tuple[bool, int, str]:
    path = urlparse(handler.path).path
    if "checksum-validator" in path or "virtual-id/name-enquiry" in path:
        return True, 200, "ok"
    api_key = handler.headers.get("X-EFN-API-Key", "")
    timestamp = handler.headers.get("X-EFN-Timestamp", "")
    signature = handler.headers.get("X-EFN-Signature", "")
    if api_key != API_KEY:
        return False, 401, "invalid api key"
    try:
        ts = int(timestamp)
    except ValueError:
        return False, 401, "invalid timestamp"
    if abs(int(time.time()) - ts) > REPLAY_WINDOW_SECONDS:
        return False, 401, "stale timestamp"
    expected = sign(API_SECRET, timestamp, body)
    if not hmac.compare_digest(signature, expected):
        return False, 401, "invalid signature"
    return True, 200, "ok"


def idempotent(handler: BaseHTTPRequestHandler, body: bytes, compute):
    key = handler.headers.get("Idempotency-Key")
    if not key:
        return canonical_response(400, {"success": False, "message": "Idempotency-Key required"})
    body_hash = hashlib.sha256(body).hexdigest()
    existing = idempotency.get(key)
    if existing:
        if existing["body_hash"] != body_hash:
            return canonical_response(409, {"success": False, "message": "idempotency conflict"})
        return existing["status"], existing["body"]
    status, response_body = compute()
    idempotency[key] = {"body_hash": body_hash, "status": status, "body": response_body}
    return status, response_body


def parse_json(body: bytes) -> dict[str, Any]:
    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


def amount_value(payload: dict[str, Any]) -> float:
    return float(payload.get("amount") or 0)


def account_response(account_number: str, ref: str = "") -> tuple[int, bytes]:
    acct = ensure_account(account_number)
    if not acct:
        return canonical_response(200, {"success": False, "status": "not_found", "account_number": account_number, "account_name": "", "currency": "NGN", "response_code": "25", "message": "Account not found"})
    return canonical_response(200, {"success": True, "status": acct["status"], "account_number": account_number, "account_name": acct["name"], "currency": acct["currency"], "response_code": "00", "message": "Approved"})


class Handler(BaseHTTPRequestHandler):
    server_version = "EFNMockBankAdapter/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print("mock-bank", self.address_string(), fmt % args)

    def send_json(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        body = b""
        ok, status, msg = verify_headers(self, body)
        if not ok:
            self.send_json(*canonical_response(status, {"success": False, "message": msg}))
            return
        match = re.fullmatch(r"/efn/v1/transactions/([^/]+)", parsed.path)
        if not match:
            self.send_json(*canonical_response(404, {"success": False, "message": "not found"}))
            return
        ref = match.group(1)
        tx = transactions.get(ref)
        if not tx:
            self.send_json(*canonical_response(404, {"success": False, "message": "EFN reference not found"}))
            return
        self.send_json(*canonical_response(200, {"success": True, "efn_reference": ref, **tx}))

    def do_POST(self) -> None:
        body = self.read_body()
        ok, status, msg = verify_headers(self, body)
        if not ok:
            self.send_json(*canonical_response(status, {"success": False, "message": msg}))
            return
        path = urlparse(self.path).path
        try:
            if "checksum-validator" in path:
                self.send_json(*self.validate_checksum(body))
            elif "virtual-id/name-enquiry" in path:
                self.send_json(*self.virtual_id_name_enquiry(body))
            elif path == "/efn/v1/accounts/resolve":
                self.send_json(*idempotent(self, body, lambda: self.accounts_resolve(body)))
            elif path == "/efn/v1/accounts/balance":
                self.send_json(*idempotent(self, body, lambda: self.accounts_balance(body)))
            elif path == "/efn/v1/authorizations":
                self.send_json(*idempotent(self, body, lambda: self.authorize(body)))
            elif re.fullmatch(r"/efn/v1/authorizations/[^/]+/capture", path):
                auth_id = path.split("/")[4]
                self.send_json(*idempotent(self, body, lambda: self.capture(auth_id, body)))
            elif re.fullmatch(r"/efn/v1/authorizations/[^/]+/reversal", path):
                auth_id = path.split("/")[4]
                self.send_json(*idempotent(self, body, lambda: self.reversal(auth_id, body)))
            elif path == "/efn/v1/credits":
                self.send_json(*idempotent(self, body, lambda: self.credit(body)))
            elif path == "/efn/v1/reconciliation/report":
                self.send_json(*idempotent(self, body, lambda: self.reconciliation(body)))
            else:
                self.send_json(*canonical_response(404, {"success": False, "message": "not found"}))
        except Exception as exc:  # noqa: BLE001 - mock server should return JSON errors.
            self.send_json(*canonical_response(500, {"success": False, "message": str(exc)}))

    def validate_checksum(self, body: bytes) -> tuple[int, bytes]:
        return canonical_response(200, {
            "responseCode": "00",
            "responseMsg": "Successful",
            "responseDetails": {
                "isValid": "True"
            }
        })

    def virtual_id_name_enquiry(self, body: bytes) -> tuple[int, bytes]:
        payload = parse_json(body)
        account_number = payload.get("accountNumber")
        acct = ensure_account(account_number)
        if acct:
            name = acct["name"]
            response_code = "00"
            desc = "SUCCESSFUL"
        else:
            if account_number and (account_number.startswith("578") or account_number.startswith("221") or "wallet" in account_number):
                name = f"MOCK WALLET USER {account_number[-4:]}"
                response_code = "00"
                desc = "SUCCESSFUL"
            else:
                return canonical_response(200, {
                    "responseCode": "07",
                    "responseDescription": "Invalid Account",
                    "accountName": ""
                })
        
        return canonical_response(200, {
            "responseCode": response_code,
            "responseDescription": desc,
            "accountName": name
        })

    def accounts_resolve(self, body: bytes) -> tuple[int, bytes]:
        payload = parse_json(body)
        account_number = payload.get("account_number") or payload.get("source_account_number")
        return account_response(account_number, payload.get("efn_reference", ""))

    def accounts_balance(self, body: bytes) -> tuple[int, bytes]:
        payload = parse_json(body)
        account_number = payload.get("account_number")
        acct = ensure_account(account_number)
        if not acct:
            return canonical_response(200, {"success": False, "available_balance": "0.00", "ledger_balance": "0.00", "currency": payload.get("currency", "NGN"), "response_code": "25", "message": "Account not found"})
        return canonical_response(200, {"success": True, "available_balance": f"{acct['available']:.2f}", "ledger_balance": f"{acct['ledger']:.2f}", "currency": acct["currency"], "response_code": "00", "message": "Approved"})

    def authorize(self, body: bytes) -> tuple[int, bytes]:
        payload = parse_json(body)
        ref = payload["efn_reference"]
        source = payload["source_account_number"]
        amount = amount_value(payload)
        acct = ensure_account(source)
        if not acct or acct["status"] != "active":
            return canonical_response(200, {"success": False, "status": "declined", "response_code": "25", "message": "Account not active"})
        if acct["available"] < amount:
            return canonical_response(200, {"success": False, "status": "declined", "response_code": "51", "message": "Insufficient funds"})
        auth_id = "AUTH-" + ref
        acct["available"] -= amount
        authorizations[auth_id] = {"ref": ref, "source": source, "amount": amount, "status": "authorized"}
        transactions[ref] = {"status": "authorized", "authorization_id": auth_id, "amount": f"{amount:.2f}", "currency": payload.get("currency", "NGN"), "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        return canonical_response(200, {"success": True, "status": "authorized", "authorization_id": auth_id, "bank_reference": "HOLD-" + ref, "response_code": "00", "message": "Approved"})

    def capture(self, auth_id: str, body: bytes) -> tuple[int, bytes]:
        auth = authorizations.get(auth_id)
        if not auth:
            return canonical_response(404, {"success": False, "status": "failed", "response_code": "25", "message": "Authorization not found"})
        if auth["status"] == "completed":
            return canonical_response(200, {"success": True, "status": "completed", "authorization_id": auth_id, "bank_reference": "DEBIT-" + auth["ref"], "response_code": "00", "message": "Already captured"})
        acct = ensure_account(auth["source"])
        acct["ledger"] -= auth["amount"]
        auth["status"] = "completed"
        transactions[auth["ref"]].update({"status": "completed", "debit_reference": "DEBIT-" + auth["ref"], "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return canonical_response(200, {"success": True, "status": "completed", "authorization_id": auth_id, "bank_reference": "DEBIT-" + auth["ref"], "response_code": "00", "message": "Debited"})

    def credit(self, body: bytes) -> tuple[int, bytes]:
        payload = parse_json(body)
        ref = payload["efn_reference"]
        dest = payload["destination_account_number"]
        amount = amount_value(payload)
        acct = ensure_account(dest)
        if not acct or acct["status"] != "active":
            return canonical_response(200, {"success": False, "status": "failed", "response_code": "25", "message": "Destination account not active"})
        acct["available"] += amount
        acct["ledger"] += amount
        transactions.setdefault(ref, {"status": "completed", "amount": f"{amount:.2f}", "currency": payload.get("currency", "NGN")})
        transactions[ref].update({"status": "credited", "credit_reference": "CREDIT-" + ref, "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return canonical_response(200, {"success": True, "status": "credited", "bank_reference": "CREDIT-" + ref, "response_code": "00", "message": "Credited"})

    def reversal(self, auth_id: str, body: bytes) -> tuple[int, bytes]:
        auth = authorizations.get(auth_id)
        if not auth:
            return canonical_response(404, {"success": False, "status": "failed", "response_code": "25", "message": "Authorization not found"})
        if auth["status"] == "reversed":
            return canonical_response(200, {"success": True, "status": "reversed", "authorization_id": auth_id, "bank_reference": "REV-" + auth["ref"], "response_code": "00", "message": "Already reversed"})
        acct = ensure_account(auth["source"])
        if auth["status"] == "authorized":
            acct["available"] += auth["amount"]
        elif auth["status"] == "completed":
            acct["available"] += auth["amount"]
            acct["ledger"] += auth["amount"]
        auth["status"] = "reversed"
        transactions[auth["ref"]].update({"status": "reversed", "reversal_reference": "REV-" + auth["ref"], "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return canonical_response(200, {"success": True, "status": "reversed", "authorization_id": auth_id, "bank_reference": "REV-" + auth["ref"], "response_code": "00", "message": "Reversed"})

    def reconciliation(self, body: bytes) -> tuple[int, bytes]:
        payload = parse_json(body)
        report_id = payload.get("report_id") or "REPORT-" + str(int(time.time()))
        reconciliation_reports[report_id] = payload
        txs = payload.get("transactions") or []
        return canonical_response(200, {"success": True, "report_id": report_id, "accepted_count": len(txs), "rejected_count": 0, "message": "Accepted"})


def main() -> int:
    global API_KEY, API_SECRET

    parser = argparse.ArgumentParser(description="Run mock EFN partner-bank adapter")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--api-key", default=API_KEY)
    parser.add_argument("--api-secret", default=API_SECRET)
    args = parser.parse_args()

    API_KEY = args.api_key
    API_SECRET = args.api_secret

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Mock EFN bank adapter listening on http://{args.host}:{args.port}")
    print(f"API key: {API_KEY}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping mock adapter")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
