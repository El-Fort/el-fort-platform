use efn_utility_adapter::{
    adapter::EFNUtilityAdapter,
    models::{
        DispenseRequest, DispenseResponse, TransactionStatusResponse, ValidateRequest,
        ValidateResponse,
    },
    router::make_router,
};
use axum::async_trait;
use std::{collections::HashMap, sync::Arc};

/// Example implementation of EFNUtilityAdapter for a prepaid electricity company.
///
/// Replace the TODO sections with your actual business logic:
/// - Database lookups for meter/account validation
/// - STS token generation for electricity vending
/// - Transaction storage and retrieval
struct MyElectricityAdapter;

#[async_trait]
impl EFNUtilityAdapter for MyElectricityAdapter {
    async fn validate_customer(&self, req: ValidateRequest) -> ValidateResponse {
        // TODO: Query your utility database for req.customer_ref (meter number / account ID)
        println!(
            "[validate] checking meter: {} category: {}",
            req.customer_ref, req.utility_category
        );

        // Example: hardcoded lookup — replace with real DB query
        if req.customer_ref == "12345678901" {
            return ValidateResponse {
                is_valid: true,
                customer_name: Some("Emeka Chukwu".to_string()),
                customer_address: Some("22 Adeola Odeku, Victoria Island, Lagos".to_string()),
                minimum_amount: 500.0,
                outstanding_balance: 0.0,
            };
        }

        ValidateResponse {
            is_valid: false,
            customer_name: None,
            customer_address: None,
            minimum_amount: 0.0,
            outstanding_balance: 0.0,
        }
    }

    async fn dispense_value(&self, req: DispenseRequest) -> DispenseResponse {
        // TODO: Generate your value token here
        // For electricity: generate a 20-digit STS token
        // For water/gas: generate a vend voucher
        // For cable TV: activate subscription via your billing API
        println!(
            "[dispense] meter: {} amount: {} {} ref: {}",
            req.customer_ref, req.amount, req.currency, req.efn_reference
        );

        // Example: dummy token — replace with real STS/vend generation
        let units = req.amount / 80.0; // NGN 80 per kWh example tariff
        let mut receipt = HashMap::new();
        receipt.insert("units".to_string(), format!("{:.2} kWh", units));
        receipt.insert("tariff".to_string(), "NGN 80/kWh".to_string());
        receipt.insert("tax".to_string(), "0 NGN".to_string());

        DispenseResponse {
            status: "success".to_string(),
            dispense_ref: Some(format!("UTL-{}", &req.efn_reference[..8.min(req.efn_reference.len())])),
            value_token: Some("4512-6773-9901-2233-4455".to_string()),
            receipt_details: receipt,
            error: None,
        }
    }

    async fn transaction_status(&self, efn_reference: String) -> TransactionStatusResponse {
        // TODO: Look up the transaction in your DB by efn_reference
        // Return the stored token if found, or an appropriate status
        println!("[status] querying ref: {}", efn_reference);

        TransactionStatusResponse {
            status: "success".to_string(),
            value_token: Some("4512-6773-9901-2233-4455".to_string()),
        }
    }
}

#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive("efn_utility_adapter=info".parse().unwrap()),
        )
        .init();

    let secret = std::env::var("EFN_API_SECRET")
        .expect("EFN_API_SECRET environment variable must be set");

    let adapter = Arc::new(MyElectricityAdapter);
    let app = make_router(adapter, secret);

    let bind_addr = std::env::var("BIND_ADDR").unwrap_or_else(|_| "0.0.0.0:8080".to_string());
    let listener = tokio::net::TcpListener::bind(&bind_addr)
        .await
        .expect("Failed to bind listener");

    tracing::info!("EFN Utility Adapter listening on {}", bind_addr);
    tracing::info!("Endpoints:");
    tracing::info!("  POST /efn/v1/utility/validate");
    tracing::info!("  POST /efn/v1/utility/dispense");
    tracing::info!("  GET  /efn/v1/utility/transaction/:ref/status");

    axum::serve(listener, app)
        .await
        .expect("Server failed");
}
