package adapter
import ("crypto/hmac"; "crypto/sha256"; "encoding/hex"; "math"; "strconv"; "strings"; "time")
func VerifySignature(secret string, timestamp string, signature string, body []byte, window int64) bool {
    ts, err := strconv.ParseInt(timestamp, 10, 64)
    if err != nil || math.Abs(float64(time.Now().Unix()-ts)) > float64(window) { return false }
    mac := hmac.New(sha256.New, []byte(secret))
    mac.Write([]byte(timestamp + "."))
    mac.Write(body)
    expected := hex.EncodeToString(mac.Sum(nil))
    provided := strings.TrimPrefix(signature, "v1=")
    return hmac.Equal([]byte(expected), []byte(provided))
}
