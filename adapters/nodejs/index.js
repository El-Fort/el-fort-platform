'use strict';
const https = require('https'), crypto = require('crypto');

class EFNError extends Error {
  constructor(message, statusCode) { super(message); this.statusCode = statusCode; }
}

function request(apiKey, baseUrl, method, path, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const url  = new URL(path, baseUrl);
    const opts = { method, hostname: url.hostname, path: url.pathname + url.search,
      headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json',
                 ...(data ? {'Content-Length': Buffer.byteLength(data)} : {}) }};
    const req = https.request(opts, res => {
      let raw = '';
      res.on('data', d => raw += d);
      res.on('end', () => {
        const parsed = JSON.parse(raw);
        if (res.statusCode >= 400) return reject(new EFNError(parsed.error || raw, res.statusCode));
        resolve(parsed);
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

class EFNClient {
  constructor({ apiKey, baseUrl = 'https://smart-terminal.el-fort.com' }) {
    this._key  = apiKey;
    this._base = baseUrl;
    const r = (m, p, b) => request(this._key, this._base, m, p, b);
    this.plans = {
      create:      (p) => r('POST',   '/efn/api/subscriptions/plans/', p),
      list:        ()  => r('GET',    '/efn/api/subscriptions/plans/'),
      get:         (id)=> r('GET',    `/efn/api/subscriptions/plans/${id}/`),
      paymentLink: (id)=> r('GET',    `/efn/api/subscriptions/plans/${id}/payment-link/`),
      archive:     (id)=> r('DELETE', `/efn/api/subscriptions/plans/${id}/`),
    };
    this.subscriptions = {
      list:   (uan)    => r('GET',  `/efn/api/subscriptions/my/?uan=${uan}`),
      cancel: (id,uan) => r('POST', `/efn/api/subscriptions/my/${id}/cancel/`, {uan}),
    };
    this.analytics = { get: () => r('GET', '/efn/api/subscriptions/merchant/analytics/') };
    this.webhooks = {
      verify(payload, signature, secret) {
        const expected = 'sha256=' + crypto.createHmac('sha256', secret).update(payload).digest('hex');
        return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
      },
      constructEvent(payload, signature, secret) {
        if (!this.verify(payload, signature, secret)) throw new EFNError('Invalid signature');
        return JSON.parse(payload);
      }
    };
  }
}

module.exports = { EFNClient, EFNError };
