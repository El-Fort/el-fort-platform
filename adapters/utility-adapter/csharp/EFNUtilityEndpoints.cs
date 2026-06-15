using EfnUtilityAdapter.Models;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;

namespace EfnUtilityAdapter;

/// <summary>
/// Extension methods to map EFN Utility endpoints onto an ASP.NET Core application.
/// </summary>
public static class EFNUtilityEndpoints
{
    /// <summary>
    /// Maps the three required EFN Utility endpoints:
    /// <list type="bullet">
    ///   <item><c>POST /efn/v1/utility/validate</c></item>
    ///   <item><c>POST /efn/v1/utility/dispense</c></item>
    ///   <item><c>GET  /efn/v1/utility/transaction/{efnReference}/status</c></item>
    /// </list>
    /// </summary>
    /// <example>
    /// <code>
    /// var app = builder.Build();
    /// app.UseMiddleware&lt;EFNSignatureMiddleware&gt;();
    /// app.MapEFNUtilityEndpoints();
    /// app.Run();
    /// </code>
    /// </example>
    public static WebApplication MapEFNUtilityEndpoints(this WebApplication app)
    {
        var adapter = app.Services.GetRequiredService<IEFNUtilityAdapter>();

        /// POST /efn/v1/utility/validate
        /// Validates a customer account or meter number before payment.
        app.MapPost("/efn/v1/utility/validate", (ValidateRequest req) =>
        {
            var result = adapter.ValidateCustomer(req);
            return Results.Ok(result);
        })
        .WithName("ValidateCustomer")
        .WithDescription("Validate customer account/meter before EFN accepts payment");

        /// POST /efn/v1/utility/dispense
        /// Dispenses value (token/credit) after payment confirmation.
        app.MapPost("/efn/v1/utility/dispense", (DispenseRequest req) =>
        {
            var result = adapter.DispenseValue(req);
            return Results.Ok(result);
        })
        .WithName("DispenseValue")
        .WithDescription("Dispense value token after customer payment is confirmed");

        /// GET /efn/v1/utility/transaction/{efnReference}/status
        /// Queries the outcome of a previous dispense transaction.
        app.MapGet("/efn/v1/utility/transaction/{efnReference}/status", (string efnReference) =>
        {
            var result = adapter.TransactionStatus(efnReference);
            return Results.Ok(result);
        })
        .WithName("TransactionStatus")
        .WithDescription("Query status of a previous dispense transaction");

        return app;
    }
}

/// <summary>
/// Extension methods for registering EFN Utility Adapter services.
/// </summary>
public static class EFNUtilityServiceExtensions
{
    /// <summary>
    /// Registers the provided adapter implementation as the <see cref="IEFNUtilityAdapter"/> service.
    /// </summary>
    /// <typeparam name="TAdapter">Your adapter class implementing <see cref="IEFNUtilityAdapter"/></typeparam>
    /// <example>
    /// <code>
    /// builder.Services.AddEFNUtilityAdapter&lt;MyUtilityAdapter&gt;();
    /// </code>
    /// </example>
    public static IServiceCollection AddEFNUtilityAdapter<TAdapter>(this IServiceCollection services)
        where TAdapter : class, IEFNUtilityAdapter
    {
        services.AddSingleton<IEFNUtilityAdapter, TAdapter>();
        return services;
    }
}
