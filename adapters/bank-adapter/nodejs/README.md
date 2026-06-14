# EFN Bank Adapter — Node.js / TypeScript SDK

## Install

```bash
npm install
npm run build
```

## Usage

```typescript
import express from "express";
import { makeRouter, EFNBankAdapter } from "@elfort/efn-bank-adapter";

class MyBankAdapter implements EFNBankAdapter {
  async authorize(req) { /* connect to your core banking */ }
  // ... implement all methods
}

const app = express();
app.use("/efn/v1", makeRouter(new MyBankAdapter(), process.env.EFN_API_SECRET!));
app.listen(3000);
```

## Signature

`HMAC-SHA256(apiSecret, timestamp + "." + rawBody)` → base64 → prefix `v1=`

Timestamps outside ±300 s are rejected.

## Endpoints implemented

| Method | Path |
|--------|------|
| POST | /efn/v1/authorizations |
| POST | /efn/v1/authorizations/:id/capture |
| POST | /efn/v1/authorizations/:id/reversal |
| POST | /efn/v1/debit |
| POST | /efn/v1/credit |
| POST | /efn/v1/balance |
| POST | /efn/v1/account-enquiry |
| GET  | /efn/v1/transaction/:ref/status |
| POST | /efn/v1/consent-otp |
| POST | /efn/v1/consent-verify |
| GET  | /efn/v1/health |
