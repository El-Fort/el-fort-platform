using EfnUtilityAdapter.Models;

namespace EfnUtilityAdapter;

/// <summary>
/// Core interface that every EFN Utility Provider Adapter must implement.
/// </summary>
/// <remarks>
/// Integration flow:
/// <code>
/// EFN Smart Terminal
///        │ HMAC-signed HTTP request
///        ▼
/// Your Adapter Server  ◄── implements IEFNUtilityAdapter
///        │ Business logic
///        ▼
/// Your Utility DB / Vending System
/// </code>
///
/// Quick start:
/// <code>
/// public class MyAdapter : IEFNUtilityAdapter {
///     public ValidateResponse ValidateCustomer(ValidateRequest req) {
///         var meter = _db.Meters.FirstOrDefault(m => m.Number == req.CustomerRef);
///         if (meter == null) return new ValidateResponse(IsValid: false);
///         return new ValidateResponse(IsValid: true, CustomerName: meter.Name, ...);
///     }
/// }
/// </code>
/// </remarks>
public interface IEFNUtilityAdapter
{
    /// <summary>
    /// Validate a customer's account or meter number before payment.
    /// Return <see cref="ValidateResponse.IsValid"/> = false to abort the transaction.
    /// </summary>
    ValidateResponse ValidateCustomer(ValidateRequest req);

    /// <summary>
    /// Dispense value (token, units, credit) after the customer pays.
    /// This method must be idempotent — use <see cref="DispenseRequest.EfnReference"/>
    /// to detect duplicate calls and return the same token safely.
    /// </summary>
    DispenseResponse DispenseValue(DispenseRequest req);

    /// <summary>
    /// Return the status and value token of a previous dispense transaction.
    /// Used for reconciliation and retry flows.
    /// </summary>
    TransactionStatusResponse TransactionStatus(string efnReference);
}
