use base64::{engine::general_purpose::STANDARD, Engine};
use hmac::{Hmac, Mac};
use sha2::Sha256;
use std::time::{SystemTime, UNIX_EPOCH};

const REPLAY_WINDOW: i64 = 300;

/// Compute EFN signature: HMAC-SHA256(secret, timestamp + "." + body) → base64 → "v1={result}"
pub fn sign_request(api_secret: &str, timestamp: &str, raw_body: &[u8]) -> String {
    let mut msg = format!("{}.", timestamp).into_bytes();
    msg.extend_from_slice(raw_body);
    let mut mac = Hmac::<Sha256>::new_from_slice(api_secret.as_bytes())
        .expect("HMAC accepts any key length");
    mac.update(&msg);
    format!("v1={}", STANDARD.encode(mac.finalize().into_bytes()))
}

/// Verify the EFN gateway HMAC-SHA256 signature and timestamp freshness.
pub fn verify_signature(api_secret: &str, timestamp: &str, raw_body: &[u8], signature: &str) -> bool {
    let ts: i64 = match timestamp.parse() {
        Ok(v) => v,
        Err(_) => return false,
    };
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs() as i64;
    if (now - ts).abs() > REPLAY_WINDOW {
        return false;
    }
    let expected = sign_request(api_secret, timestamp, raw_body);
    // Constant-time compare
    expected.len() == signature.len()
        && expected.bytes().zip(signature.bytes())
            .fold(0u8, |acc, (a, b)| acc | (a ^ b)) == 0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sign_known_vector() {
        let body = br#"{"uan":"014800001234567890","amount":"5000.00","currency":"NGN"}"#;
        let sig = sign_request("test_secret_key_efn", "1749999999", body);
        assert_eq!(sig, "v1=deVTwbJf8evqMRcQN8itx/dnr0epb35U1gRQBZ9YdLE=");
    }

    #[test]
    fn test_replay_rejection() {
        // Ancient timestamp must fail verify (replay protection)
        let body = b"test";
        let old_ts = "1000000000";
        let sig = sign_request("secret", old_ts, body);
        assert!(!verify_signature("secret", old_ts, body, &sig));
    }

    #[test]
    fn test_wrong_secret_rejected() {
        let body = b"payload";
        let ts = "1749999999";
        let sig = sign_request("correct_secret", ts, body);
        assert!(!verify_signature("wrong_secret", ts, body, &sig));
    }
}
