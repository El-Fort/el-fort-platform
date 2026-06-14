"""EFN Subscriptions Python SDK"""
import hashlib, hmac, json, time
import requests

BASE_URL = 'https://smart-terminal.el-fort.com'

class EFNError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class _Resource:
    def __init__(self, client): self._c = client
    def _req(self, method, path, **kw):
        r = requests.request(method, f"{self._c.base_url}{path}",
            headers={'Authorization': f'Bearer {self._c.api_key}',
                     'Content-Type': 'application/json', **kw.pop('headers', {})},
            **kw, timeout=30)
        if not r.ok:
            raise EFNError(r.json().get('error', r.text), r.status_code)
        return r.json()

class Plans(_Resource):
    def create(self, **kw): return self._req('POST', '/efn/api/subscriptions/plans/', json=kw)
    def list(self):         return self._req('GET',  '/efn/api/subscriptions/plans/')
    def get(self, id):      return self._req('GET',  f'/efn/api/subscriptions/plans/{id}/')
    def update(self, id, **kw): return self._req('PATCH', f'/efn/api/subscriptions/plans/{id}/', json=kw)
    def archive(self, id):  return self._req('DELETE', f'/efn/api/subscriptions/plans/{id}/')
    def payment_link(self, id): return self._req('GET', f'/efn/api/subscriptions/plans/{id}/payment-link/')

class Subscriptions(_Resource):
    def list(self, uan):    return self._req('GET', f'/efn/api/subscriptions/my/?uan={uan}')
    def get(self, id, uan): return self._req('GET', f'/efn/api/subscriptions/my/{id}/?uan={uan}')
    def cancel(self, id, uan, immediate=False):
        return self._req('POST', f'/efn/api/subscriptions/my/{id}/cancel/', json={'uan': uan, 'immediate': immediate})
    def pause(self, id, uan, resume_at=None):
        return self._req('POST', f'/efn/api/subscriptions/my/{id}/pause/', json={'uan': uan, 'resume_at': resume_at})

class Webhooks:
    @staticmethod
    def verify(payload: bytes, signature: str, secret: str) -> bool:
        expected = 'sha256=' + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    @staticmethod
    def construct_event(payload: bytes, signature: str, secret: str) -> dict:
        if not Webhooks.verify(payload, signature, secret):
            raise EFNError('Invalid webhook signature')
        return json.loads(payload)

class Analytics(_Resource):
    def get(self): return self._req('GET', '/efn/api/subscriptions/merchant/analytics/')

class EFNClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL):
        self.api_key  = api_key
        self.base_url = base_url.rstrip('/')
        self.plans         = Plans(self)
        self.subscriptions = Subscriptions(self)
        self.webhooks      = Webhooks()
        self.analytics     = Analytics(self)
