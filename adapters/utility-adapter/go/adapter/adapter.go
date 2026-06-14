package adapter
import "context"
type EFNUtilityAdapter interface {
    ValidateCustomer(ctx context.Context, req ValidateRequest) (*ValidateResponse, error)
    DispenseValue(ctx context.Context, req DispenseRequest) (*DispenseResponse, error)
    TransactionStatus(ctx context.Context, efnReference string) (*TransactionStatusResponse, error)
}
