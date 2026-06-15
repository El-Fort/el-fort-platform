package com.elfort.efn.utility.models;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Request sent by EFN to dispense value after a customer completes payment.
 * The adapter must generate a value token (STS token, voucher, data PIN, etc.)
 * and return it in {@link DispenseResponse}.
 *
 * <p>Use {@code efnReference} as an idempotency key — store it with the
 * generated token so duplicate requests return the same token safely.
 */
public class DispenseRequest {

    @JsonProperty("customer_ref")
    private String customerRef;

    @JsonProperty("amount")
    private double amount;

    @JsonProperty("currency")
    private String currency;

    @JsonProperty("efn_reference")
    private String efnReference;

    public DispenseRequest() {}

    public DispenseRequest(String customerRef, double amount, String currency, String efnReference) {
        this.customerRef = customerRef;
        this.amount = amount;
        this.currency = currency;
        this.efnReference = efnReference;
    }

    public String getCustomerRef() { return customerRef; }
    public void setCustomerRef(String customerRef) { this.customerRef = customerRef; }

    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }

    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }

    public String getEfnReference() { return efnReference; }
    public void setEfnReference(String efnReference) { this.efnReference = efnReference; }
}
