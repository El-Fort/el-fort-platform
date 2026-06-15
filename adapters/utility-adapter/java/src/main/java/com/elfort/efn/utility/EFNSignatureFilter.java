package com.elfort.efn.utility;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * Spring Security filter that validates EFN HMAC signatures on all
 * {@code /efn/v1/utility/**} requests.
 *
 * <p>Every request from EFN Smart Terminal includes two headers:
 * <ul>
 *   <li>{@code X-EFN-Timestamp} — Unix timestamp in seconds</li>
 *   <li>{@code X-EFN-Signature} — {@code v1=HMAC-SHA256(secret, timestamp.body)}</li>
 * </ul>
 *
 * <p>Requests with a timestamp older than 300 seconds are rejected to
 * prevent replay attacks.
 */
public class EFNSignatureFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(EFNSignatureFilter.class);
    private static final String EFN_PATH_PREFIX = "/efn/v1/utility";
    private static final String TIMESTAMP_HEADER = "X-EFN-Timestamp";
    private static final String SIGNATURE_HEADER = "X-EFN-Signature";

    private final String apiSecret;

    public EFNSignatureFilter(String apiSecret) {
        this.apiSecret = apiSecret;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !request.getRequestURI().startsWith(EFN_PATH_PREFIX);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {

        String timestamp = request.getHeader(TIMESTAMP_HEADER);
        String signature = request.getHeader(SIGNATURE_HEADER);

        if (timestamp == null || signature == null) {
            log.warn("EFN request missing signature headers: {}", request.getRequestURI());
            writeUnauthorized(response, "Missing X-EFN-Timestamp or X-EFN-Signature header");
            return;
        }

        // Wrap request to allow body to be read multiple times
        ContentCachingRequestWrapper wrappedRequest = new ContentCachingRequestWrapper(request);

        // Read body to trigger caching (ContentCachingRequestWrapper lazy-reads)
        wrappedRequest.getInputStream().readAllBytes();
        byte[] body = wrappedRequest.getContentAsByteArray();

        String bodyStr = new String(body, StandardCharsets.UTF_8);

        if (!EFNSignatureVerifier.verify(apiSecret, timestamp, signature, bodyStr, 300)) {
            log.warn("EFN signature verification failed for: {}", request.getRequestURI());
            writeUnauthorized(response, "Invalid EFN signature or expired timestamp");
            return;
        }

        log.debug("EFN signature verified for: {}", request.getRequestURI());
        filterChain.doFilter(wrappedRequest, response);
    }

    private void writeUnauthorized(HttpServletResponse response, String message) throws IOException {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType("application/json");
        response.getWriter().write(
            String.format("{\"error\":\"%s\",\"hint\":\"Ensure X-EFN-Timestamp is within 300s of server time\"}", message)
        );
    }
}
