package com.elfort.efn.adapter.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class DebitRequest {
    public String uan;
    public double amount;
    public String currency;
    @JsonProperty("tx_ref") public String txRef;
    @JsonProperty("efn_reference") public String efnReference;
    public String narration;
}
