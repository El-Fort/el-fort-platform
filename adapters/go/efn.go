// Package efn provides the EFN Biometric Subscription Payments SDK for Go.
package efn

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const DefaultBaseURL = "https://smart-terminal.el-fort.com"

type Client struct {
	APIKey  string
	BaseURL string
	http    *http.Client
}

func New(apiKey string) *Client {
	return &Client{APIKey: apiKey, BaseURL: DefaultBaseURL,
		http: &http.Client{Timeout: 30 * time.Second}}
}

func (c *Client) do(method, path string, body interface{}) (map[string]interface{}, error) {
	var r io.Reader
	if body != nil {
		b, _ := json.Marshal(body)
		r = bytes.NewReader(b)
	}
	req, _ := http.NewRequest(method, c.BaseURL+path, r)
	req.Header.Set("Authorization", "Bearer "+c.APIKey)
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.http.Do(req)
	if err != nil { return nil, err }
	defer resp.Body.Close()
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("EFN API error %d: %v", resp.StatusCode, result["error"])
	}
	return result, nil
}

type PlanParams struct {
	Name        string  `json:"name"`
	Amount      float64 `json:"amount"`
	Currency    string  `json:"currency"`
	Interval    string  `json:"interval"`
	TrialDays   int     `json:"trial_days,omitempty"`
	WebhookURL  string  `json:"webhook_url,omitempty"`
}

func (c *Client) CreatePlan(p *PlanParams) (map[string]interface{}, error) {
	return c.do("POST", "/efn/api/subscriptions/plans/", p)
}
func (c *Client) ListPlans() (map[string]interface{}, error) {
	return c.do("GET", "/efn/api/subscriptions/plans/", nil)
}
func (c *Client) GetPaymentLink(planID string) (map[string]interface{}, error) {
	return c.do("GET", "/efn/api/subscriptions/plans/"+planID+"/payment-link/", nil)
}
func (c *Client) GetAnalytics() (map[string]interface{}, error) {
	return c.do("GET", "/efn/api/subscriptions/merchant/analytics/", nil)
}

// VerifyWebhook verifies the HMAC-SHA256 signature of a webhook payload.
func VerifyWebhook(payload []byte, signature, secret string) bool {
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(payload)
	expected := "sha256=" + hex.EncodeToString(mac.Sum(nil))
	return hmac.Equal([]byte(expected), []byte(signature))
}
