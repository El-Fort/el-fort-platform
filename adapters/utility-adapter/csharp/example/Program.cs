using EfnUtilityAdapter;
using EfnUtilityAdapter.Example;

var builder = WebApplication.CreateBuilder(args);

// Register your adapter implementation
builder.Services.AddEFNUtilityAdapter<MyElectricityAdapter>();

var app = builder.Build();

// Apply EFN HMAC signature verification middleware
app.UseMiddleware<EFNSignatureMiddleware>();

// Map the three EFN utility endpoints
app.MapEFNUtilityEndpoints();

app.Run();
