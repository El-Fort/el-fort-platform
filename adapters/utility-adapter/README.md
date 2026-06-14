# EFN Utility Provider Adapter SDK

This SDK enables utility companies (electricity, water, gas, cable TV, etc.) to integrate 
with the EL-FORT Fintech Network (EFN) Smart Terminal.

## How It Works

```
EFN Smart Terminal → [HMAC-signed request] → Your Adapter Server → Your Utility DB/System
```

When a customer initiates a utility payment on a Smart Terminal, EFN calls your adapter 
server with three possible requests:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/efn/v1/utility/validate` | Verify the customer's account/meter number |
| POST | `/efn/v1/utility/dispense` | Process payment & return a value token |
| GET | `/efn/v1/utility/transaction/{ref}/status` | Query a prior transaction |

## Authentication

All requests from EFN include two headers:

```
X-EFN-Timestamp: 1718400000          (Unix timestamp)
X-EFN-Signature: v1=<hmac-sha256>   (HMAC-SHA256 of timestamp.body)
```

You MUST verify these on every request using your shared EFN API secret.

## Available SDKs

| Language | Directory | Framework |
|----------|-----------|-----------|
| Python | `python/` | FastAPI / Django |
| Node.js / TypeScript | `nodejs/` | Express |
| Go | `go/` | Chi Router |
| Rust | `rust/` | Axum |
| Java | `java/` | Spring Boot |
| C# | `csharp/` | ASP.NET Core |

## Quick Start (Python FastAPI)

```python
from fastapi import FastAPI
from efn_utility_adapter import EFNUtilityAdapter, ValidateRequest, ValidateResponse
from efn_utility_adapter import DispenseRequest, DispenseResponse, TransactionStatusResponse
from efn_utility_adapter.fastapi_router import make_router
import os

class MyElectricityAdapter(EFNUtilityAdapter):
    def validate_customer(self, req: ValidateRequest) -> ValidateResponse:
        # Look up the meter number in your DB
        meter = db.get_meter(req.customer_ref)
        if not meter:
            return ValidateResponse(is_valid=False)
        return ValidateResponse(
            is_valid=True,
            customer_name=meter.name,
            customer_address=meter.address,
            minimum_amount=1000.0,
            outstanding_balance=meter.debt
        )

    def dispense_value(self, req: DispenseRequest) -> DispenseResponse:
        # Generate STS token or voucher code
        token = sts_generator.generate(req.customer_ref, req.amount)
        return DispenseResponse(
            status="success",
            dispense_ref="UTL-" + req.efn_reference,
            value_token=token,
            receipt_details={"units": str(req.amount / 80) + " kWh"}
        )

    def transaction_status(self, efn_reference: str) -> TransactionStatusResponse:
        tx = db.get_transaction(efn_reference)
        return TransactionStatusResponse(status=tx.status, value_token=tx.token)

app = FastAPI()
app.include_router(make_router(
    MyElectricityAdapter(),
    secret=os.environ["EFN_API_SECRET"].encode()
))
```

## One-off vs Subscription Purchases

EFN supports two payment modes for utilities:

- **One-off**: Customer pays for a specific amount of value (e.g. ₦5,000 electricity units)
- **Subscription**: Customer sets up recurring auto-purchase when their balance runs low

The `DispenseRequest` includes a `efn_reference` that is unique per transaction, enabling 
idempotent processing on your side.

## Certification

Before going live, your adapter must pass the EFN certification test suite. See the 
`certification/` directory for the automated certification script.
