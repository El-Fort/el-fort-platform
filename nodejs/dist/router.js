"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.makeRouter = void 0;
const express_1 = require("express");
const security_1 = require("./security");
function sigError(res) {
    res.status(401).json({ success: false, message: "Invalid or expired signature" });
}
function checkSig(req, apiSecret) {
    return (0, security_1.verifySignature)(apiSecret, req.headers["x-efn-timestamp"] ?? "", req.rawBody ?? Buffer.alloc(0), req.headers["x-efn-signature"] ?? "");
}
function makeRouter(adapter, apiSecret) {
    const router = (0, express_1.Router)();
    // Capture raw body for signature verification
    router.use((0, express_1.raw)({ type: "*/*", limit: "1mb" }));
    router.use((req, _res, next) => {
        if (Buffer.isBuffer(req.body))
            req.rawBody = req.body;
        next();
    });
    router.post("/authorizations", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.authorize(JSON.parse(req.rawBody));
        res.json(result);
    });
    router.post("/authorizations/:id/capture", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.capture(req.params.id, JSON.parse(req.rawBody));
        res.json(result);
    });
    router.post("/authorizations/:id/reversal", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.reverse(req.params.id, JSON.parse(req.rawBody));
        res.json(result);
    });
    router.post("/debit", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.debit(JSON.parse(req.rawBody));
        res.json(result);
    });
    router.post("/credit", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.credit(JSON.parse(req.rawBody));
        res.json(result);
    });
    router.post("/balance", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.balance(JSON.parse(req.rawBody));
        res.json(result);
    });
    router.post("/account-enquiry", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.accountEnquiry(JSON.parse(req.rawBody));
        res.json(result);
    });
    router.get("/transaction/:ref/status", async (req, res) => {
        const result = await adapter.transactionStatus(req.params.ref);
        res.json(result);
    });
    router.post("/consent-otp", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.consentOtp(JSON.parse(req.rawBody));
        res.json(result);
    });
    router.post("/consent-verify", async (req, res) => {
        if (!checkSig(req, apiSecret))
            return sigError(res);
        const result = await adapter.consentVerify(JSON.parse(req.rawBody));
        res.json(result);
    });
    router.get("/health", (_req, res) => res.json({ status: "ok" }));
    return router;
}
exports.makeRouter = makeRouter;
//# sourceMappingURL=router.js.map