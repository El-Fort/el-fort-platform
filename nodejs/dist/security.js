"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.verifySignature = void 0;
const crypto_1 = require("crypto");
const REPLAY_WINDOW = 300; // seconds
function verifySignature(apiSecret, timestamp, rawBody, signature) {
    const ts = parseInt(timestamp, 10);
    if (isNaN(ts))
        return false;
    if (Math.abs(Date.now() / 1000 - ts) > REPLAY_WINDOW)
        return false;
    const body = Buffer.isBuffer(rawBody) ? rawBody : Buffer.from(rawBody);
    const message = Buffer.concat([Buffer.from(timestamp + "."), body]);
    const expected = "v1=" + (0, crypto_1.createHmac)("sha256", apiSecret).update(message).digest("base64");
    try {
        return (0, crypto_1.timingSafeEqual)(Buffer.from(expected), Buffer.from(signature));
    }
    catch {
        return false;
    }
}
exports.verifySignature = verifySignature;
//# sourceMappingURL=security.js.map