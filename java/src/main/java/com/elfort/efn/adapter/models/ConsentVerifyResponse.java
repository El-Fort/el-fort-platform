package com.elfort.efn.adapter.models;
public record ConsentVerifyResponse(boolean success, String status, String bankReference, String responseCode, String message) {
    public ConsentVerifyResponse(boolean success, String status) { this(success, status, "", "00", ""); }
}
