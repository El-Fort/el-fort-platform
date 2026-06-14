# EFN Bank Adapter — Python SDK

Integrate your bank with the EFN Gateway using Django or FastAPI.

## Install

```bash
pip install fastapi uvicorn  # or Django
```

## Django

```python
# urls.py
from efn_adapter.django_router import make_router
from mybank.adapter import MyBankAdapter

_views = make_router(MyBankAdapter(), api_secret="YOUR_EFN_SECRET")

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
```

## FastAPI

```python
from fastapi import FastAPI
from efn_adapter.fastapi_router import make_router
from mybank.adapter import MyBankAdapter

app = FastAPI()
app.include_router(make_router(MyBankAdapter(), api_secret="YOUR_EFN_SECRET"))
```

## Implement your adapter

```python
from efn_adapter import EFNBankAdapter

class MyBankAdapter(EFNBankAdapter):
    def authorize(self, req): ...
    def capture(self, authorization_id, req): ...
    def reverse(self, authorization_id, req): ...
    def debit(self, req): ...
    def credit(self, req): ...
    def balance(self, req): ...
    def account_enquiry(self, req): ...
    def transaction_status(self, ref): ...
    def consent_otp(self, req): ...
    def consent_verify(self, req): ...
```

## Signature verification

`HMAC-SHA256(api_secret, timestamp + "." + raw_body)` → base64 → prefix `v1=`

Timestamps outside ±300 seconds are rejected.
