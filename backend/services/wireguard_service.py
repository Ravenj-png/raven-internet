class WireGuardService:
    def __init__(self, app=None): self.app=app
    def generate_config(self, priv, pub, ip, server_pub, endpoint):
        return f"[Interface]\nPrivateKey = {priv}\nAddress = {ip}\nDNS = 8.8.8.8\n\n[Peer]\nPublicKey = {server_pub}\nEndpoint = {endpoint}:{self.app.config['MIKROTIK_WG_PORT']}\nAllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 25"
