namespace EfnAdapter;

public interface IEfnBankAdapter
{
    Task<AuthorizationResponse> AuthorizeAsync(AuthorizationRequest req);
    Task<CaptureResponse>       CaptureAsync(string authorizationId, AuthorizationRequest req);
    Task<CaptureResponse>       ReverseAsync(string authorizationId, AuthorizationRequest req);
    Task<DebitResponse>         DebitAsync(DebitRequest req);
    Task<DebitResponse>         CreditAsync(CreditRequest req);
    Task<BalanceResponse>       BalanceAsync(BalanceRequest req);
    Task<AccountEnquiryResponse> AccountEnquiryAsync(AccountEnquiryRequest req);
    Task<TransactionStatusResponse> TransactionStatusAsync(string efnReference);
    Task<object>                ConsentOtpAsync(ConsentOtpRequest req);
    Task<object>                ConsentVerifyAsync(ConsentVerifyRequest req);
}
