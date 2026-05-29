import requests, urllib.parse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import current_app
def get_retry_session():
    s = requests.Session(); r = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504]); s.mount("http://", HTTPAdapter(max_retries=r)); s.mount("https://", HTTPAdapter(max_retries=r)); return s
class WireGuardService:
    def __init__(self, app=None):
        self.app = app; self.session = get_retry_session()
        if app: self.init_app(app)
    def init_app(self, app):
        self.base_url = app.config['LAPTOP_API_URL']
        parsed = urllib.parse.urlparse(self.base_url)
        self.endpoint_host = parsed.hostname or 'localhost'
        self.headers = {'Content-Type': 'application/json', 'X-Auth-Token': app.config['LAPTOP_API_TOKEN']}
    def health_check(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/health", headers=self.headers, timeout=5)
            return response.status_code == 200
        except: return False
    def add_peer(self, public_key: str, allowed_ip: str, voucher_code: str) -> dict:
        if not self.health_check():
            current_app.logger.error("Laptop API unreachable")
            return {'success': False, 'error': 'VPN server unavailable'}
        try:
            res = self.session.post(f"{self.base_url}/api/add_peer", json={'public_key': public_key, 'allowed_ip': allowed_ip, 'voucher_code': voucher_code}, headers=self.headers, timeout=10)
            return {'success': res.status_code == 200, 'data': res.json()}
        except Exception as e: current_app.logger.error(f"Add peer failed: {e}"); return {'success': False, 'error': str(e)}
    def remove_peer(self, public_key: str) -> dict:
        try:
            res = self.session.post(f"{self.base_url}/api/remove_peer", json={'public_key': public_key}, headers=self.headers, timeout=10)
            return {'success': res.status_code == 200}
        except Exception as e: current_app.logger.error(f"Remove peer failed: {e}"); return {'success': False, 'error': str(e)}
    def get_peer_stats(self, public_key: str) -> dict:
        try:
            res = self.session.get(f"{self.base_url}/api/peer_stats", params={'public_key': public_key}, headers=self.headers, timeout=10)
            return {'success': res.status_code == 200, 'data': res.json()}
        except: return {'success': True, 'data': {'bytes_received': 0, 'bytes_sent': 0}}
