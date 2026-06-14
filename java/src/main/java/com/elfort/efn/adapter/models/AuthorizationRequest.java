package com.elfort.efn.adapter.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class AuthorizationRequest {
    public String uan;
    public double amount;
    public String currency;
    @JsonProperty("efn_reference") public String efnReference;
    @JsonProperty("auth_method") public String authMethod;
    @JsonProperty("biometric_hash") public String biometricHash;
    @JsonProperty("pin_hash") public String pinHash;
    @JsonProperty("terminal_id") public String terminalId;
    public String gps;
}
