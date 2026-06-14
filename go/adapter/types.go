package adapter

// ---- Requests ----

type AuthorizationRequest struct {
	UAN           string  `json:"uan"`
	Amount        float64 `json:"amount"`
	Currency      string  `json:"currency"`
	EFNReference  string  `json:"efn_reference"`
	AuthMethod    string  `json:"auth_method"`
	BiometricHash string  `json:"biometric_hash,omitempty"`
	PINHash       string  `json:"pin_hash,omitempty"`
	TerminalID    string  `json:"terminal_id,omitempty"`
	GPS           string  `json:"gps,omitempty"`
}

type CaptureRequest struct {
	AuthorizationID string  `json:"authorization_id"`
	Amount          float64 `json:"amount"`
	EFNReference    string  `json:"efn_reference"`
}

type ReversalRequest struct {
	AuthorizationID string `json:"authorization_id"`
	EFNReference    string `json:"efn_reference"`
	Reason          string `json:"reason,omitempty"`
}

type DebitRequest struct {
	UAN          string  `json:"uan"`
	Amount       float64 `json:"amount"`
	Currency     string  `json:"currency"`
	TxRef        string  `json:"tx_ref"`
	EFNReference string  `json:"efn_reference"`
	Narration    string  `json:"narration,omitempty"`
}

type CreditRequest struct {
	UAN          string  `json:"uan"`
	Amount       float64 `json:"amount"`
	Currency     string  `json:"currency"`
	TxRef        string  `json:"tx_ref"`
	EFNReference string  `json:"efn_reference"`
	Narration    string  `json:"narration,omitempty"`
}

type BalanceRequest struct {
	UAN string `json:"uan"`
}

type AccountEnquiryRequest struct {
	UAN string `json:"uan"`
}

type ConsentOTPRequest struct {
	UAN     string `json:"uan"`
	Purpose string `json:"purpose"`
}

type ConsentVerifyRequest struct {
	UAN     string `json:"uan"`
	OTP     string `json:"otp"`
	Purpose string `json:"purpose"`
}

// ---- Responses ----

type AuthorizationResponse struct {
	Success         bool   `json:"success"`
	Status          string `json:"status"`
	AuthorizationID string `json:"authorization_id"`
	BankReference   string `json:"bank_reference"`
	ResponseCode    string `json:"response_code"`
	Message         string `json:"message"`
}

type CaptureReversalResponse struct {
	Success       bool   `json:"success"`
	Status        string `json:"status"`
	BankReference string `json:"bank_reference"`
	ResponseCode  string `json:"response_code"`
	Message       string `json:"message"`
}

type DebitCreditResponse struct {
	Success       bool   `json:"success"`
	Status        string `json:"status"`
	BankReference string `json:"bank_reference"`
	TxRef         string `json:"tx_ref"`
	ResponseCode  string `json:"response_code"`
	Message       string `json:"message"`
}

type BalanceResponse struct {
	Success       bool    `json:"success"`
	UAN           string  `json:"uan"`
	Balance       float64 `json:"balance"`
	Currency      string  `json:"currency"`
	AccountNumber string  `json:"account_number"`
	ResponseCode  string  `json:"response_code"`
}

type AccountEnquiryResponse struct {
	Success       bool   `json:"success"`
	AccountNumber string `json:"account_number"`
	AccountName   string `json:"account_name"`
	Currency      string `json:"currency"`
	PhoneLast4    string `json:"phone_last4"`
	ResponseCode  string `json:"response_code"`
	Message       string `json:"message"`
}

type TransactionStatusResponse struct {
	Success       bool   `json:"success"`
	Status        string `json:"status"`
	BankReference string `json:"bank_reference"`
	ResponseCode  string `json:"response_code"`
	Message       string `json:"message"`
}

type ConsentOTPResponse struct {
	Success      bool   `json:"success"`
	Message      string `json:"message"`
	ResponseCode string `json:"response_code"`
}

type ConsentVerifyResponse struct {
	Success      bool   `json:"success"`
	Verified     bool   `json:"verified"`
	Message      string `json:"message"`
	ResponseCode string `json:"response_code"`
}
