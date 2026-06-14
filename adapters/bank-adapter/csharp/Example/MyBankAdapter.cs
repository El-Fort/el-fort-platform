using EfnAdapter;

namespace Example;

/// <summary>Replace this with real calls to your core banking system.</summary>
public class MyBankAdapter : IEfnBankAdapter
{
    public Task<AuthorizationResponse> AuthorizeAsync(AuthorizationRequest req) =>
        Task.FromResult(new AuthorizationResponse(true, "authorized",
            AuthorizationId: $"AUTH-{Guid.NewGuid():N}",
            BankReference: $"MYB-{DateTime.UtcNow:yyyyMMddHHmmss}"));

    public Task<CaptureResponse> CaptureAsync(string authId, AuthorizationRequest req) =>
        Task.FromResult(new CaptureResponse(true, "completed",
            BankReference: $"CAP-{authId[..8]}"));

    public Task<CaptureResponse> ReverseAsync(string authId, AuthorizationRequest req) =>
        Task.FromResult(new CaptureResponse(true, "reversed",
            BankReference: $"REV-{authId[..8]}"));

    public Task<DebitResponse> DebitAsync(DebitRequest req) =>
        Task.FromResult(new DebitResponse(true, "completed",
            TxRef: $"DBT-{Guid.NewGuid():N}",
            BankReference: $"MYB-{DateTime.UtcNow:yyyyMMddHHmmss}"));

    public Task<DebitResponse> CreditAsync(CreditRequest req) =>
        Task.FromResult(new DebitResponse(true, "completed",
            TxRef: $"CRD-{Guid.NewGuid():N}",
            BankReference: $"MYB-{DateTime.UtcNow:yyyyMMddHHmmss}"));

    public Task<BalanceResponse> BalanceAsync(BalanceRequest req) =>
        Task.FromResult(new BalanceResponse(true, req.Uan, "150000.00", "NGN"));

    public Task<AccountEnquiryResponse> AccountEnquiryAsync(AccountEnquiryRequest req) =>
        Task.FromResult(new AccountEnquiryResponse(true, req.AccountNumber, "JOHN DOE"));

    public Task<TransactionStatusResponse> TransactionStatusAsync(string efnRef) =>
        Task.FromResult(new TransactionStatusResponse(true, "completed", Message: efnRef));

    public Task<object> ConsentOtpAsync(ConsentOtpRequest req) =>
        Task.FromResult<object>(new { success = true, message = "OTP sent" });

    public Task<object> ConsentVerifyAsync(ConsentVerifyRequest req) =>
        Task.FromResult<object>(new { success = true, message = "OTP verified" });
}
