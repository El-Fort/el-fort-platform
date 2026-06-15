package com.elfort.efn.utility.models;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Request sent by EFN to validate a customer's account or meter number
 * before accepting payment from the customer.
 */
public class ValidateRequest {

    @JsonProperty("customer_ref")
    private String customerRef;

    @JsonProperty("utility_category")
    private String utilityCategory;

    public ValidateRequest() {}

    public ValidateRequest(String customerRef, String utilityCategory) {
        this.customerRef = customerRef;
        this.utilityCategory = utilityCategory;
    }

    public String getCustomerRef() { return customerRef; }
    public void setCustomerRef(String customerRef) { this.customerRef = customerRef; }

    public String getUtilityCategory() { return utilityCategory; }
    public void setUtilityCategory(String utilityCategory) { this.utilityCategory = utilityCategory; }
}
