from efn_utility_adapter import EFNUtilityAdapter, ValidateRequest, ValidateResponse, DispenseRequest, DispenseResponse, TransactionStatusResponse

class MyUtilityAdapter(EFNUtilityAdapter):
    def validate_customer(self, req: ValidateRequest) -> ValidateResponse:
        if req.customer_ref == "123":
            return ValidateResponse(is_valid=True, customer_name="Test User")
        return ValidateResponse(is_valid=False)

    def dispense_value(self, req: DispenseRequest) -> DispenseResponse:
        return DispenseResponse(status="success", dispense_ref="REF123", value_token="1122-3344", receipt_details={"units": "50.0"})

    def transaction_status(self, efn_reference: str) -> TransactionStatusResponse:
        return TransactionStatusResponse(status="success", value_token="1122-3344")
