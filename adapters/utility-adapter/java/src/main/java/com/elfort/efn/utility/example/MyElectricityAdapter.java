package com.elfort.efn.utility.example;

import com.elfort.efn.utility.EFNUtilityAdapter;
import com.elfort.efn.utility.models.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * Example implementation of {@link EFNUtilityAdapter} for a prepaid electricity company.
 *
 * <p>Replace the hardcoded logic with real database queries and your utility vending system.
 *
 * <h2>STS Token Generation</h2>
 * <p>For prepaid electricity, you will typically integrate with an STS (Standard Transfer
 * Specification) library to generate 20-digit tokens for the meter. Libraries are available
 * for Java via the open-sts or meter-library projects.
 */
@Component
public class MyElectricityAdapter implements EFNUtilityAdapter {

    private static final Logger log = LoggerFactory.getLogger(MyElectricityAdapter.class);

    @Override
    public ValidateResponse validateCustomer(ValidateRequest req) {
        log.info("Validating meter: {} category: {}", req.getCustomerRef(), req.getUtilityCategory());

        // TODO: Replace with actual database lookup
        // Example: meterRepository.findByMeterNumber(req.getCustomerRef())
        if ("12345678901".equals(req.getCustomerRef())) {
            ValidateResponse response = new ValidateResponse();
            response.setIsValid(true);
            response.setCustomerName("Emeka Chukwu");
            response.setCustomerAddress("22 Adeola Odeku, Victoria Island, Lagos");
            response.setMinimumAmount(500.0);
            response.setOutstandingBalance(0.0);
            return response;
        }

        ValidateResponse invalid = new ValidateResponse();
        invalid.setIsValid(false);
        return invalid;
    }

    @Override
    public DispenseResponse dispenseValue(DispenseRequest req) {
        log.info("Dispensing value: meter={} amount={} {} ref={}",
            req.getCustomerRef(), req.getAmount(), req.getCurrency(), req.getEfnReference());

        // IMPORTANT: First check if this efnReference was already processed (idempotency)
        // DispenseResponse existing = transactionRepository.findByEfnReference(req.getEfnReference());
        // if (existing != null) return existing;

        // TODO: Generate STS token or integrate with your vending system
        double units = req.getAmount() / 80.0; // NGN 80 per kWh example tariff

        Map<String, String> receipt = new HashMap<>();
        receipt.put("units", String.format("%.2f kWh", units));
        receipt.put("tariff", "NGN 80/kWh");
        receipt.put("tax", "0 NGN");

        DispenseResponse response = new DispenseResponse();
        response.setStatus("success");
        response.setDispenseRef("UTL-" + req.getEfnReference().substring(0, Math.min(8, req.getEfnReference().length())));
        response.setValueToken("4512-6773-9901-2233-4455"); // TODO: replace with generated STS token
        response.setReceiptDetails(receipt);

        // TODO: Save transaction to DB for idempotency:
        // transactionRepository.save(new Transaction(req.getEfnReference(), response));

        return response;
    }

    @Override
    public TransactionStatusResponse transactionStatus(String efnReference) {
        log.info("Querying transaction status: ref={}", efnReference);

        // TODO: Look up transaction in your DB
        // Transaction tx = transactionRepository.findByEfnReference(efnReference);
        // if (tx == null) return new TransactionStatusResponse("not_found", null);

        return new TransactionStatusResponse("success", "4512-6773-9901-2233-4455");
    }
}
