package com.elfort.efn.adapter.models;
public record TransactionStatusResponse(boolean success, String status, String bankReference, String responseCode, String message) {
    public TransactionStatusResponse(boolean success, String status) { this(success, status, "", "00", ""); }
}
