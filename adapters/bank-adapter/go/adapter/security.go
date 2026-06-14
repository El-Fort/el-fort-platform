package adapter

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"math"
	"strconv"
	"time"
)

const replayWindow = 300 // seconds

// VerifySignature validates the EFN gateway HMAC signature and timestamp.
func VerifySignature(apiSecret, timestamp string, rawBody []byte, signature string) bool {
	ts, err := strconv.ParseInt(timestamp, 10, 64)
	if err != nil {
		return false
	}
	if math.Abs(float64(time.Now().Unix()-ts)) > replayWindow {
		return false
	}

	msg := append([]byte(timestamp+"."), rawBody...)
	mac := hmac.New(sha256.New, []byte(apiSecret))
	mac.Write(msg)
	expected := "v1=" + base64.StdEncoding.EncodeToString(mac.Sum(nil))

	return hmac.Equal([]byte(expected), []byte(signature))
}
