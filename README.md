
---

## 🌍 Regional Architecture (E.164 Standard)

All phone numbers are stored in E.164 format (`+256...`, `+254...`, etc.) for seamless cross-border scaling.

| Country | Prefix | Currency | Payment Gateway | Status |
|---------|--------|----------|-----------------|--------|
| 🇺🇬 Uganda | `+256` | UGX | Pesapal (Official API v3) | ✅ Live |
| 🇰🇪 Kenya | `+254` | KES | Pesapal (Official API v3) | ✅ Live |
| 🇹🇿 Tanzania | `+255` | TZS | Pesapal (Official API v3) | ✅ Live |
| 🇷🇼 Rwanda | `+250` | RWF | Pesapal (Official API v3) | ✅ Live |
| 🇸🇸 South Sudan | `+211` | SSP | Pesapal (Official API v3) | ✅ Live |

✅ Adding a new country only requires a config update. No code rewrites.

---

## 💰 Plan Pricing (Base: UGX)

| Tier | Data | Speed | Duration | Price (UGX) |
|------|------|-------|----------|-------------|
| 🟦 **Basic** | 20 GB | 1 Mbps | Monthly | **15,000** |
| 🟪 **Premium** | 30 GB | 2 Mbps | Monthly | 25,000 |
| 🟨 **PRO 30** | 30 GB | 4 Mbps | 2 Months | 30,000 |
| 🟨 **PRO 60** | 60 GB | 10 Mbps | 2 Months | 95,000 |
| 🟧 **Annual 250** | 250 GB | 1 Mbps | 12 Months | 300,000 |
| 🟣 **Annual Unlimited** | Unlimited | 3 Mbps | 12 Months | 600,000 |

*(PRO & Annual require manual WhatsApp approval. Basic/Premium are instant.)*

---

## 🔄 Auto-Switch Architecture (Test ↔ Live)

| Mode | Trigger Condition | Behavior |
|------|-------------------|----------|
| 🟡 **TEST MODE** | `MIKROTIK_HOST` empty OR `DUMMY_PASSWORD` exists OR router unreachable | • Skips Pesapal → instant mock success<br>• Generates `TEST-XXXXXXX` vouchers<br>• SMS logged only<br>• Admin shows 🟡 TEST MODE & disables real controls |
| 🟢 **LIVE MODE** | `MIKROTIK_HOST` set + router responds + `DUMMY_PASSWORD` removed | • Real Pesapal payments<br>• Real `RVN-XXXXXXX` vouchers<br>• Real SMS & MikroTik provisioning<br>• Full admin controls active |

---

## 🛠️ Technology Stack

### Backend
- **Flask** – Python web framework
- **PostgreSQL** – Primary database
- **SQLAlchemy** – ORM
- **JWT** – Authentication
- **WebSockets** – Real-time updates
- **Flask-Limiter** – Rate limiting

### Frontend
- **PWA / APK** – Mobile-first client
- **JavaScript** – Client-side logic
- **HTML5 / CSS3** – UI

### Integrations
- **Pesapal API v3** – Payment processing
- **MikroTik RouterOS** – Provisioning
- **SMS Gateway** – Notifications

### DevOps
- **GitHub** – Source control
- **Render** – Hosting
- **Docker** – Containerization (optional)

---

## 🔒 Enterprise Safeguards

| Feature | Purpose |
|---------|---------|
| **Idempotency Keys** | Prevents double-charges from network retries |
| **Amount/Plan Matching** | Hardcoded price map stops exploitation |
| **E.164 Validation** | Regex enforces international format across all regions |
| **Webhook HMAC** | Validates payment callbacks with SHA256 signatures |
| **Timeout Handling** | 5s API / 12s Router → graceful `PENDING_REVIEW` fallback |
| **Rate Limiting** | `5/min` on purchase stops bot abuse |
| **Audit Logging** | Every action tracked with metadata for compliance |
| **Request ID** | Every response carries `X-Request-ID` for instant tracing |

---

## 💾 Backup & Recovery

- **Database:** Render automated backups every 6 hours (7-day retention)
- **Code:** GitHub primary + GitLab mirror
- **Env Vars:** Encrypted backup in password manager
- **Recovery:** 1-click DB restore via Render. 2-min code rollback.

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Ravenj-png/raven-internet.git
cd raven-internet/backend
pip install -r requirements.txt
