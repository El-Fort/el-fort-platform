from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class ValidateRequest:
    customer_ref: str
    utility_category: str

@dataclass
class ValidateResponse:
    is_valid: bool
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    minimum_amount: float = 0.0
    outstanding_balance: float = 0.0

@dataclass
class DispenseRequest:
    customer_ref: str
    amount: float
    currency: str
    efn_reference: str

@dataclass
class DispenseResponse:
    status: str
    dispense_ref: Optional[str] = None
    value_token: Optional[str] = None
    receipt_details: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class TransactionStatusResponse:
    status: str
    value_token: Optional[str] = None
