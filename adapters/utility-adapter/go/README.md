# EFN Utility Adapter - Go SDK

A Gin-gonic implementation of the EFN Utility Provider Adapter.

## Quickstart
1. Download dependencies: `go mod tidy`
2. Set your secret: `export EFN_API_SECRET="your_secret"`
3. Run the server: `go run main.go`

## Customization
Open `main.go` and replace the placeholder logic inside the `POST /validate` and `POST /dispense` routes.
