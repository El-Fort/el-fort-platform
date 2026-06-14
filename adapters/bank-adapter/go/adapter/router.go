package adapter

import (
	"encoding/json"
	"io"
	"net/http"

	"github.com/go-chi/chi/v5"
)

func sigError(w http.ResponseWriter) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusUnauthorized)
	w.Write([]byte(`{"success":false,"message":"Invalid or expired signature"}`))
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(v)
}

func readBody(r *http.Request) ([]byte, error) {
	return io.ReadAll(r.Body)
}

func check(r *http.Request, body []byte, apiSecret string) bool {
	return VerifySignature(
		apiSecret,
		r.Header.Get("X-EFN-Timestamp"),
		body,
		r.Header.Get("X-EFN-Signature"),
	)
}

// NewRouter builds an http.Handler with all EFN adapter routes mounted under /efn/v1.
func NewRouter(a EFNBankAdapter, apiSecret string) http.Handler {
	r := chi.NewRouter()

	r.Post("/efn/v1/authorizations", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload AuthorizationRequest
		json.Unmarshal(body, &payload)
		resp, err := a.Authorize(payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Post("/efn/v1/authorizations/{id}/capture", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload CaptureRequest
		json.Unmarshal(body, &payload)
		resp, err := a.Capture(chi.URLParam(req, "id"), payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Post("/efn/v1/authorizations/{id}/reversal", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload ReversalRequest
		json.Unmarshal(body, &payload)
		resp, err := a.Reverse(chi.URLParam(req, "id"), payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Post("/efn/v1/debit", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload DebitRequest
		json.Unmarshal(body, &payload)
		resp, err := a.Debit(payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Post("/efn/v1/credit", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload CreditRequest
		json.Unmarshal(body, &payload)
		resp, err := a.Credit(payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Post("/efn/v1/balance", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload BalanceRequest
		json.Unmarshal(body, &payload)
		resp, err := a.Balance(payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Post("/efn/v1/account-enquiry", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload AccountEnquiryRequest
		json.Unmarshal(body, &payload)
		resp, err := a.AccountEnquiry(payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Get("/efn/v1/transaction/{ref}/status", func(w http.ResponseWriter, req *http.Request) {
		resp, err := a.TransactionStatus(chi.URLParam(req, "ref"))
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Post("/efn/v1/consent-otp", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload ConsentOTPRequest
		json.Unmarshal(body, &payload)
		resp, err := a.ConsentOTP(payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Post("/efn/v1/consent-verify", func(w http.ResponseWriter, req *http.Request) {
		body, _ := readBody(req)
		if !check(req, body, apiSecret) {
			sigError(w); return
		}
		var payload ConsentVerifyRequest
		json.Unmarshal(body, &payload)
		resp, err := a.ConsentVerify(payload)
		if err != nil {
			http.Error(w, err.Error(), 500); return
		}
		writeJSON(w, resp)
	})

	r.Get("/efn/v1/health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, map[string]string{"status": "ok"})
	})

	return r
}
