import { createHmac, timingSafeEqual } from "crypto";

const REPLAY_WINDOW = 300; // seconds

export function verifySignature(
  apiSecret: string,
  timestamp: string,
  rawBody: Buffer | string,
  signature: string
): boolean {
  const ts = parseInt(timestamp, 10);
  if (isNaN(ts)) return false;
  if (Math.abs(Date.now() / 1000 - ts) > REPLAY_WINDOW) return false;

  const body = Buffer.isBuffer(rawBody) ? rawBody : Buffer.from(rawBody);
  const message = Buffer.concat([Buffer.from(timestamp + "."), body]);
  const expected = "v1=" + createHmac("sha256", apiSecret).update(message).digest("base64");

  try {
    return timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
  } catch {
    return false;
  }
}
