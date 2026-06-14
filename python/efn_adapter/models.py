from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthorizationRequest:
    uan: str
    amount: float
    currency: str
    efn_reference: str
    auth_method: str
    biometric_hash: Optional[str] = None
    pin_hash: Optional[str] = None
    terminal_id: Optional[str] = None
    gps: Optional[str] = None


@dataclass
class CaptureRequest:
    authorization_id: str
    amount: float
    efn_reference: str


@dataclass
class ReversalRequest:
    authorization_id: str
    efn_reference: str
    reason: Optional[str] = None


@dataclass
class DebitRequest:
    uan: str
    amount: float
    currency: str
    tx_ref: str
    efn_reference: str
    narration: Optional[str] = None


@dataclass
class CreditRequest:
    uan: str
    amount: float
    currency: str
    tx_ref: str
    efn_reference: str
    narration: Optional[str] = None


@dataclass
class BalanceRequest:
    uan: str


@dataclass
class AccountEnquiryRequest:
    uan: str


@dataclass
class ConsentOTPRequest:
    uan: str
    purpose: str


@dataclass
class ConsentVerifyRequest:
    uan: str
    otp: str
    purpose: str


@dataclass
class AuthorizationResponse:
    success: bool
    status: str  # "authorized" | "failed"
    authorization_id: str
    bank_reference: str
    response_code: str
    message: str


@dataclass
class CaptureReversalResponse:
    success: bool
    status: str  # "completed" | "reversed" | "failed"
    bank_reference: str
    response_code: str
    message: str


@dataclass
class DebitCreditResponse:
    success: bool
    status: str  # "completed" | "failed"
    bank_reference: str
    tx_ref: str
    response_code: str
    message: str


@dataclass
class BalanceResponse:
    success: bool
    uan: str
    balance: float
    currency: str
    account_number: str
    response_code: str


@dataclass
class AccountEnquiryResponse:
    success: bool
    account_number: str
    account_name: str
    currency: str
    phone_last4: str
    response_code: str
    message: str


@dataclass
class TransactionStatusResponse:
    success: bool
    status: str
    bank_reference: str
    response_code: str
    message: str


@dataclass
class ConsentOTPResponse:
    success: bool
    message: str
    response_code: str


@dataclass
class ConsentVerifyResponse:
    success: bool
    verified: bool
    message: str
    response_code: str
