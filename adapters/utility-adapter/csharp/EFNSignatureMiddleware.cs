using System.Text;
using System.Text.Json;

namespace EfnUtilityAdapter;

/// <summary>
/// ASP.NET Core middleware that verifies EFN HMAC signatures on all
/// <c>/efn/v1/utility/**</c> requests.
///
/// <para>Every request from EFN Smart Terminal must include:</para>
/// <list type="bullet">
///   <item><c>X-EFN-Timestamp</c> — Unix timestamp in seconds</item>
///   <item><c>X-EFN-Signature</c> — <c>v1=HMAC-SHA256(secret, timestamp.body)</c></item>
/// </list>
///
/// <para>Requests with a timestamp older than 300 seconds are rejected
/// to prevent replay attacks.</para>
/// </summary>
public class EFNSignatureMiddleware
{
    private const string TimestampHeader = "X-EFN-Timestamp";
    private const string SignatureHeader = "X-EFN-Signature";
    private const string EfnPathPrefix = "/efn/v1/utility";
    private const int MaxAgeSeconds = 300;

    private readonly RequestDelegate _next;
    private readonly string _secret;

    public EFNSignatureMiddleware(RequestDelegate next, IConfiguration configuration)
    {
        _next = next;
        _secret = configuration["EFN_API_SECRET"]
            ?? throw new InvalidOperationException(
                "EFN_API_SECRET configuration value is not set. " +
                "Add it to appsettings.json or set the EFN_API_SECRET environment variable.");
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var path = context.Request.Path.Value ?? string.Empty;

        // Only authenticate EFN utility paths
        if (!path.StartsWith(EfnPathPrefix, StringComparison.OrdinalIgnoreCase))
        {
            await _next(context);
            return;
        }

        var timestamp = context.Request.Headers[TimestampHeader].FirstOrDefault();
        var signature = context.Request.Headers[SignatureHeader].FirstOrDefault();

        if (string.IsNullOrEmpty(timestamp) || string.IsNullOrEmpty(signature))
        {
            await WriteUnauthorized(context, "Missing X-EFN-Timestamp or X-EFN-Signature header");
            return;
        }

        // Buffer the request body so it can be read by downstream handlers
        context.Request.EnableBuffering();
        var bodyBytes = await ReadBodyAsync(context.Request);
        context.Request.Body.Position = 0; // reset for downstream

        var body = Encoding.UTF8.GetString(bodyBytes);

        if (!Security.VerifySignature(_secret, timestamp, signature, body, MaxAgeSeconds))
        {
            await WriteUnauthorized(context, "Invalid EFN signature or expired timestamp");
            return;
        }

        await _next(context);
    }

    private static async Task<byte[]> ReadBodyAsync(HttpRequest request)
    {
        using var ms = new MemoryStream();
        await request.Body.CopyToAsync(ms);
        return ms.ToArray();
    }

    private static async Task WriteUnauthorized(HttpContext context, string message)
    {
        context.Response.StatusCode = StatusCodes.Status401Unauthorized;
        context.Response.ContentType = "application/json";

        var payload = JsonSerializer.Serialize(new
        {
            error = message,
            hint = "Ensure X-EFN-Timestamp is within 300s of server time and X-EFN-Signature is v1=HMAC-SHA256(secret, timestamp.body)"
        });

        await context.Response.WriteAsync(payload);
    }
}
