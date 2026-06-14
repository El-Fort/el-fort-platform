using EfnAdapter;
using Example;

var builder = WebApplication.CreateBuilder(args);

var apiSecret = builder.Configuration["EFN_API_SECRET"] ?? "change_me";
builder.Services.AddEfnAdapter(new MyBankAdapter(), apiSecret);
// Enable buffering so controller can re-read request body for signature verification
builder.Services.AddHttpContextAccessor();

var app = builder.Build();
app.Use(async (ctx, next) => { ctx.Request.EnableBuffering(); await next(); });
app.MapControllers();
app.Run();
