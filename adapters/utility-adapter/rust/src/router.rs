//! Axum HTTP router for the EFN Utility Provider Adapter.
//!
//! Exposes three endpoints that EFN Smart Terminal calls:
//!
//! | Method | Path | Description |
//! |--------|------|-------------|
//! | POST | `/efn/v1/utility/validate` | Validate customer account/meter |
//! | POST | `/efn/v1/utility/dispense` | Dispense value token after payment |
//! | GET | `/efn/v1/utility/transaction/:ref/status` | Query transaction result |

use axum::{
    Router,
    routing::{get, post},
    extract::{Path, Request, State},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    Json,
    http::{StatusCode, HeaderMap},
    body::to_bytes,
};
use serde_json::json;
use std::sync::Arc;

use crate::{adapter::EFNUtilityAdapter, models::*, security::verify_signature};

/// Shared application state injected into every handler.
#[derive(Clone)]
pub struct AppState {
    pub adapter: Arc<dyn EFNUtilityAdapter>,
    pub secret: String,
}

/// HMAC authentication middleware.
///
/// All requests to `/efn/v1/utility/**` must include:
/// - `X-EFN-Timestamp`: Unix timestamp (seconds). Rejected if >300s old.
/// - `X-EFN-Signature`: `v1=<hmac-sha256(secret, timestamp.body)>`
async fn efn_auth_middleware(
    State(state): State<AppState>,
    request: Request,
    next: Next,
) -> Result<Response, (StatusCode, Json<serde_json::Value>)> {
    let path = request.uri().path().to_string();

    // Only authenticate EFN utility paths
    if !path.starts_with("/efn/v1/utility") {
        return Ok(next.run(request).await);
    }

    let headers: HeaderMap = request.headers().clone();
    let timestamp = headers
        .get("X-EFN-Timestamp")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("0")
        .to_string();
    let signature = headers
        .get("X-EFN-Signature")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("")
        .to_string();

    // Buffer the body so we can both verify HMAC and pass it to the handler
    let (parts, body) = request.into_parts();
    let body_bytes = to_bytes(body, 1024 * 1024) // 1MB max
        .await
        .map_err(|_| {
            (
                StatusCode::BAD_REQUEST,
                Json(json!({"error": "Failed to read request body"})),
            )
        })?;

    if !verify_signature(&state.secret, &timestamp, &signature, &body_bytes, 300) {
        return Err((
            StatusCode::UNAUTHORIZED,
            Json(json!({
                "error": "Invalid EFN signature or expired timestamp",
                "hint": "Ensure X-EFN-Timestamp is within 300s of server time and X-EFN-Signature is v1=HMAC-SHA256(secret, timestamp.body)"
            })),
        ));
    }

    // Reconstruct the request with the buffered body
    let request = Request::from_parts(parts, axum::body::Body::from(body_bytes));
    Ok(next.run(request).await)
}

/// POST /efn/v1/utility/validate
///
/// EFN calls this to verify a customer account or meter number before accepting payment.
async fn validate_handler(
    State(state): State<AppState>,
    Json(req): Json<ValidateRequest>,
) -> impl IntoResponse {
    let resp = state.adapter.validate_customer(req).await;
    Json(resp)
}

/// POST /efn/v1/utility/dispense
///
/// EFN calls this after the customer pays. The adapter must generate and return
/// a value token (e.g. STS prepaid electricity token, voucher code, data pin).
async fn dispense_handler(
    State(state): State<AppState>,
    Json(req): Json<DispenseRequest>,
) -> impl IntoResponse {
    let resp = state.adapter.dispense_value(req).await;
    Json(resp)
}

/// GET /efn/v1/utility/transaction/:efn_reference/status
///
/// EFN calls this to check the result of a previous dispense transaction.
/// Used for reconciliation and retry flows.
async fn status_handler(
    State(state): State<AppState>,
    Path(efn_reference): Path<String>,
) -> impl IntoResponse {
    let resp = state.adapter.transaction_status(efn_reference).await;
    Json(resp)
}

/// Build the Axum router with all EFN endpoints and HMAC authentication.
///
/// # Example
/// ```rust,no_run
/// # use std::sync::Arc;
/// # use efn_utility_adapter::router::make_router;
/// # use efn_utility_adapter::adapter::EFNUtilityAdapter;
/// # use efn_utility_adapter::models::*;
/// # use axum::async_trait;
/// # struct MyAdapter;
/// # #[async_trait]
/// # impl EFNUtilityAdapter for MyAdapter {
/// #     async fn validate_customer(&self, req: ValidateRequest) -> ValidateResponse { ValidateResponse { is_valid: false, customer_name: None, customer_address: None, minimum_amount: 0.0, outstanding_balance: 0.0 } }
/// #     async fn dispense_value(&self, req: DispenseRequest) -> DispenseResponse { DispenseResponse { status: "success".to_string(), dispense_ref: None, value_token: None, receipt_details: Default::default(), error: None } }
/// #     async fn transaction_status(&self, _: String) -> TransactionStatusResponse { TransactionStatusResponse { status: "success".to_string(), value_token: None } }
/// # }
/// #[tokio::main]
/// async fn main() {
///     let app = make_router(Arc::new(MyAdapter), "your_efn_secret".to_string());
///     let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
///     axum::serve(listener, app).await.unwrap();
/// }
/// ```
pub fn make_router(adapter: Arc<dyn EFNUtilityAdapter>, secret: String) -> Router {
    let state = AppState { adapter, secret };

    Router::new()
        .route("/efn/v1/utility/validate", post(validate_handler))
        .route("/efn/v1/utility/dispense", post(dispense_handler))
        .route(
            "/efn/v1/utility/transaction/:efn_reference/status",
            get(status_handler),
        )
        .layer(middleware::from_fn_with_state(
            state.clone(),
            efn_auth_middleware,
        ))
        .with_state(state)
}
