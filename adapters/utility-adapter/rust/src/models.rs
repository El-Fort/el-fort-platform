use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Deserialize, Serialize)]
pub struct ValidateRequest { pub customer_ref: String, pub utility_category: String }
#[derive(Debug, Deserialize, Serialize)]
pub struct ValidateResponse { pub is_valid: bool, pub customer_name: Option<String>, pub customer_address: Option<String>, pub minimum_amount: f64, pub outstanding_balance: f64 }
#[derive(Debug, Deserialize, Serialize)]
pub struct DispenseRequest { pub customer_ref: String, pub amount: f64, pub currency: String, pub efn_reference: String }
#[derive(Debug, Deserialize, Serialize)]
pub struct DispenseResponse { pub status: String, pub dispense_ref: Option<String>, pub value_token: Option<String>, pub receipt_details: HashMap<String, String>, pub error: Option<String> }
#[derive(Debug, Deserialize, Serialize)]
pub struct TransactionStatusResponse { pub status: String, pub value_token: Option<String> }
