use std::sync::Arc;
use axum::{
    Router,
    body::Bytes,
    extract::{Path, State},
    http::{HeaderMap, StatusCode},
    response::IntoResponse,
    routing::{get, post},
    Json,
};
use serde_json::json;

use crate::{adapter::EFNBankAdapter, models::*, security::verify_signature};

#[derive(Clone)]
pub struct AppState {
    pub adapter: Arc<dyn EFNBankAdapter>,
    pub api_secret: String,
}

fn check_sig(headers: &HeaderMap, body: &[u8], secret: &str) -> bool {
    let ts = headers.get("x-efn-timestamp").and_then(|v| v.to_str().ok()).unwrap_or("");
    let sig = headers.get("x-efn-signature").and_then(|v| v.to_str().ok()).unwrap_or("");
    verify_signature(secret, ts, body, sig)
}

async fn authorize(State(s): State<AppState>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<AuthorizationRequest>(&body) {
        Ok(req) => match s.adapter.authorize(req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn capture(State(s): State<AppState>, Path(id): Path<String>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<CaptureRequest>(&body) {
        Ok(req) => match s.adapter.capture(&id, req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn reversal(State(s): State<AppState>, Path(id): Path<String>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<ReversalRequest>(&body) {
        Ok(req) => match s.adapter.reverse(&id, req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn debit(State(s): State<AppState>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<DebitRequest>(&body) {
        Ok(req) => match s.adapter.debit(req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn credit(State(s): State<AppState>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<CreditRequest>(&body) {
        Ok(req) => match s.adapter.credit(req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn balance(State(s): State<AppState>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<BalanceRequest>(&body) {
        Ok(req) => match s.adapter.balance(req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn account_enquiry(State(s): State<AppState>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<AccountEnquiryRequest>(&body) {
        Ok(req) => match s.adapter.account_enquiry(req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn tx_status(State(s): State<AppState>, Path(ref_): Path<String>) -> impl IntoResponse {
    match s.adapter.transaction_status(&ref_) {
        Ok(resp) => Json(resp).into_response(),
        Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
    }
}

async fn consent_otp(State(s): State<AppState>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<ConsentOTPRequest>(&body) {
        Ok(req) => match s.adapter.consent_otp(req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn consent_verify(State(s): State<AppState>, headers: HeaderMap, body: Bytes) -> impl IntoResponse {
    if !check_sig(&headers, &body, &s.api_secret) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"success":false,"message":"Invalid or expired signature"}))).into_response();
    }
    match serde_json::from_slice::<ConsentVerifyRequest>(&body) {
        Ok(req) => match s.adapter.consent_verify(req) {
            Ok(resp) => Json(resp).into_response(),
            Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, e).into_response(),
        },
        Err(e) => (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

async fn health() -> impl IntoResponse {
    Json(json!({"status": "ok"}))
}

pub fn make_router(adapter: Arc<dyn EFNBankAdapter>, api_secret: String) -> Router {
    let state = AppState { adapter, api_secret };
    Router::new()
        .route("/efn/v1/authorizations", post(authorize))
        .route("/efn/v1/authorizations/:id/capture", post(capture))
        .route("/efn/v1/authorizations/:id/reversal", post(reversal))
        .route("/efn/v1/debit", post(debit))
        .route("/efn/v1/credit", post(credit))
        .route("/efn/v1/balance", post(balance))
        .route("/efn/v1/account-enquiry", post(account_enquiry))
        .route("/efn/v1/transaction/:ref/status", get(tx_status))
        .route("/efn/v1/consent-otp", post(consent_otp))
        .route("/efn/v1/consent-verify", post(consent_verify))
        .route("/efn/v1/health", get(health))
        .with_state(state)
}
