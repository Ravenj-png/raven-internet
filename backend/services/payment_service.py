import requests, time, base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import current_app

class PaymentService:
    def __init__(self, app=None):
        self.app = app
        self.session = requests.Session()
        # Configure retries
        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self._token = None
        self._exp = 0
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.consumer_key = app.config['PESAPAL_CONSUMER_KEY']
        self.consumer_secret = app.config['PESAPAL_CONSUMER_SECRET']
        self.ipn = app.config['PESAPAL_IPN_URL']
        self.env = app.config['PESAPAL_ENVIRONMENT']
        self.base = 'https://cybqa.pesapal.com/pesapalv3' if self.env == 'cybqa' else 'https://www.pesapal.com'

    def _get_token(self):
        if self._token and time.time() < self._exp - 300:
            return self._token
        try:
            enc = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
            r = self.session.post(f"{self.base}/api/Authentication/RequestToken", 
                                  headers={"Authorization": f"Basic {enc}"},
                                  json={"consumer_key": self.consumer_key, "consumer_secret": self.consumer_secret})
            r.raise_for_status()
            d = r.json()
            self._token = d.get('token')
            self._exp = time.time() + 82800
            return self._token


        except requests.HTTPError as e:
            current_app.logger.error(f"Status: {e.response.status_code}")
            current_app.logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            current_app.logger.error(f"Pesapal token fail: {e}")
            raise
        #except Exception as e:
         #   current_app.logger.error(f"Pesapal token fail: {e}")
          #  raise

    def initiate_payment(self, phone, amount, ref, plan_id):
        try:
            tok = self._get_token()
            r = self.session.post(f"{self.base}/api/Transaction/SubmitTransactionRequest", 
                                  headers={"Authorization": f"Bearer {tok}"},
                                  json={"id": ref, "currency": "UGX", "amount": float(amount), 
                                        "description": f"Raven {plan_id}", "callback_url": self.ipn,
                                        "notification_id": "0",
                                        "billing_address": {"phone_number": phone, "country_code": "UG"}})
            r.raise_for_status()
            d = r.json()
            if d.get('message') == 'Success' and d.get('redirect_url'):
                return {'success': True, 'checkout_url': d['redirect_url']}
            return {'success': False, 'error': d.get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
