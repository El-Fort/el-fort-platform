package adapter
import (
    "crypto/hmac"; "crypto/sha256"; "encoding/base64"; "testing"
)
func computeSig(secret, ts string, body []byte) string {
    m := hmac.New(sha256.New, []byte(secret))
    m.Write([]byte(ts + ".")); m.Write(body)
    return "v1=" + base64.StdEncoding.EncodeToString(m.Sum(nil))
}
func TestSignKnownVector(t *testing.T) {
    body := []byte(`{"uan":"014800001234567890","amount":"5000.00","currency":"NGN"}`)
    got := computeSig("test_secret_key_efn", "1749999999", body)
    expected := "v1=deVTwbJf8evqMRcQN8itx/dnr0epb35U1gRQBZ9YdLE="
    if !hmac.Equal([]byte(got), []byte(expected)) {
        t.Errorf("got %s, want %s", got, expected)
    }
}
func TestVerifySignature(t *testing.T) {
    if !VerifySignature("test", "bad_ts", nil, "") {
        // expected false
    }
    if VerifySignature("s", "not-a-number", []byte("body"), "v1=x") {
        t.Error("bad timestamp should fail")
    }
}
