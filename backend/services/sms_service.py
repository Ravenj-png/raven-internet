import requests
from flask import current_app
class SMSService:
    def __init__(self, app=None): self.app=app; if app: self.init_app(app)
    def init_app(self, app): self.key=app.config['YOOLA_SMS_API_KEY']; self.sender=app.config['YOOLA_SMS_SENDER_ID']; self.url=app.config.get('YOOLA_SMS_BASE_URL','https://api.yoola.com/v1')
    def send_voucher_sms(self, phone, code, plan):
        if not self.key: return True
        msg=f"Raven VPN: Code {code}. Valid {plan['duration']} • {plan['data']} • {plan['speed']}"
        try:
            r=requests.post(f"{self.url}/sms/send", json={'api_key':self.key,'to':phone,'message':msg,'sender_id':self.sender}, timeout=10)
            return r.status_code==200
        except: return False
