# EFN Bank Adapter — Go SDK

## Usage

```go
import "github.com/elfort/efn-bank-adapter/adapter"

type MyBank struct{}

func (b *MyBank) Authorize(req adapter.AuthorizationRequest) (adapter.AuthorizationResponse, error) {
    // connect to your core banking system
}
// implement remaining interface methods...

func main() {
    h := adapter.NewRouter(&MyBank{}, os.Getenv("EFN_API_SECRET"))
    http.ListenAndServe(":8080", h)
}
```

## Build

```bash
go mod tidy
go build ./...
```

## Signature

`HMAC-SHA256(apiSecret, timestamp + "." + rawBody)` → base64 → prefix `v1=`

Replay window: ±300 seconds.
