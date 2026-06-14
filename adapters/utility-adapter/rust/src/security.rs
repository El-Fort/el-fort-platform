use hmac::{Hmac, Mac};
use sha2::Sha256;
use std::time::{SystemTime, UNIX_EPOCH};

pub fn verify_signature(secret: &str, timestamp: &str, signature: &str, body: &[u8], window: u64) -> bool {
    let ts: u64 = match timestamp.parse() { Ok(t) => t, Err(_) => return false };
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
    if (now as i64 - ts as i64).abs() > window as i64 { return false; }

    let mut mac = Hmac::<Sha256>::new_from_slice(secret.as_bytes()).unwrap();
    mac.update(timestamp.as_bytes());
    mac.update(b".");
    mac.update(body);
    let expected = hex::encode(mac.finalize().into_bytes());
    let provided = signature.replace("v1=", "");
    expected == provided
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_verify() {
        let secret = "test_secret";
        let ts = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs().to_string();
        let body = b"{\"customer_ref\":\"123\"}";
        let mut mac = Hmac::<Sha256>::new_from_slice(secret.as_bytes()).unwrap();
        mac.update(ts.as_bytes()); mac.update(b"."); mac.update(body);
        let sig = format!("v1={}", hex::encode(mac.finalize().into_bytes()));
        assert!(verify_signature(secret, &ts, &sig, body, 300));
        assert!(!verify_signature(secret, &ts, "v1=bad", body, 300));
    }
}
