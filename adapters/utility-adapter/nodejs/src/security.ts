
import * as crypto from 'crypto';

export function verifySignature(secret: string, timestamp: string, signature: string, body: Buffer, window: number = 300): boolean {
    try {
        if (Math.abs(Date.now() / 1000 - parseInt(timestamp)) > window) return false;
        const expected = crypto.createHmac('sha256', Buffer.from(secret)).update(timestamp + '.' + body.toString()).digest('hex');
        const provided = signature.replace('v1=', '');
        if (expected.length !== provided.length) return false;
        return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(provided));
    } catch {
        return false;
    }
}
