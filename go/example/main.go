package main

import (
	"fmt"
	"net/http"
	"os"

	"github.com/elfort/efn-bank-adapter/adapter"
	"github.com/google/uuid"
)

type MyBankAdapter struct{}

func (b *MyBankAdapter) Authorize(req adapter.AuthorizationRequest) (adapter.AuthorizationResponse, error) {
	return adapter.AuthorizationResponse{
		Success: true, Status: "authorized",
		AuthorizationID: uuid.NewString(),
		BankReference:   "BNK-" + uuid.NewString()[:8],
		ResponseCode:    "00", Message: "Authorization successful",
	}, nil
}

func (b *MyBankAdapter) Capture(id string, req adapter.CaptureRequest) (adapter.CaptureReversalResponse, error) {
	return adapter.CaptureReversalResponse{
		Success: true, Status: "completed",
		BankReference: "BNK-" + uuid.NewString()[:8],
		ResponseCode:  "00", Message: "Capture successful",
	}, nil
}

func (b *MyBankAdapter) Reverse(id string, req adapter.ReversalRequest) (adapter.CaptureReversalResponse, error) {
	return adapter.CaptureReversalResponse{
		Success: true, Status: "reversed",
		BankReference: "BNK-" + uuid.NewString()[:8],
		ResponseCode:  "00", Message: "Reversal successful",
	}, nil
}

func (b *MyBankAdapter) Debit(req adapter.DebitRequest) (adapter.DebitCreditResponse, error) {
	return adapter.DebitCreditResponse{
		Success: true, Status: "completed",
		BankReference: "BNK-" + uuid.NewString()[:8],
		TxRef:         req.TxRef, ResponseCode: "00", Message: "Debit successful",
	}, nil
}

func (b *MyBankAdapter) Credit(req adapter.CreditRequest) (adapter.DebitCreditResponse, error) {
	return adapter.DebitCreditResponse{
		Success: true, Status: "completed",
		BankReference: "BNK-" + uuid.NewString()[:8],
		TxRef:         req.TxRef, ResponseCode: "00", Message: "Credit successful",
	}, nil
}

func (b *MyBankAdapter) Balance(req adapter.BalanceRequest) (adapter.BalanceResponse, error) {
	return adapter.BalanceResponse{
		Success: true, UAN: req.UAN, Balance: 50000.00,
		Currency: "NGN", AccountNumber: "0123456789", ResponseCode: "00",
	}, nil
}

func (b *MyBankAdapter) AccountEnquiry(req adapter.AccountEnquiryRequest) (adapter.AccountEnquiryResponse, error) {
	return adapter.AccountEnquiryResponse{
		Success: true, AccountNumber: "0123456789", AccountName: "John Doe",
		Currency: "NGN", PhoneLast4: "7890", ResponseCode: "00", Message: "OK",
	}, nil
}

func (b *MyBankAdapter) TransactionStatus(ref string) (adapter.TransactionStatusResponse, error) {
	return adapter.TransactionStatusResponse{
		Success: true, Status: "completed",
		BankReference: "BNK-" + ref[:8],
		ResponseCode:  "00", Message: "Transaction found",
	}, nil
}

func (b *MyBankAdapter) ConsentOTP(req adapter.ConsentOTPRequest) (adapter.ConsentOTPResponse, error) {
	return adapter.ConsentOTPResponse{Success: true, Message: "OTP sent", ResponseCode: "00"}, nil
}

func (b *MyBankAdapter) ConsentVerify(req adapter.ConsentVerifyRequest) (adapter.ConsentVerifyResponse, error) {
	return adapter.ConsentVerifyResponse{
		Success: true, Verified: true, Message: "Consent verified", ResponseCode: "00",
	}, nil
}

func main() {
	secret := os.Getenv("EFN_API_SECRET")
	if secret == "" {
		secret = "dev-secret"
	}
	h := adapter.NewRouter(&MyBankAdapter{}, secret)
	fmt.Println("EFN adapter listening on :8080")
	http.ListenAndServe(":8080", h)
}
