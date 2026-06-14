import { Router, Request, Response, raw } from "express";
import { verifySignature } from "./security";
import { EFNBankAdapter } from "./adapter";

function sigError(res: Response) {
  res.status(401).json({ success: false, message: "Invalid or expired signature" });
}

function checkSig(req: Request, apiSecret: string): boolean {
  return verifySignature(
    apiSecret,
    req.headers["x-efn-timestamp"] as string ?? "",
    (req as any).rawBody ?? Buffer.alloc(0),
    req.headers["x-efn-signature"] as string ?? "",
  );
}

export function makeRouter(adapter: EFNBankAdapter, apiSecret: string): Router {
  const router = Router();

  // Capture raw body for signature verification
  router.use(raw({ type: "*/*", limit: "1mb" }));
  router.use((req: any, _res, next) => {
    if (Buffer.isBuffer(req.body)) req.rawBody = req.body;
    next();
  });

  router.post("/authorizations", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.authorize(JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.post("/authorizations/:id/capture", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.capture(req.params.id, JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.post("/authorizations/:id/reversal", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.reverse(req.params.id, JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.post("/debit", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.debit(JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.post("/credit", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.credit(JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.post("/balance", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.balance(JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.post("/account-enquiry", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.accountEnquiry(JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.get("/transaction/:ref/status", async (req, res) => {
    const result = await adapter.transactionStatus(req.params.ref);
    res.json(result);
  });

  router.post("/consent-otp", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.consentOtp(JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.post("/consent-verify", async (req, res) => {
    if (!checkSig(req, apiSecret)) return sigError(res);
    const result = await adapter.consentVerify(JSON.parse((req as any).rawBody));
    res.json(result);
  });

  router.get("/health", (_req, res) => res.json({ status: "ok" }));

  return router;
}
