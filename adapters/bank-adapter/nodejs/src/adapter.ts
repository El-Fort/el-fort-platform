import {
  AuthorizationRequest, AuthorizationResponse,
  CaptureRequest, ReversalRequest, CaptureReversalResponse,
  DebitRequest, CreditRequest, DebitCreditResponse,
  BalanceRequest, BalanceResponse,
  AccountEnquiryRequest, AccountEnquiryResponse,
  TransactionStatusResponse,
  ConsentOTPRequest, ConsentOTPResponse,
  ConsentVerifyRequest, ConsentVerifyResponse,
} from "./types";

export interface EFNBankAdapter {
  authorize(req: AuthorizationRequest): Promise<AuthorizationResponse>;
  capture(authorizationId: string, req: CaptureRequest): Promise<CaptureReversalResponse>;
  reverse(authorizationId: string, req: ReversalRequest): Promise<CaptureReversalResponse>;
  debit(req: DebitRequest): Promise<DebitCreditResponse>;
  credit(req: CreditRequest): Promise<DebitCreditResponse>;
  balance(req: BalanceRequest): Promise<BalanceResponse>;
  accountEnquiry(req: AccountEnquiryRequest): Promise<AccountEnquiryResponse>;
  transactionStatus(ref: string): Promise<TransactionStatusResponse>;
  consentOtp(req: ConsentOTPRequest): Promise<ConsentOTPResponse>;
  consentVerify(req: ConsentVerifyRequest): Promise<ConsentVerifyResponse>;
}
