package com.elfort.efn.adapter;

import com.elfort.efn.adapter.models.*;

public interface EFNBankAdapter {
    AuthorizationResponse authorize(AuthorizationRequest request);
    com.elfort.efn.adapter.models.CaptureReversalResponse capture(String authorizationId, com.elfort.efn.adapter.models.CaptureRequest request);
    com.elfort.efn.adapter.models.CaptureReversalResponse reverse(String authorizationId, com.elfort.efn.adapter.models.ReversalRequest request);
    DebitResponse debit(DebitRequest request);
    DebitResponse credit(DebitRequest request);
    BalanceResponse balance(BalanceRequest request);
    AccountEnquiryResponse accountEnquiry(AccountEnquiryRequest request);
    com.elfort.efn.adapter.models.TransactionStatusResponse transactionStatus(String ref);
    com.elfort.efn.adapter.models.ConsentOTPResponse consentOtp(com.elfort.efn.adapter.models.ConsentOTPRequest request);
    com.elfort.efn.adapter.models.ConsentVerifyResponse consentVerify(com.elfort.efn.adapter.models.ConsentVerifyRequest request);
}
