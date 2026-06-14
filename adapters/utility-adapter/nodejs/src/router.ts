import { Router, Request, Response, raw } from 'express';
import { EFNUtilityAdapter } from './adapter';
import { verifySignature } from './security';

/**
 * Creates an Express router that exposes the three required EFN Utility endpoints:
 *
 *  POST /efn/v1/utility/validate                         - Validate a customer account
 *  POST /efn/v1/utility/dispense                         - Dispense value / tokens
 *  GET  /efn/v1/utility/transaction/:ref/status          - Transaction status lookup
 *
 * Mount this in your Express app:
 *   app.use(makeRouter(new MyAdapter(), 'your_efn_secret'));
 */
export function makeRouter(adapter: EFNUtilityAdapter, secret: string): Router {
    const router = Router();

    // Use raw body parser so we can verify the HMAC signature
    router.use(raw({ type: '*/*' }));

    function authenticate(req: Request, res: Response): Buffer | null {
        const rawBody: Buffer = req.body instanceof Buffer ? req.body : Buffer.from('');
        const ts = (req.headers['x-efn-timestamp'] as string) || '0';
        const sig = (req.headers['x-efn-signature'] as string) || '';
        if (!verifySignature(secret, ts, sig, rawBody)) {
            res.status(401).json({ error: 'Invalid EFN signature or expired timestamp' });
            return null;
        }
        return rawBody;
    }

    /** POST /efn/v1/utility/validate */
    router.post('/efn/v1/utility/validate', async (req: Request, res: Response) => {
        const body = authenticate(req, res);
        if (!body) return;
        const result = await adapter.validateCustomer(JSON.parse(body.toString()));
        res.json(result);
    });

    /** POST /efn/v1/utility/dispense */
    router.post('/efn/v1/utility/dispense', async (req: Request, res: Response) => {
        const body = authenticate(req, res);
        if (!body) return;
        const result = await adapter.dispenseValue(JSON.parse(body.toString()));
        res.json(result);
    });

    /** GET /efn/v1/utility/transaction/:ref/status */
    router.get('/efn/v1/utility/transaction/:ref/status', async (req: Request, res: Response) => {
        const body = authenticate(req, res);
        if (!body) return;
        const result = await adapter.transactionStatus(req.params.ref);
        res.json(result);
    });

    return router;
}
