using Microsoft.AspNetCore.Mvc;

namespace EfnAdapter;

[ApiController]
public class EfnAdapterController(IEfnBankAdapter adapter, EfnAdapterOptions options) : ControllerBase
{
    private bool Verify()
    {
        Request.Headers.TryGetValue("X-EFN-Timestamp", out var ts);
        Request.Headers.TryGetValue("X-EFN-Signature", out var sig);
        // Body already read via EnableBuffering middleware
        Request.Body.Position = 0;
        using var ms = new System.IO.MemoryStream();
        Request.Body.CopyTo(ms);
        return EfnSecurity.VerifySignature(options.ApiSecret, ts!, ms.ToArray(), sig!);
    }

    [HttpPost("/efn/v1/authorizations")]
    public async Task<IActionResult> Authorize([FromBody] AuthorizationRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.AuthorizeAsync(req));
    }

    [HttpPost("/efn/v1/authorizations/{authorizationId}/capture")]
    public async Task<IActionResult> Capture(string authorizationId, [FromBody] AuthorizationRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.CaptureAsync(authorizationId, req));
    }

    [HttpPost("/efn/v1/authorizations/{authorizationId}/reversal")]
    public async Task<IActionResult> Reversal(string authorizationId, [FromBody] AuthorizationRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.ReverseAsync(authorizationId, req));
    }

    [HttpPost("/efn/v1/debit")]
    public async Task<IActionResult> Debit([FromBody] DebitRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.DebitAsync(req));
    }

    [HttpPost("/efn/v1/credit")]
    public async Task<IActionResult> Credit([FromBody] CreditRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.CreditAsync(req));
    }

    [HttpPost("/efn/v1/balance")]
    public async Task<IActionResult> Balance([FromBody] BalanceRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.BalanceAsync(req));
    }

    [HttpPost("/efn/v1/account-enquiry")]
    public async Task<IActionResult> AccountEnquiry([FromBody] AccountEnquiryRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.AccountEnquiryAsync(req));
    }

    [HttpGet("/efn/v1/transaction/{efnReference}/status")]
    public async Task<IActionResult> TransactionStatus(string efnReference)
        => Ok(await adapter.TransactionStatusAsync(efnReference));

    [HttpPost("/efn/v1/consent-otp")]
    public async Task<IActionResult> ConsentOtp([FromBody] ConsentOtpRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.ConsentOtpAsync(req));
    }

    [HttpPost("/efn/v1/consent-verify")]
    public async Task<IActionResult> ConsentVerify([FromBody] ConsentVerifyRequest req)
    {
        if (!Verify()) return Unauthorized(new { success = false, message = "Invalid signature" });
        return Ok(await adapter.ConsentVerifyAsync(req));
    }

    [HttpGet("/efn/v1/health")]
    public IActionResult Health() => Ok(new { status = "ok" });
}

public class EfnAdapterOptions { public string ApiSecret { get; set; } = ""; }
