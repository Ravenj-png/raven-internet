#!/bin/bash
set -e
echo "🦅 Setting up Raven Laptop..."
apt update && apt install -y wireguard python3-pip python3-venv iptables curl

wg genkey | sudo tee /etc/wireguard/privatekey | wg pubkey | sudo tee /etc/wireguard/publickey
chmod 600 /etc/wireguard/privatekey

IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
if [ -z "$IFACE" ]; then echo "⚠️  Could not detect default interface"; IFACE="enxPLACEHOLDER"; fi

cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/privatekey)
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o $IFACE -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o $IFACE -j MASQUERADE
EOF

echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && sysctl -p

cd "$(dirname "$0")"
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

mkdir -p systemd
cp systemd/raven-laptop-api.service /etc/systemd/system/ 2>/dev/null || true
cp systemd/raven-cleanup.timer /etc/systemd/system/ 2>/dev/null || true
systemctl daemon-reload

systemctl enable wg-quick@wg0 raven-laptop-api 2>/dev/null || true

echo "✅ Setup complete. Next:"
echo "1. Edit .env with LAPTOP_API_TOKEN"
echo "2. Forward UDP 51820 and TCP 5001 on your router"
echo "3. Start services: sudo systemctl start wg-quick@wg0 && sudo systemctl start raven-laptop-api"
echo "4. Test: curl http://localhost:5001/health"
