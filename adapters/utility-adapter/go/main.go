package main

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io/ioutil"
	"math"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

var apiSecret = []byte(getEnv("EFN_API_SECRET", "test_secret_key_efn"))

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

func signatureMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		tsStr := c.GetHeader("X-EFN-Timestamp")
		sig := c.GetHeader("X-EFN-Signature")

		ts, _ := strconv.ParseInt(tsStr, 10, 64)
		if math.Abs(float64(time.Now().Unix()-ts)) > 300 {
			c.AbortWithStatusJSON(401, gin.H{"error": "Expired"})
			return
		}

		body, _ := ioutil.ReadAll(c.Request.Body)
		c.Request.Body = ioutil.NopCloser(bytes.NewBuffer(body))

		mac := hmac.New(sha256.New, apiSecret)
		mac.Write([]byte(tsStr + "."))
		mac.Write(body)
		expected := "v1=" + hex.EncodeToString(mac.Sum(nil))

		if expected != sig {
			c.AbortWithStatusJSON(401, gin.H{"error": "Invalid signature"})
			return
		}
		c.Next()
	}
}

func main() {
	r := gin.Default()
	utility := r.Group("/efn/v1/utility")
	utility.Use(signatureMiddleware())

	utility.POST("/validate", func(c *gin.Context) {
		// TODO: Implement logic
		c.JSON(200, gin.H{"is_valid": true, "customer_name": "John Doe"})
	})

	utility.POST("/dispense", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "success", "value_token": "1234-5678-9012"})
	})

	r.Run(":8080")
}
