import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from .adapter import EFNUtilityAdapter
from .models import ValidateRequest, DispenseRequest
from .security import verify_signature

def make_router(adapter: EFNUtilityAdapter, secret: bytes) -> APIRouter:
    """
    Creates a FastAPI router that exposes the three required EFN utility endpoints:
    
    POST /efn/v1/utility/validate         - Validate a customer account/meter number
    POST /efn/v1/utility/dispense         - Dispense value (tokens, units, credit)
    GET  /efn/v1/utility/transaction/{ref}/status - Query a transaction result

    Mount this router in your FastAPI app:
        app.include_router(make_router(MyAdapter(), secret=b"your_secret"))
    """
    router = APIRouter()

    async def _verify_request(request: Request):
        body = await request.body()
        ts = request.headers.get("X-EFN-Timestamp", "0")
        sig = request.headers.get("X-EFN-Signature", "")
        if not verify_signature(secret, ts, sig, body):
            raise HTTPException(status_code=401, detail="Invalid EFN signature or expired timestamp")
        return body

    @router.post("/efn/v1/utility/validate",
                 summary="Validate Customer",
                 description="EFN calls this endpoint to verify a customer account/meter number before payment.")
    async def validate_customer(request: Request):
        body = await _verify_request(request)
        req = ValidateRequest(**json.loads(body))
        result = adapter.validate_customer(req)
        return result

    @router.post("/efn/v1/utility/dispense",
                 summary="Dispense Value",
                 description="EFN calls this endpoint after a customer pays. The adapter must generate and return a value token (e.g. STS token, voucher code).")
    async def dispense_value(request: Request):
        body = await _verify_request(request)
        req = DispenseRequest(**json.loads(body))
        result = adapter.dispense_value(req)
        return result

    @router.get("/efn/v1/utility/transaction/{efn_reference}/status",
                summary="Transaction Status",
                description="EFN calls this endpoint to query the status of a previous dispense transaction.")
    async def transaction_status(efn_reference: str, request: Request):
        body = b""
        ts = request.headers.get("X-EFN-Timestamp", "0")
        sig = request.headers.get("X-EFN-Signature", "")
        if not verify_signature(secret, ts, sig, body):
            raise JSONResponse({"error": "Invalid signature"}, status_code=401)
        result = adapter.transaction_status(efn_reference)
        return result

    return router
