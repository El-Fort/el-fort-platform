using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace EfnUtilityAdapter.Models;

/// <summary>
/// Request sent by EFN to validate a customer account or meter number
/// before the customer is allowed to pay.
/// </summary>
public record ValidateRequest(
    [property: JsonPropertyName("customer_ref")] string CustomerRef,
    [property: JsonPropertyName("utility_category")] string UtilityCategory
);

/// <summary>
/// Response from the adapter after validating a customer.
/// If <see cref="IsValid"/> is false, EFN will not proceed with payment.
/// </summary>
public record ValidateResponse(
    [property: JsonPropertyName("is_valid")] bool IsValid,
    [property: JsonPropertyName("customer_name")] string? CustomerName = null,
    [property: JsonPropertyName("customer_address")] string? CustomerAddress = null,
    [property: JsonPropertyName("minimum_amount")] double MinimumAmount = 0,
    [property: JsonPropertyName("outstanding_balance")] double OutstandingBalance = 0
);

/// <summary>
/// Request sent by EFN to dispense value after payment is confirmed.
/// Use <see cref="EfnReference"/> as an idempotency key.
/// </summary>
public record DispenseRequest(
    [property: JsonPropertyName("customer_ref")] string CustomerRef,
    [property: JsonPropertyName("amount")] double Amount,
    [property: JsonPropertyName("currency")] string Currency,
    [property: JsonPropertyName("efn_reference")] string EfnReference,
    [property: JsonPropertyName("idempotency_key")] string? IdempotencyKey = null
);

/// <summary>
/// Response returned after value is dispensed.
/// Must include a <see cref="ValueToken"/> (e.g. STS electricity token, voucher code).
/// </summary>
public record DispenseResponse(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("dispense_ref")] string? DispenseRef = null,
    [property: JsonPropertyName("value_token")] string? ValueToken = null,
    [property: JsonPropertyName("receipt_details")] Dictionary<string, string>? ReceiptDetails = null,
    [property: JsonPropertyName("error")] string? Error = null,
    [property: JsonPropertyName("error_code")] string? ErrorCode = null
);

/// <summary>
/// Response returned when querying a previous transaction's status.
/// </summary>
public record TransactionStatusResponse(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("value_token")] string? ValueToken = null
);
