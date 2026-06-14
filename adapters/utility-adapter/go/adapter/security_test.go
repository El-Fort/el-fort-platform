package adapter
import ("testing"; "time"; "fmt"; "crypto/hmac"; "crypto/sha256"; "encoding/hex")
func TestVerifySignature(t *testing.T) {
    secret := "test_secret"
    ts := fmt.Sprintf("%d", time.Now().Unix())
    body := []byte(`{"customer_ref":"123"}`)
    mac := hmac.New(sha256.New, []byte(secret))
    mac.Write([]byte(ts + ".")); mac.Write(body)
    sig := "v1=" + hex.EncodeToString(mac.Sum(nil))
    if !VerifySignature(secret, ts, sig, body, 300) { t.Error("Signature verification failed") }
    if VerifySignature(secret, ts, "v1=bad", body, 300) { t.Error("Should fail on bad signature") }
}
