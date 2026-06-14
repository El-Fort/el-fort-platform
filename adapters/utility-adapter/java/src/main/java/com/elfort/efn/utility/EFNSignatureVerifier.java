package com.elfort.efn.utility;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;

public class EFNSignatureVerifier {
    public static boolean verify(String secret, String timestamp, String signature, String body, int windowSecs) {
        try {
            long ts = Long.parseLong(timestamp);
            if (Math.abs(System.currentTimeMillis()/1000 - ts) > windowSecs) return false;
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            String payload = timestamp + "." + body;
            byte[] rawHmac = mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : rawHmac) { sb.append(String.format("%02x", b)); }
            String expected = sb.toString();
            String provided = signature.replace("v1=", "");
            return java.security.MessageDigest.isEqual(expected.getBytes(), provided.getBytes());
        } catch (Exception e) { return false; }
    }
}
