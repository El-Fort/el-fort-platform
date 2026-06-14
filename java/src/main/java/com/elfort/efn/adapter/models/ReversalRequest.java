package com.elfort.efn.adapter.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ReversalRequest {
    @JsonProperty("authorization_id") public String authorizationId;
    @JsonProperty("efn_reference") public String efnReference;
    public String reason;
}
