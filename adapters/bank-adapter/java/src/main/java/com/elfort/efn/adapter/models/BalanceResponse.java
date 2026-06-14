package com.elfort.efn.adapter.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class BalanceResponse {
    public boolean success;
    public String uan;
    public double balance;
    public String currency;
    @JsonProperty("account_number") public String accountNumber;
    @JsonProperty("response_code") public String responseCode;

    public BalanceResponse() {}
    public BalanceResponse(boolean success, String uan, double balance, String currency,
                            String accountNumber, String responseCode) {
        this.success = success; this.uan = uan; this.balance = balance;
        this.currency = currency; this.accountNumber = accountNumber; this.responseCode = responseCode;
    }
}
