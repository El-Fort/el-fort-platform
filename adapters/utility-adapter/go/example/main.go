package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"

	"efn-utility-adapter/adapter"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

// MyAdapter is a concrete example implementation of adapter.EFNUtilityAdapter.
// Replace the logic below with your actual utility company business logic.
type MyAdapter struct{}

// ValidateCustomer checks whether a customer's meter/account number is valid
// before EFN accepts payment from the customer.
func (a *MyAdapter) ValidateCustomer(ctx context.Context, req adapter.ValidateRequest) (*adapter.ValidateResponse, error) {
	// TODO: Replace with a real database lookup using req.CustomerRef
	log.Printf("[validate] meter=%s category=%s", req.CustomerRef, req.UtilityCategory)

	if req.CustomerRef == "12345678901" {
		return &adapter.ValidateResponse{
			IsValid:            true,
			CustomerName:       "Emeka Chukwu",
			CustomerAddress:    "22 Adeola Odeku, Victoria Island, Lagos",
			MinimumAmount:      500.0,
			OutstandingBalance: 0.0,
		}, nil
	}

	return &adapter.ValidateResponse{IsValid: false}, nil
}

// DispenseValue is called after the customer completes payment. Generate and
// return a value token (e.g. STS electricity token, gas voucher, data PIN).
func (a *MyAdapter) DispenseValue(ctx context.Context, req adapter.DispenseRequest) (*adapter.DispenseResponse, error) {
	// TODO: Integrate with your token generation / vending system
	log.Printf("[dispense] meter=%s amount=%.2f %s ref=%s", req.CustomerRef, req.Amount, req.Currency, req.EfnReference)

	units := req.Amount / 80.0 // Example: NGN 80 per kWh

	return &adapter.DispenseResponse{
		Status:      "success",
		DispenseRef: fmt.Sprintf("UTL-%s", req.EfnReference[:min(8, len(req.EfnReference))]),
		ValueToken:  "4512-6773-9901-2233-4455", // TODO: replace with real generated token
		ReceiptDetails: map[string]string{
			"units":  fmt.Sprintf("%.2f kWh", units),
			"tariff": "NGN 80/kWh",
			"tax":    "0 NGN",
		},
	}, nil
}

// TransactionStatus is called by EFN to query the outcome of a previous dispense.
// Used for reconciliation and failed-payment retry flows.
func (a *MyAdapter) TransactionStatus(ctx context.Context, efnReference string) (*adapter.TransactionStatusResponse, error) {
	// TODO: Look up the transaction in your DB by efnReference and return stored result
	log.Printf("[status] querying ref=%s", efnReference)

	return &adapter.TransactionStatusResponse{
		Status:     "success",
		ValueToken: "4512-6773-9901-2233-4455",
	}, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	secret := os.Getenv("EFN_API_SECRET")
	if secret == "" {
		log.Fatal("EFN_API_SECRET environment variable must be set")
	}

	bindAddr := os.Getenv("BIND_ADDR")
	if bindAddr == "" {
		bindAddr = ":8080"
	}

	myAdapter := &MyAdapter{}

	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Mount("/", adapter.MakeRouter(myAdapter, secret))

	log.Printf("EFN Utility Adapter listening on %s", bindAddr)
	log.Println("  POST /efn/v1/utility/validate")
	log.Println("  POST /efn/v1/utility/dispense")
	log.Println("  GET  /efn/v1/utility/transaction/{ref}/status")

	if err := http.ListenAndServe(bindAddr, r); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
