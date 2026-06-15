package com.elfort.efn.utility.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Response returned when EFN queries the status of a prior dispense transaction.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TransactionStatusResponse {

    @JsonProperty("status")
    private String status; // "success", "pending", "failed"

    @JsonProperty("value_token")
    private String valueToken;

    public TransactionStatusResponse() {}

    public TransactionStatusResponse(String status, String valueToken) {
        this.status = status;
        this.valueToken = valueToken;
    }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getValueToken() { return valueToken; }
    public void setValueToken(String valueToken) { this.valueToken = valueToken; }
}
