package adapter

// EFNBankAdapter is the interface every partner bank must implement.
type EFNBankAdapter interface {
	Authorize(req AuthorizationRequest) (AuthorizationResponse, error)
	Capture(authorizationID string, req CaptureRequest) (CaptureReversalResponse, error)
	Reverse(authorizationID string, req ReversalRequest) (CaptureReversalResponse, error)
	Debit(req DebitRequest) (DebitCreditResponse, error)
	Credit(req CreditRequest) (DebitCreditResponse, error)
	Balance(req BalanceRequest) (BalanceResponse, error)
	AccountEnquiry(req AccountEnquiryRequest) (AccountEnquiryResponse, error)
	TransactionStatus(ref string) (TransactionStatusResponse, error)
	ConsentOTP(req ConsentOTPRequest) (ConsentOTPResponse, error)
	ConsentVerify(req ConsentVerifyRequest) (ConsentVerifyResponse, error)
}
