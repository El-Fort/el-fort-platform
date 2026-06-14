package com.elfort.efn.adapter.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class AuthorizationResponse {
    public boolean success;
    public String status;
    @JsonProperty("authorization_id") public String authorizationId;
    @JsonProperty("bank_reference") public String bankReference;
    @JsonProperty("response_code") public String responseCode;
    public String message;

    public AuthorizationResponse() {}
    public AuthorizationResponse(boolean success, String status, String authorizationId,
                                  String bankReference, String responseCode, String message) {
        this.success = success; this.status = status; this.authorizationId = authorizationId;
        this.bankReference = bankReference; this.responseCode = responseCode; this.message = message;
    }
}
