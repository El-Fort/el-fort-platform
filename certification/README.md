# EFN Partner Bank Adapter Certification Kit

This kit is used to certify a partner bank adapter before EFN enables `adapter_enabled=true` for production local transactions.

The first production scope is domestic/local EFN traffic only:

- Smart Terminal initiated transfers.
- UAN/AUN routing by EFN-assigned bank prefix.
- Biometric/PIN authorization evidence from EFN.
- Source-bank authorization and capture against the actual customer account.
- Destination-bank credit for local EFN-to-EFN transfers.
- Reversal, idempotency, status lookup, settlement, and reconciliation.

Global/cross-border services are out of scope for this certification.

## Files

| File | Purpose |
|---|---|
| `openapi_partner_bank_adapter.yaml` | Contract every bank-hosted adapter must implement |
| `test_vectors.json` | Deterministic HMAC and payload fixtures |
| `sample_config.json` | Example conformance runner config |
| `efn_certify.py` | Stdlib-only conformance test runner |
| `mock_bank_adapter.py` | Local mock partner-bank adapter for certification development |

## Required Adapter Endpoints

| Method | Path | Required behavior |
|---|---|---|
| `POST` | `/efn/v1/accounts/resolve` | Confirm real account binding and account status |
| `POST` | `/efn/v1/accounts/balance` | Return available balance where permitted |
| `POST` | `/efn/v1/authorizations` | Validate funds and place debit hold/reservation |
| `POST` | `/efn/v1/authorizations/{authorization_id}/capture` | Debit the customer's actual bank account |
| `POST` | `/efn/v1/credits` | Credit destination customer account for local EFN transfers |
| `POST` | `/efn/v1/authorizations/{authorization_id}/reversal` | Void/reverse held/captured transactions where possible |
| `GET` | `/efn/v1/transactions/{efn_reference}` | Return final/idempotent transaction status |
| `POST` | `/efn/v1/reconciliation/report` | Accept or expose reconciliation records |

## Request Signing

EFN signs every request with HMAC-SHA256:

```http
X-EFN-API-Key: <partner api_key>
X-EFN-Timestamp: <unix seconds>
X-EFN-Signature: v1=<base64(hmac_sha256(api_secret, timestamp + "." + raw_body))>
Idempotency-Key: <efn_reference>:<operation>
```

Banks must verify the exact raw request body bytes. Do not parse and reserialize JSON before verification.

Reject requests when:

- API key is unknown, suspended, or not enabled.
- Timestamp is outside the replay window, normally 5 minutes.
- Signature is invalid.
- Same `Idempotency-Key` is reused with a different payload.

## Running Certification

Validate the built-in HMAC vectors:

```bash
python3 efn/certification/efn_certify.py --self-test
```

Run against a bank sandbox adapter:

```bash
python3 efn/certification/efn_certify.py   --base-url https://bank-sandbox.example.com   --api-key efn_sandbox_bank_key   --api-secret sandbox_secret   --source-account 0123456789   --destination-account 9876543210
```

Or use a config file:

```bash
python3 efn/certification/efn_certify.py --config efn/certification/sample_config.json
```

## Certification Suites

The `local-ngn-v1` suite checks:

- HMAC signature acceptance.
- Bad signature rejection.
- Stale timestamp rejection.
- Account resolve.
- Balance inquiry.
- Authorization hold.
- Authorization idempotent replay.
- Idempotency conflict rejection.
- Capture/debit.
- Source ledger debit verification after capture.
- Destination ledger credit verification after `/credits`.
- Destination credit.
- Reversal.
- Transaction status lookup.
- Reconciliation report acceptance.

## Go-Live Rule

A bank is production eligible only when:

- The full conformance suite passes in sandbox.
- EFN verifies a successful end-to-end Smart Terminal transaction.
- Same-bank and cross-bank local transfer scenarios pass.
- Daily reconciliation matches EFN references to bank debit/credit references.
- Production credentials are issued and `adapter_enabled=true` is set by EFN operations.

## Local Mock Adapter

Start the mock bank adapter:

```bash
python3 efn/certification/mock_bank_adapter.py --port 18099
```

Run the certification suite against it:

```bash
python3 efn/certification/efn_certify.py \
  --base-url http://127.0.0.1:18099 \
  --api-key efn_sandbox_bank_key \
  --api-secret sandbox_secret \
  --source-account 0123456789 \
  --destination-account 9876543210
```

Expected result: `17/17 checks passed`.
