"""FastAPI router for EFN Bank Adapter."""
from dataclasses import asdict
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from .security import verify_signature
from .models import (
    AuthorizationRequest, CaptureRequest, ReversalRequest,
    DebitRequest, CreditRequest, BalanceRequest,
    AccountEnquiryRequest, ConsentOTPRequest, ConsentVerifyRequest,
)


# Pydantic input models
class AuthBody(BaseModel):
    uan: str; amount: float; currency: str; efn_reference: str; auth_method: str
    biometric_hash: Optional[str] = None; pin_hash: Optional[str] = None
    terminal_id: Optional[str] = None; gps: Optional[str] = None

class CaptureBody(BaseModel):
    authorization_id: str; amount: float; efn_reference: str

class ReversalBody(BaseModel):
    authorization_id: str; efn_reference: str; reason: Optional[str] = None

class DebitBody(BaseModel):
    uan: str; amount: float; currency: str; tx_ref: str; efn_reference: str
    narration: Optional[str] = None

class CreditBody(BaseModel):
    uan: str; amount: float; currency: str; tx_ref: str; efn_reference: str
    narration: Optional[str] = None

class BalanceBody(BaseModel):
    uan: str

class EnquiryBody(BaseModel):
    uan: str

class ConsentOTPBody(BaseModel):
    uan: str; purpose: str

class ConsentVerifyBody(BaseModel):
    uan: str; otp: str; purpose: str


async def _verify(request: Request, api_secret: str):
    body = await request.body()
    ok = verify_signature(
        api_secret,
        request.headers.get("x-efn-timestamp", ""),
        body,
        request.headers.get("x-efn-signature", ""),
    )
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid or expired signature")


def make_router(adapter, api_secret: str) -> APIRouter:
    router = APIRouter(prefix="/efn/v1")

    @router.post("/authorizations")
    async def authorize(body: AuthBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.authorize(AuthorizationRequest(**body.dict())))

    @router.post("/authorizations/{pk}/capture")
    async def capture(pk: str, body: CaptureBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.capture(pk, CaptureRequest(**body.dict())))

    @router.post("/authorizations/{pk}/reversal")
    async def reversal(pk: str, body: ReversalBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.reverse(pk, ReversalRequest(**body.dict())))

    @router.post("/debit")
    async def debit(body: DebitBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.debit(DebitRequest(**body.dict())))

    @router.post("/credit")
    async def credit(body: CreditBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.credit(CreditRequest(**body.dict())))

    @router.post("/balance")
    async def balance(body: BalanceBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.balance(BalanceRequest(**body.dict())))

    @router.post("/account-enquiry")
    async def account_enquiry(body: EnquiryBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.account_enquiry(AccountEnquiryRequest(**body.dict())))

    @router.get("/transaction/{ref}/status")
    async def tx_status(ref: str):
        return asdict(adapter.transaction_status(ref))

    @router.post("/consent-otp")
    async def consent_otp(body: ConsentOTPBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.consent_otp(ConsentOTPRequest(**body.dict())))

    @router.post("/consent-verify")
    async def consent_verify(body: ConsentVerifyBody, request: Request):
        await _verify(request, api_secret)
        return asdict(adapter.consent_verify(ConsentVerifyRequest(**body.dict())))

    @router.get("/health")
    async def health():
        return {"status": "ok"}

    return router
