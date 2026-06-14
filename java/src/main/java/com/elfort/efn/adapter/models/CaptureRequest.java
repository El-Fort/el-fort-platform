package com.elfort.efn.adapter.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class CaptureRequest {
    @JsonProperty("authorization_id") public String authorizationId;
    public double amount;
    @JsonProperty("efn_reference") public String efnReference;
}
