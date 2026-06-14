
import { ValidateRequest, ValidateResponse, DispenseRequest, DispenseResponse, TransactionStatusResponse } from './types';

export abstract class EFNUtilityAdapter {
    abstract validateCustomer(req: ValidateRequest): Promise<ValidateResponse>;
    abstract dispenseValue(req: DispenseRequest): Promise<DispenseResponse>;
    abstract transactionStatus(efnReference: string): Promise<TransactionStatusResponse>;
}
