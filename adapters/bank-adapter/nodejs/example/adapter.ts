import { randomUUID } from "crypto";
import { EFNBankAdapter } from "../src/adapter";
import {
  AuthorizationRequest, AuthorizationResponse,
  CaptureRequest, ReversalRequest, CaptureReversalResponse,
  DebitRequest, CreditRequest, DebitCreditResponse,
  BalanceRequest, BalanceResponse,
  AccountEnquiryRequest, AccountEnquiryResponse,
  TransactionStatusResponse,
  ConsentOTPRequest, ConsentOTPResponse,
  ConsentVerifyRequest, ConsentVerifyResponse,
} from "../src/types";
import express from "express";
import { makeRouter } from "../src/router";

class MyBankAdapter implements EFNBankAdapter {
  async authorize(_req: AuthorizationRequest): Promise<AuthorizationResponse> {
    return {
      success: true, status: "authorized",
      authorization_id: randomUUID(),
      bank_reference: "BNK-" + randomUUID().slice(0, 8).toUpperCase(),
      response_code: "00", message: "Authorization successful",
    };
  }

  async capture(_id: string, _req: CaptureRequest): Promise<CaptureReversalResponse> {
    return {
      success: true, status: "completed",
      bank_reference: "BNK-" + randomUUID().slice(0, 8).toUpperCase(),
      response_code: "00", message: "Capture successful",
    };
  }

  async reverse(_id: string, _req: ReversalRequest): Promise<CaptureReversalResponse> {
    return {
      success: true, status: "reversed",
      bank_reference: "BNK-" + randomUUID().slice(0, 8).toUpperCase(),
      response_code: "00", message: "Reversal successful",
    };
  }

  async debit(req: DebitRequest): Promise<DebitCreditResponse> {
    return {
      success: true, status: "completed",
      bank_reference: "BNK-" + randomUUID().slice(0, 8).toUpperCase(),
      tx_ref: req.tx_ref, response_code: "00", message: "Debit successful",
    };
  }

  async credit(req: CreditRequest): Promise<DebitCreditResponse> {
    return {
      success: true, status: "completed",
      bank_reference: "BNK-" + randomUUID().slice(0, 8).toUpperCase(),
      tx_ref: req.tx_ref, response_code: "00", message: "Credit successful",
    };
  }

  async balance(req: BalanceRequest): Promise<BalanceResponse> {
    return {
      success: true, uan: req.uan, balance: 50000.00,
      currency: "NGN", account_number: "0123456789", response_code: "00",
    };
  }

  async accountEnquiry(_req: AccountEnquiryRequest): Promise<AccountEnquiryResponse> {
    return {
      success: true, account_number: "0123456789", account_name: "John Doe",
      currency: "NGN", phone_last4: "7890", response_code: "00", message: "OK",
    };
  }

  async transactionStatus(ref: string): Promise<TransactionStatusResponse> {
    return {
      success: true, status: "completed",
      bank_reference: "BNK-" + ref.slice(0, 8).toUpperCase(),
      response_code: "00", message: "Transaction found",
    };
  }

  async consentOtp(_req: ConsentOTPRequest): Promise<ConsentOTPResponse> {
    return { success: true, message: "OTP sent", response_code: "00" };
  }

  async consentVerify(_req: ConsentVerifyRequest): Promise<ConsentVerifyResponse> {
    return { success: true, verified: true, message: "Consent verified", response_code: "00" };
  }
}

const app = express();
app.use("/efn/v1", makeRouter(new MyBankAdapter(), process.env.EFN_API_SECRET ?? "dev-secret"));
app.listen(3000, () => console.log("EFN adapter listening on :3000"));
