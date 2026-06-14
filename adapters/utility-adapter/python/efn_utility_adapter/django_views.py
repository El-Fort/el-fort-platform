import json
import hmac as hmac_lib
import hashlib
import time
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .adapter import EFNUtilityAdapter
from .models import ValidateRequest, DispenseRequest

def _verify(secret: bytes, request) -> bool:
    try:
        body = request.body
        ts = request.META.get("HTTP_X_EFN_TIMESTAMP", "0")
        sig = request.META.get("HTTP_X_EFN_SIGNATURE", "")
        if abs(time.time() - int(ts)) > 300:
            return False
        expected = hmac_lib.new(secret, ts.encode() + b'.' + body, hashlib.sha256).hexdigest()
        provided = sig.replace("v1=", "")
        return hmac_lib.compare_digest(expected, provided)
    except Exception:
        return False

def make_views(adapter: EFNUtilityAdapter, secret: bytes):
    """
    Returns Django class-based views for each EFN endpoint.
    Register in urls.py:
        views = make_views(MyAdapter(), b"your_secret")
        urlpatterns = [
            path("efn/v1/utility/validate", views["validate"]),
            path("efn/v1/utility/dispense", views["dispense"]),
            path("efn/v1/utility/transaction/<str:efn_reference>/status", views["status"]),
        ]
    """
    @method_decorator(csrf_exempt, name="dispatch")
    class ValidateView(View):
        def post(self, request):
            if not _verify(secret, request):
                return JsonResponse({"error": "Invalid signature"}, status=401)
            req = ValidateRequest(**json.loads(request.body))
            return JsonResponse(adapter.validate_customer(req).__dict__)

    @method_decorator(csrf_exempt, name="dispatch")
    class DispenseView(View):
        def post(self, request):
            if not _verify(secret, request):
                return JsonResponse({"error": "Invalid signature"}, status=401)
            req = DispenseRequest(**json.loads(request.body))
            result = adapter.dispense_value(req)
            return JsonResponse(result.__dict__ if hasattr(result, '__dict__') else result)

    @method_decorator(csrf_exempt, name="dispatch")
    class StatusView(View):
        def get(self, request, efn_reference):
            if not _verify(secret, request):
                return JsonResponse({"error": "Invalid signature"}, status=401)
            return JsonResponse(adapter.transaction_status(efn_reference).__dict__)

    return {"validate": ValidateView.as_view(), "dispense": DispenseView.as_view(), "status": StatusView.as_view()}
