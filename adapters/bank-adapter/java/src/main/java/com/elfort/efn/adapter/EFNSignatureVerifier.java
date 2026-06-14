package com.elfort.efn.adapter;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

public class EFNSignatureVerifier {

    private static final long REPLAY_WINDOW = 300L;

    /**
     * Verifies the EFN gateway HMAC-SHA256 signature and timestamp freshness.
     * Expected signature: v1=base64(HMAC-SHA256(secret, timestamp + "." + rawBody))
     */
    public static boolean verify(String apiSecret, String timestamp, byte[] rawBody, String signature) {
        if (timestamp == null || signature == null) return false;

        long ts;
        try {
            ts = Long.parseLong(timestamp);
        } catch (NumberFormatException e) {
            return false;
        }

        long now = System.currentTimeMillis() / 1000L;
        if (Math.abs(now - ts) > REPLAY_WINDOW) return false;

        try {
            byte[] prefix = (timestamp + ".").getBytes(StandardCharsets.UTF_8);
            byte[] message = new byte[prefix.length + rawBody.length];
            System.arraycopy(prefix, 0, message, 0, prefix.length);
            System.arraycopy(rawBody, 0, message, prefix.length, rawBody.length);

            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(apiSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            String expected = "v1=" + Base64.getEncoder().encodeToString(mac.doFinal(message));

            // Constant-time comparison
            return MessageDigest.isEqual(
                expected.getBytes(StandardCharsets.UTF_8),
                signature.getBytes(StandardCharsets.UTF_8)
            );
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            return false;
        }
    }
}
