package com.elfort.efn.adapter.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class DebitResponse {
    public boolean success;
    public String status;
    @JsonProperty("bank_reference") public String bankReference;
    @JsonProperty("tx_ref") public String txRef;
    @JsonProperty("response_code") public String responseCode;
    public String message;

    public DebitResponse() {}
    public DebitResponse(boolean success, String status, String bankReference,
                          String txRef, String responseCode, String message) {
        this.success = success; this.status = status; this.bankReference = bankReference;
        this.txRef = txRef; this.responseCode = responseCode; this.message = message;
    }
}
