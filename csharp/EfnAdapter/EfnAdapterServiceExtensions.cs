using Microsoft.Extensions.DependencyInjection;

namespace EfnAdapter;

public static class EfnAdapterServiceExtensions
{
    /// <summary>
    /// Register EFN adapter services. Call builder.Services.AddEfnAdapter(myAdapter, "api_secret").
    /// </summary>
    public static IServiceCollection AddEfnAdapter(
        this IServiceCollection services, IEfnBankAdapter adapter, string apiSecret)
    {
        services.AddSingleton(adapter);
        services.AddSingleton(new EfnAdapterOptions { ApiSecret = apiSecret });
        services.AddControllers();
        return services;
    }
}
