# EFN Bank Adapter — Rust SDK

## Usage

```rust
use std::sync::Arc;
use efn_bank_adapter::{adapter::EFNBankAdapter, models::*, router::make_router};

struct MyBank;

impl EFNBankAdapter for MyBank {
    fn authorize(&self, req: AuthorizationRequest) -> Result<AuthorizationResponse, String> {
        // connect to your core banking
    }
    // implement remaining methods...
}

#[tokio::main]
async fn main() {
    let app = make_router(Arc::new(MyBank), "your-efn-secret".into());
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

## Build

```bash
cargo build --release
EFN_API_SECRET=your-secret ./target/release/efn-bank-adapter
```

## Signature

`HMAC-SHA256(apiSecret, timestamp + "." + rawBody)` → base64 → prefix `v1=`

Replay window: ±300 seconds.
