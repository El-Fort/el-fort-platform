using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapPost("/efn/v1/utility/validate", (ValidateReq req) => {
    return Results.Ok(new { is_valid = true, customer_name = "John Doe" });
});

app.MapPost("/efn/v1/utility/dispense", (DispenseReq req) => {
    return Results.Ok(new { status = "success", value_token = "1234-5678" });
});

app.Run();

record ValidateReq(string customer_ref);
record DispenseReq(string customer_ref, decimal amount);
