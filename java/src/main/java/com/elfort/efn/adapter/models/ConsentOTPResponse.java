package com.elfort.efn.adapter.models;
public record ConsentOTPResponse(boolean success, String status, String bankReference, String responseCode, String message) {
    public ConsentOTPResponse(boolean success, String status) { this(success, status, "", "00", ""); }
}
