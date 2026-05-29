# 🦅 Raven Student - Production Ready

## 🔑 Key Generation (One-Time)

### Ed25519 Signing Keys
```bash
# Generate private key
openssl genpkey -algorithm ed25519 -out backend_wg_private.pem

# Extract RAW 32-byte public key for APK (CRITICAL: not DER)
python3 << 'EOF'
from cryptography.hazmat.primitives import serialization

with open('backend_wg_private.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

public_key = private_key.public_key()
raw_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

with open('apk/assets/wg_public_key.raw', 'wb') as f:
    f.write(raw_bytes)

print(f"✅ Raw 32-byte key: {raw_bytes.hex()}")
print(f"✅ Length: {len(raw_bytes)} bytes")
EOF

# WireGuard server keys
wg genkey | sudo tee /etc/wireguard/privatekey | wg pubkey | sudo tee /etc/wireguard/publickey
```

### Tailscale Setup (Recommended)
```bash
# On laptop
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4  # Use this IP in LAPTOP_API_URL
```

## 🚀 Deploy
1. **Backend**: Render → Root: `backend` → Add env vars
2. **PWA**: GitHub Pages → Source: `/pwa`
3. **APK**: `flutter build apk --release --split-per-abi`
4. **Laptop**: `sudo ./setup.sh` → Start services
```
