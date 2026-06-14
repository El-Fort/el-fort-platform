use std::sync::Arc;
use efn_bank_adapter::{
    adapter::EFNBankAdapter,
    models::*,
    router::make_router,
};
use uuid::Uuid;

struct MyBankAdapter;

impl EFNBankAdapter for MyBankAdapter {
    fn authorize(&self, _req: AuthorizationRequest) -> Result<AuthorizationResponse, String> {
        Ok(AuthorizationResponse {
            success: true,
            status: "authorized".into(),
            authorization_id: Uuid::new_v4().to_string(),
            bank_reference: format!("BNK-{}", &Uuid::new_v4().to_string()[..8]),
            response_code: "00".into(),
            message: "Authorization successful".into(),
        })
    }

    fn capture(&self, _id: &str, _req: CaptureRequest) -> Result<CaptureReversalResponse, String> {
        Ok(CaptureReversalResponse {
            success: true, status: "completed".into(),
            bank_reference: format!("BNK-{}", &Uuid::new_v4().to_string()[..8]),
            response_code: "00".into(), message: "Capture successful".into(),
        })
    }

    fn reverse(&self, _id: &str, _req: ReversalRequest) -> Result<CaptureReversalResponse, String> {
        Ok(CaptureReversalResponse {
            success: true, status: "reversed".into(),
            bank_reference: format!("BNK-{}", &Uuid::new_v4().to_string()[..8]),
            response_code: "00".into(), message: "Reversal successful".into(),
        })
    }

    fn debit(&self, req: DebitRequest) -> Result<DebitCreditResponse, String> {
        Ok(DebitCreditResponse {
            success: true, status: "completed".into(),
            bank_reference: format!("BNK-{}", &Uuid::new_v4().to_string()[..8]),
            tx_ref: req.tx_ref, response_code: "00".into(), message: "Debit successful".into(),
        })
    }

    fn credit(&self, req: CreditRequest) -> Result<DebitCreditResponse, String> {
        Ok(DebitCreditResponse {
            success: true, status: "completed".into(),
            bank_reference: format!("BNK-{}", &Uuid::new_v4().to_string()[..8]),
            tx_ref: req.tx_ref, response_code: "00".into(), message: "Credit successful".into(),
        })
    }

    fn balance(&self, req: BalanceRequest) -> Result<BalanceResponse, String> {
        Ok(BalanceResponse {
            success: true, uan: req.uan, balance: 50000.0,
            currency: "NGN".into(), account_number: "0123456789".into(), response_code: "00".into(),
        })
    }

    fn account_enquiry(&self, _req: AccountEnquiryRequest) -> Result<AccountEnquiryResponse, String> {
        Ok(AccountEnquiryResponse {
            success: true, account_number: "0123456789".into(), account_name: "John Doe".into(),
            currency: "NGN".into(), phone_last4: "7890".into(), response_code: "00".into(),
            message: "OK".into(),
        })
    }

    fn transaction_status(&self, ref_: &str) -> Result<TransactionStatusResponse, String> {
        Ok(TransactionStatusResponse {
            success: true, status: "completed".into(),
            bank_reference: format!("BNK-{}", &ref_[..8.min(ref_.len())]),
            response_code: "00".into(), message: "Transaction found".into(),
        })
    }

    fn consent_otp(&self, _req: ConsentOTPRequest) -> Result<ConsentOTPResponse, String> {
        Ok(ConsentOTPResponse { success: true, message: "OTP sent".into(), response_code: "00".into() })
    }

    fn consent_verify(&self, _req: ConsentVerifyRequest) -> Result<ConsentVerifyResponse, String> {
        Ok(ConsentVerifyResponse {
            success: true, verified: true, message: "Consent verified".into(), response_code: "00".into(),
        })
    }
}

#[tokio::main]
async fn main() {
    let secret = std::env::var("EFN_API_SECRET").unwrap_or_else(|_| "dev-secret".into());
    let app = make_router(Arc::new(MyBankAdapter), secret);
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    println!("EFN adapter listening on :8080");
    axum::serve(listener, app).await.unwrap();
}
