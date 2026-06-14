package adapter

import (
    "encoding/json"
    "net/http"
    "strings"
    "github.com/go-chi/chi/v5"
    "context"
)

// MakeRouter creates an HTTP router with three EFN Utility endpoints:
//
//   POST /efn/v1/utility/validate                       - Validate customer account/meter
//   POST /efn/v1/utility/dispense                       - Dispense value (token/credit)
//   GET  /efn/v1/utility/transaction/{ref}/status       - Query transaction result
//
// Mount in your HTTP server:
//   r := chi.NewRouter()
//   r.Mount("/", adapter.MakeRouter(myAdapter, "your_secret"))
func MakeRouter(a EFNUtilityAdapter, secret string) http.Handler {
    r := chi.NewRouter()

    authMiddleware := func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            ts := r.Header.Get("X-EFN-Timestamp")
            sig := r.Header.Get("X-EFN-Signature")

            var buf []byte
            if r.Body != nil {
                buf = make([]byte, 0)
                tmp := make([]byte, 512)
                for {
                    n, err := r.Body.Read(tmp)
                    if n > 0 { buf = append(buf, tmp[:n]...) }
                    if err != nil { break }
                }
            }

            if !VerifySignature(secret, ts, sig, buf, 300) {
                w.WriteHeader(http.StatusUnauthorized)
                json.NewEncoder(w).Encode(map[string]string{"error": "Invalid signature"})
                return
            }
            // Store parsed body in context
            ctx := context.WithValue(r.Context(), "rawBody", buf)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }

    r.Use(authMiddleware)
    r.Use(func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            w.Header().Set("Content-Type", "application/json")
            next.ServeHTTP(w, r)
        })
    })

    r.Post("/efn/v1/utility/validate", func(w http.ResponseWriter, r *http.Request) {
        raw, _ := r.Context().Value("rawBody").([]byte)
        var req ValidateRequest
        json.Unmarshal(raw, &req)
        resp, err := a.ValidateCustomer(r.Context(), req)
        if err != nil { w.WriteHeader(500); json.NewEncoder(w).Encode(map[string]string{"error": err.Error()}); return }
        json.NewEncoder(w).Encode(resp)
    })

    r.Post("/efn/v1/utility/dispense", func(w http.ResponseWriter, r *http.Request) {
        raw, _ := r.Context().Value("rawBody").([]byte)
        var req DispenseRequest
        json.Unmarshal(raw, &req)
        resp, err := a.DispenseValue(r.Context(), req)
        if err != nil { w.WriteHeader(500); json.NewEncoder(w).Encode(map[string]string{"error": err.Error()}); return }
        json.NewEncoder(w).Encode(resp)
    })

    r.Get("/efn/v1/utility/transaction/{ref}/status", func(w http.ResponseWriter, r *http.Request) {
        ref := chi.URLParam(r, "ref")
        ref = strings.TrimSpace(ref)
        resp, err := a.TransactionStatus(r.Context(), ref)
        if err != nil { w.WriteHeader(500); json.NewEncoder(w).Encode(map[string]string{"error": err.Error()}); return }
        json.NewEncoder(w).Encode(resp)
    })

    return r
}
