
export interface ValidateRequest {
    customer_ref: string;
    utility_category: string;
}
export interface ValidateResponse {
    is_valid: boolean;
    customer_name?: string;
    customer_address?: string;
    minimum_amount: number;
    outstanding_balance: number;
}
export interface DispenseRequest {
    customer_ref: string;
    amount: number;
    currency: string;
    efn_reference: string;
}
export interface DispenseResponse {
    status: string;
    dispense_ref?: string;
    value_token?: string;
    receipt_details: Record<string, string>;
    error?: string;
}
export interface TransactionStatusResponse {
    status: string;
    value_token?: string;
}
