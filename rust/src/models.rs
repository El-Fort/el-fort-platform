use serde::{Deserialize, Serialize};

// ---- Requests ----

#[derive(Debug, Deserialize)]
pub struct AuthorizationRequest {
    pub uan: String,
    pub amount: f64,
    pub currency: String,
    pub efn_reference: String,
    pub auth_method: String,
    pub biometric_hash: Option<String>,
    pub pin_hash: Option<String>,
    pub terminal_id: Option<String>,
    pub gps: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CaptureRequest {
    pub authorization_id: String,
    pub amount: f64,
    pub efn_reference: String,
}

#[derive(Debug, Deserialize)]
pub struct ReversalRequest {
    pub authorization_id: String,
    pub efn_reference: String,
    pub reason: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct DebitRequest {
    pub uan: String,
    pub amount: f64,
    pub currency: String,
    pub tx_ref: String,
    pub efn_reference: String,
    pub narration: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreditRequest {
    pub uan: String,
    pub amount: f64,
    pub currency: String,
    pub tx_ref: String,
    pub efn_reference: String,
    pub narration: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct BalanceRequest {
    pub uan: String,
}

#[derive(Debug, Deserialize)]
pub struct AccountEnquiryRequest {
    pub uan: String,
}

#[derive(Debug, Deserialize)]
pub struct ConsentOTPRequest {
    pub uan: String,
    pub purpose: String,
}

#[derive(Debug, Deserialize)]
pub struct ConsentVerifyRequest {
    pub uan: String,
    pub otp: String,
    pub purpose: String,
}

// ---- Responses ----

#[derive(Debug, Serialize)]
pub struct AuthorizationResponse {
    pub success: bool,
    pub status: String,
    pub authorization_id: String,
    pub bank_reference: String,
    pub response_code: String,
    pub message: String,
}

#[derive(Debug, Serialize)]
pub struct CaptureReversalResponse {
    pub success: bool,
    pub status: String,
    pub bank_reference: String,
    pub response_code: String,
    pub message: String,
}

#[derive(Debug, Serialize)]
pub struct DebitCreditResponse {
    pub success: bool,
    pub status: String,
    pub bank_reference: String,
    pub tx_ref: String,
    pub response_code: String,
    pub message: String,
}

#[derive(Debug, Serialize)]
pub struct BalanceResponse {
    pub success: bool,
    pub uan: String,
    pub balance: f64,
    pub currency: String,
    pub account_number: String,
    pub response_code: String,
}

#[derive(Debug, Serialize)]
pub struct AccountEnquiryResponse {
    pub success: bool,
    pub account_number: String,
    pub account_name: String,
    pub currency: String,
    pub phone_last4: String,
    pub response_code: String,
    pub message: String,
}

#[derive(Debug, Serialize)]
pub struct TransactionStatusResponse {
    pub success: bool,
    pub status: String,
    pub bank_reference: String,
    pub response_code: String,
    pub message: String,
}

#[derive(Debug, Serialize)]
pub struct ConsentOTPResponse {
    pub success: bool,
    pub message: String,
    pub response_code: String,
}

#[derive(Debug, Serialize)]
pub struct ConsentVerifyResponse {
    pub success: bool,
    pub verified: bool,
    pub message: String,
    pub response_code: String,
}
