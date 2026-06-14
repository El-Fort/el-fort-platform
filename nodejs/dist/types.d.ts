export interface AuthorizationRequest {
    uan: string;
    amount: number;
    currency: string;
    efn_reference: string;
    auth_method: string;
    biometric_hash?: string;
    pin_hash?: string;
    terminal_id?: string;
    gps?: string;
}
export interface CaptureRequest {
    authorization_id: string;
    amount: number;
    efn_reference: string;
}
export interface ReversalRequest {
    authorization_id: string;
    efn_reference: string;
    reason?: string;
}
export interface DebitRequest {
    uan: string;
    amount: number;
    currency: string;
    tx_ref: string;
    efn_reference: string;
    narration?: string;
}
export interface CreditRequest {
    uan: string;
    amount: number;
    currency: string;
    tx_ref: string;
    efn_reference: string;
    narration?: string;
}
export interface BalanceRequest {
    uan: string;
}
export interface AccountEnquiryRequest {
    uan: string;
}
export interface ConsentOTPRequest {
    uan: string;
    purpose: string;
}
export interface ConsentVerifyRequest {
    uan: string;
    otp: string;
    purpose: string;
}
export interface AuthorizationResponse {
    success: boolean;
    status: "authorized" | "failed";
    authorization_id: string;
    bank_reference: string;
    response_code: string;
    message: string;
}
export interface CaptureReversalResponse {
    success: boolean;
    status: "completed" | "reversed" | "failed";
    bank_reference: string;
    response_code: string;
    message: string;
}
export interface DebitCreditResponse {
    success: boolean;
    status: "completed" | "failed";
    bank_reference: string;
    tx_ref: string;
    response_code: string;
    message: string;
}
export interface BalanceResponse {
    success: boolean;
    uan: string;
    balance: number;
    currency: string;
    account_number: string;
    response_code: string;
}
export interface AccountEnquiryResponse {
    success: boolean;
    account_number: string;
    account_name: string;
    currency: string;
    phone_last4: string;
    response_code: string;
    message: string;
}
export interface TransactionStatusResponse {
    success: boolean;
    status: string;
    bank_reference: string;
    response_code: string;
    message: string;
}
export interface ConsentOTPResponse {
    success: boolean;
    message: string;
    response_code: string;
}
export interface ConsentVerifyResponse {
    success: boolean;
    verified: boolean;
    message: string;
    response_code: string;
}
//# sourceMappingURL=types.d.ts.map