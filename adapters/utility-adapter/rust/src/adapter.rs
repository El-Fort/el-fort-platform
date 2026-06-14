use crate::models::*;
use axum::async_trait;

#[async_trait]
pub trait EFNUtilityAdapter: Send + Sync {
    async fn validate_customer(&self, req: ValidateRequest) -> ValidateResponse;
    async fn dispense_value(&self, req: DispenseRequest) -> DispenseResponse;
    async fn transaction_status(&self, efn_reference: String) -> TransactionStatusResponse;
}
