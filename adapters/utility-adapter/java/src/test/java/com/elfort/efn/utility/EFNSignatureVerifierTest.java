package com.elfort.efn.utility;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class EFNSignatureVerifierTest {
    @Test
    public void testSignature() throws Exception {
        String secret = "test_secret";
        String ts = String.valueOf(System.currentTimeMillis()/1000);
        String body = "{\"customer_ref\":\"123\"}";
        
        javax.crypto.Mac mac = javax.crypto.Mac.getInstance("HmacSHA256");
        mac.init(new javax.crypto.spec.SecretKeySpec(secret.getBytes(), "HmacSHA256"));
        byte[] rawHmac = mac.doFinal((ts + "." + body).getBytes());
        StringBuilder sb = new StringBuilder();
        for (byte b : rawHmac) sb.append(String.format("%02x", b));
        String sig = "v1=" + sb.toString();
        
        assertTrue(EFNSignatureVerifier.verify(secret, ts, sig, body, 300));
        assertFalse(EFNSignatureVerifier.verify(secret, ts, "v1=bad", body, 300));
    }
}
