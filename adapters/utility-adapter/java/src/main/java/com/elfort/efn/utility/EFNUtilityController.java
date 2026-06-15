package com.elfort.efn.utility;

import com.elfort.efn.utility.models.DispenseRequest;
import com.elfort.efn.utility.models.DispenseResponse;
import com.elfort.efn.utility.models.TransactionStatusResponse;
import com.elfort.efn.utility.models.ValidateRequest;
import com.elfort.efn.utility.models.ValidateResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Spring REST controller exposing the three EFN Utility endpoints.
 *
 * <p>All requests are pre-authenticated by {@link EFNSignatureFilter} before
 * reaching these handlers. You do not need to perform signature verification here.
 *
 * <h2>Endpoints</h2>
 * <ul>
 *   <li>{@code POST /efn/v1/utility/validate} — validate customer account</li>
 *   <li>{@code POST /efn/v1/utility/dispense} — dispense value token</li>
 *   <li>{@code GET  /efn/v1/utility/transaction/{efnReference}/status} — query transaction</li>
 * </ul>
 */
@RestController
@RequestMapping("/efn/v1/utility")
public class EFNUtilityController {

    private final EFNUtilityAdapter adapter;

    public EFNUtilityController(EFNUtilityAdapter adapter) {
        this.adapter = adapter;
    }

    /**
     * Validate a customer's account or meter number.
     *
     * <p>Example request:
     * <pre>{@code
     * POST /efn/v1/utility/validate
     * {
     *   "customer_ref": "12345678901",
     *   "utility_category": "ELECTRICITY"
     * }
     * }</pre>
     */
    @PostMapping("/validate")
    public ResponseEntity<ValidateResponse> validate(@RequestBody ValidateRequest req) {
        ValidateResponse response = adapter.validateCustomer(req);
        return ResponseEntity.ok(response);
    }

    /**
     * Dispense value (token, units, credit) after payment confirmation.
     *
     * <p>Example request:
     * <pre>{@code
     * POST /efn/v1/utility/dispense
     * {
     *   "customer_ref": "12345678901",
     *   "amount": 5000.00,
     *   "currency": "NGN",
     *   "efn_reference": "EFN-TXN-20240601-ABCDEF"
     * }
     * }</pre>
     */
    @PostMapping("/dispense")
    public ResponseEntity<DispenseResponse> dispense(@RequestBody DispenseRequest req) {
        DispenseResponse response = adapter.dispenseValue(req);
        return ResponseEntity.ok(response);
    }

    /**
     * Query the outcome of a previous dispense transaction.
     *
     * <p>Example: {@code GET /efn/v1/utility/transaction/EFN-TXN-20240601-ABCDEF/status}
     */
    @GetMapping("/transaction/{efnReference}/status")
    public ResponseEntity<TransactionStatusResponse> status(@PathVariable String efnReference) {
        TransactionStatusResponse response = adapter.transactionStatus(efnReference);
        return ResponseEntity.ok(response);
    }
}
