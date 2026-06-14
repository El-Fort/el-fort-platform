
import * as crypto from 'crypto';
import { verifySignature } from '../src/security';

test('verifySignature returns true for valid signature', () => {
    const secret = 'test_secret';
    const ts = Math.floor(Date.now() / 1000).toString();
    const body = Buffer.from(JSON.stringify({ customer_ref: '123' }));
    const sig = 'v1=' + crypto.createHmac('sha256', secret).update(ts + '.' + body.toString()).digest('hex');
    expect(verifySignature(secret, ts, sig, body)).toBe(true);
});

test('verifySignature returns false for invalid signature', () => {
    const secret = 'test_secret';
    const ts = Math.floor(Date.now() / 1000).toString();
    const body = Buffer.from('{}');
    expect(verifySignature(secret, ts, 'v1=bad', body)).toBe(false);
});
