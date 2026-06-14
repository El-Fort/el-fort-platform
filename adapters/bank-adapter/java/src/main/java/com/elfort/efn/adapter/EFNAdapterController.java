package com.elfort.efn.adapter;

import com.elfort.efn.adapter.models.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletRequest;
import java.nio.charset.StandardCharsets;
import java.util.Map;

@RestController
@RequestMapping("/efn/v1")
public class EFNAdapterController {

    private final EFNBankAdapter adapter;
    private final String apiSecret;
    private final ObjectMapper mapper = new ObjectMapper();

    public EFNAdapterController(EFNBankAdapter adapter, String apiSecret) {
        this.adapter = adapter;
        this.apiSecret = apiSecret;
    }

    private ResponseEntity<?> sigError() {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
            .body(Map.of("success", false, "message", "Invalid or expired signature"));
    }

    private byte[] readBody(HttpServletRequest req) {
        try { return req.getInputStream().readAllBytes(); } catch (Exception e) { return new byte[0]; }
    }

    private boolean checkSig(HttpServletRequest req, byte[] body) {
        return EFNSignatureVerifier.verify(
            apiSecret,
            req.getHeader("X-EFN-Timestamp"),
            body,
            req.getHeader("X-EFN-Signature")
        );
    }

    @PostMapping("/authorizations")
    public ResponseEntity<?> authorize(HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.authorize(mapper.readValue(body, AuthorizationRequest.class)));
    }

    @PostMapping("/authorizations/{id}/capture")
    public ResponseEntity<?> capture(@PathVariable String id, HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.capture(id, mapper.readValue(body, CaptureRequest.class)));
    }

    @PostMapping("/authorizations/{id}/reversal")
    public ResponseEntity<?> reversal(@PathVariable String id, HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.reverse(id, mapper.readValue(body, ReversalRequest.class)));
    }

    @PostMapping("/debit")
    public ResponseEntity<?> debit(HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.debit(mapper.readValue(body, DebitRequest.class)));
    }

    @PostMapping("/credit")
    public ResponseEntity<?> credit(HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.credit(mapper.readValue(body, DebitRequest.class)));
    }

    @PostMapping("/balance")
    public ResponseEntity<?> balance(HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.balance(mapper.readValue(body, BalanceRequest.class)));
    }

    @PostMapping("/account-enquiry")
    public ResponseEntity<?> accountEnquiry(HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.accountEnquiry(mapper.readValue(body, AccountEnquiryRequest.class)));
    }

    @GetMapping("/transaction/{ref}/status")
    public ResponseEntity<?> txStatus(@PathVariable String ref) {
        return ResponseEntity.ok(adapter.transactionStatus(ref));
    }

    @PostMapping("/consent-otp")
    public ResponseEntity<?> consentOtp(HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.consentOtp(mapper.readValue(body, ConsentOTPRequest.class)));
    }

    @PostMapping("/consent-verify")
    public ResponseEntity<?> consentVerify(HttpServletRequest req) throws Exception {
        byte[] body = readBody(req);
        if (!checkSig(req, body)) return sigError();
        return ResponseEntity.ok(adapter.consentVerify(mapper.readValue(body, ConsentVerifyRequest.class)));
    }

    @GetMapping("/health")
    public ResponseEntity<?> health() {
        return ResponseEntity.ok(Map.of("status", "ok"));
    }
}
