import abc
from .models import *

class EFNUtilityAdapter(abc.ABC):
    @abc.abstractmethod
    def validate_customer(self, req: ValidateRequest) -> ValidateResponse:
        pass

    @abc.abstractmethod
    def dispense_value(self, req: DispenseRequest) -> DispenseResponse:
        pass

    @abc.abstractmethod
    def transaction_status(self, efn_reference: str) -> TransactionStatusResponse:
        pass
