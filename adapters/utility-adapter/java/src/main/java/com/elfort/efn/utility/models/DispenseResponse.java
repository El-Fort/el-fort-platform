package com.elfort.efn.utility.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

/**
 * Response returned by the adapter after dispensing value to a customer.
 * Must include a {@code valueToken} for the customer to use (e.g. STS token).
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class DispenseResponse {

    @JsonProperty("status")
    private String status; // "success" or "failed"

    @JsonProperty("dispense_ref")
    private String dispenseRef;

    @JsonProperty("value_token")
    private String valueToken;

    @JsonProperty("receipt_details")
    private Map<String, String> receiptDetails;

    @JsonProperty("error")
    private String error;

    @JsonProperty("error_code")
    private String errorCode;

    public DispenseResponse() {}

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getDispenseRef() { return dispenseRef; }
    public void setDispenseRef(String dispenseRef) { this.dispenseRef = dispenseRef; }

    public String getValueToken() { return valueToken; }
    public void setValueToken(String valueToken) { this.valueToken = valueToken; }

    public Map<String, String> getReceiptDetails() { return receiptDetails; }
    public void setReceiptDetails(Map<String, String> receiptDetails) { this.receiptDetails = receiptDetails; }

    public String getError() { return error; }
    public void setError(String error) { this.error = error; }

    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }
}
