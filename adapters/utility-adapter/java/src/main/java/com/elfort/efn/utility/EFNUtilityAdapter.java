package com.elfort.efn.utility;

import com.elfort.efn.utility.models.DispenseRequest;
import com.elfort.efn.utility.models.DispenseResponse;
import com.elfort.efn.utility.models.TransactionStatusResponse;
import com.elfort.efn.utility.models.ValidateRequest;
import com.elfort.efn.utility.models.ValidateResponse;

/**
 * Core interface that every EFN Utility Provider Adapter must implement.
 *
 * <h2>Integration Flow</h2>
 * <pre>
 * EFN Smart Terminal
 *        │
 *        │  HMAC-signed HTTP request
 *        ▼
 * Your Adapter Server  ◄─── implements EFNUtilityAdapter
 *        │
 *        │  Business logic
 *        ▼
 * Your Utility DB / Vending System
 * </pre>
 *
 * <h2>Quick Start (Spring Boot)</h2>
 * <pre>{@code
 * @Component
 * public class MyAdapter implements EFNUtilityAdapter {
 *     @Override
 *     public ValidateResponse validateCustomer(ValidateRequest req) {
 *         // look up req.getCustomerRef() in your DB
 *     }
 *     // ... implement dispenseValue and transactionStatus
 * }
 * }</pre>
 *
 * <p>Once your adapter bean is registered, the {@code EFNUtilityController}
 * auto-wires it and exposes the three required HTTP endpoints.
 */
public interface EFNUtilityAdapter {

    /**
     * Validate a customer's account or meter number.
     *
     * <p>EFN calls this before presenting the payment screen to the customer.
     * If {@code isValid} is false in the response, the transaction is aborted.
     *
     * @param req contains {@code customerRef} (meter/account number) and
     *            {@code utilityCategory} (e.g. "ELECTRICITY", "WATER")
     * @return validation result with customer details if valid
     */
    ValidateResponse validateCustomer(ValidateRequest req);

    /**
     * Dispense value to the customer after successful payment.
     *
     * <p>EFN calls this immediately after payment is confirmed. This method
     * must be idempotent — use {@code req.getEfnReference()} as a unique key
     * to detect and safely replay duplicate requests.
     *
     * @param req payment details including amount, currency, and EFN reference
     * @return dispensed value token and receipt details
     */
    DispenseResponse dispenseValue(DispenseRequest req);

    /**
     * Query the status of a previous dispense transaction.
     *
     * <p>EFN uses this for reconciliation and to recover from network failures.
     *
     * @param efnReference the unique EFN transaction reference
     * @return transaction status and the value token if previously dispensed
     */
    TransactionStatusResponse transactionStatus(String efnReference);
}
