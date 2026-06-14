use crate::models::*;

pub trait EFNBankAdapter: Send + Sync {
    fn authorize(&self, req: AuthorizationRequest) -> Result<AuthorizationResponse, String>;
    fn capture(&self, authorization_id: &str, req: CaptureRequest) -> Result<CaptureReversalResponse, String>;
    fn reverse(&self, authorization_id: &str, req: ReversalRequest) -> Result<CaptureReversalResponse, String>;
    fn debit(&self, req: DebitRequest) -> Result<DebitCreditResponse, String>;
    fn credit(&self, req: CreditRequest) -> Result<DebitCreditResponse, String>;
    fn balance(&self, req: BalanceRequest) -> Result<BalanceResponse, String>;
    fn account_enquiry(&self, req: AccountEnquiryRequest) -> Result<AccountEnquiryResponse, String>;
    fn transaction_status(&self, ref_: &str) -> Result<TransactionStatusResponse, String>;
    fn consent_otp(&self, req: ConsentOTPRequest) -> Result<ConsentOTPResponse, String>;
    fn consent_verify(&self, req: ConsentVerifyRequest) -> Result<ConsentVerifyResponse, String>;
}
