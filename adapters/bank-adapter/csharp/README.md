# EFN Bank Adapter SDK — C# (.NET 8)

## Quickstart

```csharp
// 1. Implement IEfnBankAdapter
public class MyBankAdapter : IEfnBankAdapter {
    public async Task<DebitResponse> DebitAsync(DebitRequest req) {
        var result = await _coreBank.Debit(req.AccountNumber, decimal.Parse(req.Amount));
        return new DebitResponse(true, "completed", TxRef: result.Reference);
    }
    // ... implement all 10 methods
}

// 2. Wire in Program.cs
builder.Services.AddEfnAdapter(new MyBankAdapter(), Environment.GetEnvironmentVariable("EFN_API_SECRET")!);
app.Use(async (ctx, next) => { ctx.Request.EnableBuffering(); await next(); });
app.MapControllers();
```

## Signature: `HMAC-SHA256(secret, timestamp + "." + body)` → base64 → `"v1={result}"`
Replay window: 300s
