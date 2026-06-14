package com.elfort.efn.adapter;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class EFNSignatureVerifierTest {

    private static final String SECRET = "test_secret_key_efn";
    private static final String TS = "1749999999";
    private static final String BODY =
        "{\"uan\":\"014800001234567890\",\"amount\":\"5000.00\",\"currency\":\"NGN\"}";
    private static final String EXPECTED = "v1=deVTwbJf8evqMRcQN8itx/dnr0epb35U1gRQBZ9YdLE=";

    @Test
    void testSignKnownVector() throws Exception {
        String got = EFNSignatureVerifier.sign(SECRET, TS, BODY.getBytes());
        assertEquals(EXPECTED, got, "HMAC signature must match reference vector");
    }

    @Test
    void testVerifyValidSignature() {
        // Use a fresh timestamp within 300s window
        String now = String.valueOf(System.currentTimeMillis() / 1000);
        String sig;
        try {
            sig = EFNSignatureVerifier.sign(SECRET, now, BODY.getBytes());
        } catch (Exception e) { fail(e.getMessage()); return; }
        assertTrue(EFNSignatureVerifier.verify(SECRET, now, BODY.getBytes(), sig));
    }

    @Test
    void testReplayRejection() {
        // Timestamp 1000000000 is in 2001 — must be rejected
        String oldSig = "v1=anything";
        assertFalse(EFNSignatureVerifier.verify(SECRET, "1000000000", BODY.getBytes(), oldSig));
    }

    @Test
    void testWrongSecretRejected() {
        String now = String.valueOf(System.currentTimeMillis() / 1000);
        String sig;
        try {
            sig = EFNSignatureVerifier.sign(SECRET, now, BODY.getBytes());
        } catch (Exception e) { fail(e.getMessage()); return; }
        assertFalse(EFNSignatureVerifier.verify("wrong_secret", now, BODY.getBytes(), sig));
    }
}
