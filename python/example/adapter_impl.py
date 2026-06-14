"""Example implementation of EFNBankAdapter for a hypothetical bank."""
import uuid
from efn_adapter import (
    EFNBankAdapter,
    AuthorizationRequest, AuthorizationResponse,
    CaptureRequest, ReversalRequest, CaptureReversalResponse,
    DebitRequest, CreditRequest, DebitCreditResponse,
    BalanceRequest, BalanceResponse,
    AccountEnquiryRequest, AccountEnquiryResponse,
    TransactionStatusResponse,
    ConsentOTPRequest, ConsentOTPResponse,
    ConsentVerifyRequest, ConsentVerifyResponse,
)


class MyBankAdapter(EFNBankAdapter):
    def authorize(self, req: AuthorizationRequest) -> AuthorizationResponse:
        return AuthorizationResponse(
            success=True,
            status="authorized",
            authorization_id=str(uuid.uuid4()),
            bank_reference="BNK-" + str(uuid.uuid4())[:8].upper(),
            response_code="00",
            message="Authorization successful",
        )

    def capture(self, authorization_id: str, req: CaptureRequest) -> CaptureReversalResponse:
        return CaptureReversalResponse(
            success=True, status="completed",
            bank_reference="BNK-" + str(uuid.uuid4())[:8].upper(),
            response_code="00", message="Capture successful",
        )

    def reverse(self, authorization_id: str, req: ReversalRequest) -> CaptureReversalResponse:
        return CaptureReversalResponse(
            success=True, status="reversed",
            bank_reference="BNK-" + str(uuid.uuid4())[:8].upper(),
            response_code="00", message="Reversal successful",
        )

    def debit(self, req: DebitRequest) -> DebitCreditResponse:
        return DebitCreditResponse(
            success=True, status="completed",
            bank_reference="BNK-" + str(uuid.uuid4())[:8].upper(),
            tx_ref=req.tx_ref, response_code="00", message="Debit successful",
        )

    def credit(self, req: CreditRequest) -> DebitCreditResponse:
        return DebitCreditResponse(
            success=True, status="completed",
            bank_reference="BNK-" + str(uuid.uuid4())[:8].upper(),
            tx_ref=req.tx_ref, response_code="00", message="Credit successful",
        )

    def balance(self, req: BalanceRequest) -> BalanceResponse:
        return BalanceResponse(
            success=True, uan=req.uan, balance=50000.00,
            currency="NGN", account_number="0123456789", response_code="00",
        )

    def account_enquiry(self, req: AccountEnquiryRequest) -> AccountEnquiryResponse:
        return AccountEnquiryResponse(
            success=True, account_number="0123456789",
            account_name="John Doe", currency="NGN",
            phone_last4="7890", response_code="00", message="OK",
        )

    def transaction_status(self, ref: str) -> TransactionStatusResponse:
        return TransactionStatusResponse(
            success=True, status="completed",
            bank_reference="BNK-" + ref[:8].upper(),
            response_code="00", message="Transaction found",
        )

    def consent_otp(self, req: ConsentOTPRequest) -> ConsentOTPResponse:
        return ConsentOTPResponse(success=True, message="OTP sent", response_code="00")

    def consent_verify(self, req: ConsentVerifyRequest) -> ConsentVerifyResponse:
        return ConsentVerifyResponse(
            success=True, verified=True, message="Consent verified", response_code="00",
        )
