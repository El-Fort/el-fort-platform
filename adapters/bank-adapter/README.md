# EFN Bank Adapter SDKs

Partner banks implement the EFN Adapter Spec v1.0 to connect their customers
to the El-Fort Payment Network — biometric ATM/PoS/subscriptions, offline transactions,
and Open Banking.

## Available SDKs

| Language | Framework | Directory |
|---|---|---|
| Python | Django / FastAPI | [python/](python/) |
| Node.js | Express / TypeScript | [nodejs/](nodejs/) |
| Go | gin | [go/](go/) |
| Rust | axum | [rust/](rust/) |
| Java | Spring Boot 3 | [java/](java/) |
| C# | ASP.NET Core 8 | [csharp/](csharp/) |

## Endpoints your bank implements

```
POST /efn/v1/authorizations                         ATM/PoS hold
POST /efn/v1/authorizations/{id}/capture            Capture hold
POST /efn/v1/authorizations/{id}/reversal           Void/reverse
POST /efn/v1/debit                                  Subscription debit
POST /efn/v1/credit                                 Credit customer account
POST /efn/v1/balance                                Account balance
POST /efn/v1/account-enquiry                        Verify account holder
GET  /efn/v1/transaction/{ref}/status               Transaction status
POST /efn/v1/consent-otp                            Send OTP (optional)
POST /efn/v1/consent-verify                         Verify OTP (optional)
GET  /efn/v1/health                                 Health check
```

## Security

Every request from EFN Gateway includes:
```
X-EFN-API-Key:    {key issued at bank registration}
X-EFN-Timestamp:  {unix timestamp}
X-EFN-Signature:  v1={base64(HMAC-SHA256(api_secret, timestamp + "." + raw_body))}
Idempotency-Key:  {efn_reference}:{operation}
```

Reject requests where `|now - timestamp| > 300s` to prevent replay attacks.
Use `hmac.compare_digest` (or equivalent constant-time comparison) to prevent timing attacks.

## Registration

```
POST /efn/api/subscriptions/banks/
{
  "bank_code": "YOURBANK",
  "bank_name": "Your Bank Ltd",
  "adapter_url": "https://api.yourbank.com",
  "supported_ops": ["debit", "credit", "balance", "enquiry", "consent_otp"]
}
→ { "bank_code": "YOURBANK", "hmac_secret": "..." }
```

Store the returned `hmac_secret` as `EFN_API_SECRET` in your environment.
