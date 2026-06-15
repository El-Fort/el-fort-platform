"""
EFN Utility Adapter custom exceptions.

Raise these from your adapter implementation to communicate structured
errors back to EFN. The router will translate them into appropriate
HTTP error responses.
"""


class EFNAdapterError(Exception):
    """Base error for all EFN adapter failures."""

    def __init__(self, message: str, error_code: str = "ADAPTER_ERROR"):
        super().__init__(message)
        self.error_code = error_code
        self.message = message

    def to_dict(self):
        return {"error": self.message, "error_code": self.error_code}


class CustomerNotFoundError(EFNAdapterError):
    """Raised when customer_ref does not match any record in your system."""

    def __init__(self, customer_ref: str):
        super().__init__(
            message=f"Customer with ref '{customer_ref}' not found",
            error_code="CUSTOMER_NOT_FOUND",
        )


class DispenseFailedError(EFNAdapterError):
    """
    Raised when value dispensation fails (e.g. STS token generation failed,
    vending system is offline, or insufficient credit on gateway).
    """

    def __init__(self, reason: str):
        super().__init__(
            message=f"Value dispensation failed: {reason}",
            error_code="DISPENSE_FAILED",
        )


class DuplicateTransactionError(EFNAdapterError):
    """
    Raised when efn_reference was already processed.
    Note: Instead of raising this, consider returning the original DispenseResponse
    for true idempotency. Raise this only if the duplicate is suspicious.
    """

    def __init__(self, efn_reference: str):
        super().__init__(
            message=f"Transaction '{efn_reference}' was already processed",
            error_code="DUPLICATE_TRANSACTION",
        )


class InsufficientAmountError(EFNAdapterError):
    """Raised when the payment amount is below the minimum for this utility."""

    def __init__(self, minimum: float, currency: str):
        super().__init__(
            message=f"Amount is below minimum of {minimum} {currency}",
            error_code="INSUFFICIENT_AMOUNT",
        )
