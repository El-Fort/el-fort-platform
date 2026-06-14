# EFN Bank Adapter SDK — Java (Spring Boot 3)

## Quickstart

```java
// 1. Implement EFNBankAdapter
@Component
public class MyBankAdapter implements EFNBankAdapter {
    @Override
    public DebitResponse debit(DebitRequest req) {
        // Call core banking
        return new DebitResponse(true, "completed", bankRef, txRef, "00", "Success");
    }
    // ... implement all methods
}

// 2. Set environment variable
export EFN_API_SECRET=your_secret_from_efn

// 3. Run
mvn spring-boot:run
```

## Signature: `HMAC-SHA256(secret, timestamp + "." + body)` → base64 → `"v1={result}"`
