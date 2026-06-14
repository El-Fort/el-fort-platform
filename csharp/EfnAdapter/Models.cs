namespace EfnAdapter;

public record AuthorizationRequest(
    string EfnReference, string Uan, string SourceAccountNumber, string SourceAccountName,
    string SourceBankCode, string RecipientAccountNumber, string RecipientBankCode,
    string RecipientName, string Amount, string Currency, string Description,
    string AuthMethod, bool BiometricVerified, string TerminalId, string Nonce,
    string Purpose, string? GpsLat = null, string? GpsLng = null,
    string IdempotencyKey = "");

public record DebitRequest(
    string EfnReference, string Uan, string MerchantId, string Amount, string Currency,
    string Description = "EFN Subscription Debit", string SubscriptionId = "",
    string IdempotencyKey = "");

public record CreditRequest(
    string EfnReference, string Uan, string Amount, string Currency,
    string Description, string IdempotencyKey = "");

public record BalanceRequest(string Uan, string AccountNumber = "");

public record AccountEnquiryRequest(string AccountNumber, string BankCode = "");

public record ConsentOtpRequest(string AccountNumber, string BankCode = "");
public record ConsentVerifyRequest(string AccountNumber, string Otp);

// Responses
public record AuthorizationResponse(
    bool Success, string Status, string AuthorizationId = "",
    string BankReference = "", string ResponseCode = "00", string Message = "Success");

public record CaptureResponse(
    bool Success, string Status, string BankReference = "",
    string ResponseCode = "00", string Message = "Success");

public record DebitResponse(
    bool Success, string Status, string BankReference = "", string TxRef = "",
    string ResponseCode = "00", string Message = "Success");

public record BalanceResponse(
    bool Success, string Uan, string Balance, string Currency,
    string AccountNumber = "", string ResponseCode = "00");

public record AccountEnquiryResponse(
    bool Success, string AccountNumber, string AccountName, string Currency = "NGN",
    string PhaseLast4 = "", string ResponseCode = "00", string Message = "Account found");

public record TransactionStatusResponse(
    bool Success, string Status, string BankReference = "",
    string ResponseCode = "00", string Message = "");
