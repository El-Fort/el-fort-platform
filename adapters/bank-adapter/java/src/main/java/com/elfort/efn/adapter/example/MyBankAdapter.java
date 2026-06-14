package com.elfort.efn.adapter.example;

import com.elfort.efn.adapter.EFNBankAdapter;
import com.elfort.efn.adapter.models.*;
import org.springframework.stereotype.Component;
import java.time.Instant;
import java.util.UUID;

/** Replace method bodies with real calls to your core banking system. */
@Component
public class MyBankAdapter implements EFNBankAdapter {

    @Override
    public AuthorizationResponse authorize(AuthorizationRequest req) {
        return new AuthorizationResponse(true, "authorized",
            "AUTH-" + UUID.randomUUID().toString().replace("-", "").substring(0, 12),
            "MYB-" + Instant.now().toEpochMilli(), "00", "Authorized");
    }

    @Override
    public CaptureReversalResponse capture(String authorizationId, CaptureRequest req) {
        return new CaptureReversalResponse(true, "completed",
            "CAP-" + authorizationId.substring(0, Math.min(8, authorizationId.length())), "00", "Captured");
    }

    @Override
    public CaptureReversalResponse reverse(String authorizationId, ReversalRequest req) {
        return new CaptureReversalResponse(true, "reversed",
            "REV-" + authorizationId.substring(0, Math.min(8, authorizationId.length())), "00", "Reversed");
    }

    @Override
    public DebitResponse debit(DebitRequest req) {
        return new DebitResponse(true, "completed",
            "MYB-" + Instant.now().toEpochMilli(),
            "DBT-" + UUID.randomUUID().toString().replace("-", "").substring(0, 12), "00", "Debit successful");
    }

    @Override
    public DebitResponse credit(DebitRequest req) {
        return new DebitResponse(true, "completed",
            "MYB-" + Instant.now().toEpochMilli(),
            "CRD-" + UUID.randomUUID().toString().replace("-", "").substring(0, 12), "00", "Credit successful");
    }

    @Override
    public BalanceResponse balance(BalanceRequest req) {
        return new BalanceResponse(true, req.uan, 150000.00, "NGN", "", "00");
    }

    @Override
    public AccountEnquiryResponse accountEnquiry(AccountEnquiryRequest req) {
        return new AccountEnquiryResponse(true, req.uan, "JOHN DOE", "NGN", "7821", "00", "Account found");
    }

    @Override
    public TransactionStatusResponse transactionStatus(String ref) {
        return new TransactionStatusResponse(true, "completed", ref, "00", "");
    }

    @Override
    public ConsentOTPResponse consentOtp(ConsentOTPRequest req) {
        return new ConsentOTPResponse(true, "sent", "", "00", "OTP sent to registered phone");
    }

    @Override
    public ConsentVerifyResponse consentVerify(ConsentVerifyRequest req) {
        return new ConsentVerifyResponse(true, "verified", "", "00", "OTP verified");
    }
}
