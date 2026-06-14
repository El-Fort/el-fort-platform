from abc import ABC, abstractmethod
from .models import (
    AuthorizationRequest, AuthorizationResponse,
    CaptureRequest, CaptureReversalResponse,
    ReversalRequest, DebitRequest, CreditRequest, DebitCreditResponse,
    BalanceRequest, BalanceResponse,
    AccountEnquiryRequest, AccountEnquiryResponse,
    TransactionStatusResponse, ConsentOTPRequest, ConsentOTPResponse,
    ConsentVerifyRequest, ConsentVerifyResponse,
)


class EFNBankAdapter(ABC):
    """Abstract base class. Implement all methods to integrate your bank with EFN."""

    @abstractmethod
    def authorize(self, req: AuthorizationRequest) -> AuthorizationResponse: ...

    @abstractmethod
    def capture(self, authorization_id: str, req: CaptureRequest) -> CaptureReversalResponse: ...

    @abstractmethod
    def reverse(self, authorization_id: str, req: ReversalRequest) -> CaptureReversalResponse: ...

    @abstractmethod
    def debit(self, req: DebitRequest) -> DebitCreditResponse: ...

    @abstractmethod
    def credit(self, req: CreditRequest) -> DebitCreditResponse: ...

    @abstractmethod
    def balance(self, req: BalanceRequest) -> BalanceResponse: ...

    @abstractmethod
    def account_enquiry(self, req: AccountEnquiryRequest) -> AccountEnquiryResponse: ...

    @abstractmethod
    def transaction_status(self, ref: str) -> TransactionStatusResponse: ...

    @abstractmethod
    def consent_otp(self, req: ConsentOTPRequest) -> ConsentOTPResponse: ...

    @abstractmethod
    def consent_verify(self, req: ConsentVerifyRequest) -> ConsentVerifyResponse: ...
