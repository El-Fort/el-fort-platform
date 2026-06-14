package com.elfort.efn.adapter.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class AccountEnquiryResponse {
    public boolean success;
    @JsonProperty("account_number") public String accountNumber;
    @JsonProperty("account_name") public String accountName;
    public String currency;
    @JsonProperty("phone_last4") public String phoneLast4;
    @JsonProperty("response_code") public String responseCode;
    public String message;

    public AccountEnquiryResponse() {}
    public AccountEnquiryResponse(boolean success, String accountNumber, String accountName,
                                   String currency, String phoneLast4, String responseCode, String message) {
        this.success = success; this.accountNumber = accountNumber; this.accountName = accountName;
        this.currency = currency; this.phoneLast4 = phoneLast4; this.responseCode = responseCode;
        this.message = message;
    }
}
