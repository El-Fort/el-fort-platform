"""Add to your Django project's urls.py"""
from django.urls import path
from efn_adapter.django_router import make_router
from .adapter_impl import MyBankAdapter

_views = make_router(MyBankAdapter(), api_secret="your-efn-api-secret")

urlpatterns = [
    path("efn/v1/authorizations", _views["authorize"]),
    path("efn/v1/authorizations/<str:pk>/capture", _views["capture"]),
    path("efn/v1/authorizations/<str:pk>/reversal", _views["reversal"]),
    path("efn/v1/debit", _views["debit"]),
    path("efn/v1/credit", _views["credit"]),
    path("efn/v1/balance", _views["balance"]),
    path("efn/v1/account-enquiry", _views["account_enquiry"]),
    path("efn/v1/transaction/<str:ref>/status", _views["tx_status"]),
    path("efn/v1/consent-otp", _views["consent_otp"]),
    path("efn/v1/consent-verify", _views["consent_verify"]),
    path("efn/v1/health", _views["health"]),
]
