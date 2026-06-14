package adapter
type ValidateRequest struct { CustomerRef string `json:"customer_ref"`; UtilityCategory string `json:"utility_category"` }
type ValidateResponse struct { IsValid bool `json:"is_valid"`; CustomerName string `json:"customer_name,omitempty"`; CustomerAddress string `json:"customer_address,omitempty"`; MinimumAmount float64 `json:"minimum_amount"`; OutstandingBalance float64 `json:"outstanding_balance"` }
type DispenseRequest struct { CustomerRef string `json:"customer_ref"`; Amount float64 `json:"amount"`; Currency string `json:"currency"`; EfnReference string `json:"efn_reference"` }
type DispenseResponse struct { Status string `json:"status"`; DispenseRef string `json:"dispense_ref,omitempty"`; ValueToken string `json:"value_token,omitempty"`; ReceiptDetails map[string]string `json:"receipt_details"`; Error string `json:"error,omitempty"` }
type TransactionStatusResponse struct { Status string `json:"status"`; ValueToken string `json:"value_token,omitempty"` }
