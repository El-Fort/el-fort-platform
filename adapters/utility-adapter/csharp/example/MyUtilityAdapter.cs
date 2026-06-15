using EfnUtilityAdapter.Models;

namespace EfnUtilityAdapter.Example;

/// <summary>
/// Example adapter for a prepaid electricity utility company.
/// Replace the hardcoded logic with actual database and vending system integrations.
/// </summary>
public class MyElectricityAdapter : IEFNUtilityAdapter
{
    public ValidateResponse ValidateCustomer(ValidateRequest req)
    {
        // TODO: Query your meter/account database
        // var meter = _meterRepository.FindByNumber(req.CustomerRef);
        // if (meter == null) return new ValidateResponse(IsValid: false);

        if (req.CustomerRef == "12345678901")
        {
            return new ValidateResponse(
                IsValid: true,
                CustomerName: "Emeka Chukwu",
                CustomerAddress: "22 Adeola Odeku, Victoria Island, Lagos",
                MinimumAmount: 500.0,
                OutstandingBalance: 0.0
            );
        }

        return new ValidateResponse(IsValid: false);
    }

    public DispenseResponse DispenseValue(DispenseRequest req)
    {
        // IMPORTANT: Check idempotency first
        // var existing = _txRepository.FindByEfnReference(req.EfnReference);
        // if (existing != null) return existing;

        // TODO: Generate your STS token or vend value from your billing system
        double units = req.Amount / 80.0; // NGN 80 per kWh

        var receipt = new Dictionary<string, string>
        {
            ["units"] = $"{units:F2} kWh",
            ["tariff"] = "NGN 80/kWh",
            ["tax"] = "0 NGN"
        };

        var response = new DispenseResponse(
            Status: "success",
            DispenseRef: $"UTL-{req.EfnReference[..Math.Min(8, req.EfnReference.Length)]}",
            ValueToken: "4512-6773-9901-2233-4455", // TODO: replace with real STS token
            ReceiptDetails: receipt
        );

        // TODO: Persist transaction for idempotency
        // _txRepository.Save(req.EfnReference, response);

        return response;
    }

    public TransactionStatusResponse TransactionStatus(string efnReference)
    {
        // TODO: Look up your DB
        // var tx = _txRepository.FindByEfnReference(efnReference);
        // if (tx == null) return new TransactionStatusResponse(Status: "not_found");
        return new TransactionStatusResponse(Status: "success", ValueToken: "4512-6773-9901-2233-4455");
    }
}
