use base64::{engine::general_purpose::STANDARD, Engine};
use hmac::{Hmac, Mac};
use sha2::Sha256;
use std::time::{SystemTime, UNIX_EPOCH};

const REPLAY_WINDOW: i64 = 300;

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

    let mut msg = format!("{}.", timestamp).into_bytes();
    msg.extend_from_slice(raw_body);

    let mut mac = Hmac::<Sha256>::new_from_slice(api_secret.as_bytes())
        .expect("HMAC accepts any key length");
    mac.update(&msg);
    let result = mac.finalize().into_bytes();
    let expected = format!("v1={}", STANDARD.encode(result));

    // Constant-time compare
    expected.len() == signature.len()
        && expected
            .bytes()
            .zip(signature.bytes())
            .fold(0u8, |acc, (a, b)| acc | (a ^ b))
            == 0
}
