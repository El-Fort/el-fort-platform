"""Django router for EFN Bank Adapter."""
import json
from dataclasses import asdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .security import verify_signature
from .models import (
    AuthorizationRequest, CaptureRequest, ReversalRequest,
    DebitRequest, CreditRequest, BalanceRequest,
    AccountEnquiryRequest, ConsentOTPRequest, ConsentVerifyRequest,
)


def _sig_error():
    return JsonResponse({"success": False, "message": "Invalid or expired signature"}, status=401)


def _body(request):
    return request.body


def _check(request, api_secret):
    return verify_signature(
        api_secret,
        request.headers.get("X-EFN-Timestamp", ""),
        _body(request),
        request.headers.get("X-EFN-Signature", ""),
    )


def make_router(adapter, api_secret: str):
    """Return a dict of url-pattern → view suitable for urls.py inclusion."""

    @csrf_exempt
    def authorize(request):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.authorize(AuthorizationRequest(**data))
        return JsonResponse(asdict(resp))

    @csrf_exempt
    def capture(request, pk):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.capture(pk, CaptureRequest(**data))
        return JsonResponse(asdict(resp))

    @csrf_exempt
    def reversal(request, pk):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.reverse(pk, ReversalRequest(**data))
        return JsonResponse(asdict(resp))

    @csrf_exempt
    def debit(request):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.debit(DebitRequest(**data))
        return JsonResponse(asdict(resp))

    @csrf_exempt
    def credit(request):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.credit(CreditRequest(**data))
        return JsonResponse(asdict(resp))

    @csrf_exempt
    def balance(request):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.balance(BalanceRequest(**data))
        return JsonResponse(asdict(resp))

    @csrf_exempt
    def account_enquiry(request):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.account_enquiry(AccountEnquiryRequest(**data))
        return JsonResponse(asdict(resp))

    @require_http_methods(["GET"])
    def tx_status(request, ref):
        resp = adapter.transaction_status(ref)
        return JsonResponse(asdict(resp))

    @csrf_exempt
    def consent_otp(request):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.consent_otp(ConsentOTPRequest(**data))
        return JsonResponse(asdict(resp))

    @csrf_exempt
    def consent_verify(request):
        if not _check(request, api_secret):
            return _sig_error()
        data = json.loads(_body(request))
        resp = adapter.consent_verify(ConsentVerifyRequest(**data))
        return JsonResponse(asdict(resp))

    @require_http_methods(["GET"])
    def health(request):
        return JsonResponse({"status": "ok"})

    return {
        "authorize": authorize,
        "capture": capture,
        "reversal": reversal,
        "debit": debit,
        "credit": credit,
        "balance": balance,
        "account_enquiry": account_enquiry,
        "tx_status": tx_status,
        "consent_otp": consent_otp,
        "consent_verify": consent_verify,
        "health": health,
    }
