import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import current_app
from utils.security import verify_flutterwave_webhook
def get_retry_session():
    s = requests.Session(); r = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504]); s.mount("http://", HTTPAdapter(max_retries=r)); s.mount("https://", HTTPAdapter(max_retries=r)); return s
class PaymentService:
    def __init__(self, app=None):
        self.app = app; self.session = get_retry_session()
        if app: self.init_app(app)
    def init_app(self, app): self.secret_key = app.config['FLUTTERWAVE_SECRET_KEY']; self.base_url = 'https://api.flutterwave.com/v3'
    def initiate_payment(self, phone: str, amount: int, tx_ref: str) -> dict:
        try:
            res = self.session.post(f"{self.base_url}/payments", json={"tx_ref": tx_ref, "amount": amount, "currency": "UGX", "redirect_url": "https://your-app.com/callback", "payment_options": "mobilemoneyuganda", "customer": {"phone_number": phone}}, headers={"Authorization": f"Bearer {self.secret_key}"}, timeout=10)
            data = res.json()
            return {'success': True, 'checkout_url': data['data']['link']} if data['status'] == 'success' else {'success': False, 'error': data.get('message')}
        except Exception as e: current_app.logger.error(f"Payment init failed: {e}"); return {'success': False, 'error': str(e)}
    def verify_webhook_signature(self, sig: str) -> bool: return verify_flutterwave_webhook(sig)
