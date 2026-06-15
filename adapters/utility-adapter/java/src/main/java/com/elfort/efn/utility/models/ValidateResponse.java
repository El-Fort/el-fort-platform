package com.elfort.efn.utility.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Response returned by the adapter after validating a customer account.
 * If {@code isValid} is false, EFN will not proceed with payment.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ValidateResponse {

    @JsonProperty("is_valid")
    private boolean isValid;

    @JsonProperty("customer_name")
    private String customerName;

    @JsonProperty("customer_address")
    private String customerAddress;

    @JsonProperty("minimum_amount")
    private double minimumAmount;

    @JsonProperty("outstanding_balance")
    private double outstandingBalance;

    public ValidateResponse() {}

    public boolean isValid() { return isValid; }
    public void setIsValid(boolean valid) { isValid = valid; }

    public String getCustomerName() { return customerName; }
    public void setCustomerName(String customerName) { this.customerName = customerName; }

    public String getCustomerAddress() { return customerAddress; }
    public void setCustomerAddress(String customerAddress) { this.customerAddress = customerAddress; }

    public double getMinimumAmount() { return minimumAmount; }
    public void setMinimumAmount(double minimumAmount) { this.minimumAmount = minimumAmount; }

    public double getOutstandingBalance() { return outstandingBalance; }
    public void setOutstandingBalance(double outstandingBalance) { this.outstandingBalance = outstandingBalance; }
}
