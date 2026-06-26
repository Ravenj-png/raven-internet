from librouteros import connect
from librouteros.exceptions import RouterOsApiException
from flask import current_app
import socket

class MikroTikService:
    def __init__(self, app=None):
        self.app = app
        self.conn = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.host = app.config['MIKROTIK_HOST']
        self.user = app.config['MIKROTIK_USERNAME']
        self.pw = app.config['MIKROTIK_PASSWORD']
        self.port = app.config['MIKROTIK_WG_PORT']
    
    def _connect(self):
        if self.conn:
            try:
                list(self.conn.path('system', 'resource').get())
                return self.conn
            except:
                self.conn = None
        try:
            self.conn = connect(host=self.host, username=self.user, password=self.pw, encoding='utf-8', port=8728, timeout=10)
            return self.conn
        except RouterOsApiException as e:
            current_app.logger.error(f"MT fail: {e}")
            raise
        except socket.timeout:
            current_app.logger.error("MT timeout")
            raise
    
    def add_peer(self, pub, ip, code, speed):
        try:
            api = self._connect()
            api.path('interface', 'wireguard', 'peers').add(interface='wg0', public_key=pub, allowed_address=f'{ip}/32', comment=code, persistent_keepalive='25')
            api.path('queue', 'simple').add(name=f'q-{code}', target=ip, max_limit=f'{speed}M/{speed}M', comment=f'{code}')
            return True
        except Exception as e:
            current_app.logger.error(f"MT add: {e}")
            return False
    
    def remove_peer(self, code):
        try:
            api = self._connect()
            for p in api.path('interface', 'wireguard', 'peers'):
                if p.get('comment') == code:
                    api.path('interface', 'wireguard', 'peers').remove(p['.id'])
                    break
            for q in api.path('queue', 'simple'):
                if q.get('name') == f'q-{code}':
                    api.path('queue', 'simple').remove(q['.id'])
                    break
            return True
        except Exception as e:
            current_app.logger.error(f"MT rem: {e}")
            return False
    
    def health_check(self):
        try:
            return any(i.get('name') == 'wg0' for i in self._connect().path('interface', 'wireguard').get())
        except:
            return False
