import os
import hmac
import hashlib
import time
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="EFN Utility Provider Adapter")

API_SECRET = os.getenv("EFN_API_SECRET", "test_secret_key_efn").encode('utf-8')

def verify_efn_signature(timestamp: str, signature_header: str, body: bytes) -> bool:
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False
        expected_sig = hmac.new(API_SECRET, timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
        provided_sig = signature_header.replace("v1=", "")
        return hmac.compare_digest(expected_sig, provided_sig)
    except Exception:
        return False

class ValidateRequest(BaseModel):
    customer_ref: str
    utility_category: str

class DispenseRequest(BaseModel):
    customer_ref: str
    amount: float
    currency: str
    efn_reference: str

@app.middleware("http")
async def require_efn_signature(request: Request, call_next):
    if request.url.path.startswith("/efn/v1/utility"):
        body = await request.body()
        timestamp = request.headers.get("X-EFN-Timestamp", "0")
        sig = request.headers.get("X-EFN-Signature", "")
        if not verify_efn_signature(timestamp, sig, body):
            from fastapi.responses import JSONResponse
            return JSONResponse({"error": "Invalid signature or expired timestamp"}, status_code=401)
    return await call_next(request)

@app.post("/efn/v1/utility/validate")
async def validate_customer(req: ValidateRequest):
    # TODO: Implement actual utility database lookup here
    if req.customer_ref == "12345678901":
        return {
            "is_valid": True,
            "customer_name": "John Doe",
            "customer_address": "123 Main St",
            "minimum_amount": 1000,
            "outstanding_balance": 0.0
        }
    return {"is_valid": False}

@app.post("/efn/v1/utility/dispense")
async def dispense_value(req: DispenseRequest):
    # TODO: Implement actual value dispensation (e.g. STS token generation)
    return {
        "status": "success",
        "dispense_ref": "UTL-998877",
        "value_token": "4455-6677-8899-0011-2233",
        "receipt_details": {
            "units": f"{req.amount / 100} units",
            "tax": "0 NGN"
        }
    }

@app.get("/efn/v1/utility/transaction/{efn_reference}/status")
async def tx_status(efn_reference: str):
    # TODO: Lookup transaction
    return {"status": "success", "value_token": "4455-6677-8899-0011-2233"}
