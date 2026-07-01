# 🦅 Raven Internet Platform
**Version:** R V1.0.1  
**Status:** 🟢 Production Ready (Auto-Switch Test/Live Architecture)  
**Region:** East Africa (UG, KE, TZ)  

---

## 📖 Overview
Raven Internet is a full-stack ISP management platform built for students and heavy internet users. It combines a fast PWA/APK client, secure Pesapal payments, MikroTik router provisioning, and a unique **Test/Live auto-switch architecture** that requires zero code changes to deploy or test.  

The platform also introduces **Rune**, an upcoming English-like programming language designed to make coding accessible to beginners while remaining powerful for professionals.

---

## ✨ Core Features
| Feature | Description |
|---------|-------------|
| 🌐 **PWA + APK** | Installable web app + native Android client (Flutter) |
| 💳 **Pesapal Payments** | Secure mobile money & card processing (Sandbox/Live auto-detect) |
| 🔌 **MikroTik Failover** | Router online = LIVE provisioning. Router offline = safe TEST simulation |
| ️ **Admin Panel** | Token-protected dashboard. Dormant in test mode, fully active in live |
| ⚡ **Rune Language** | English-like syntax showcase. Full compiler launching Q1 2027 |
|  **WhatsApp Community** | Broadcast channel + support group integrated in-app |
|  **Security** | JWT auth, HMAC webhooks, rate limiting, phone hashing, zero-log policy |
| 📊 **Analytics** | Anonymous visit tracking, device detection, revenue & usage stats |

---

## 💰 Plan Pricing
| Tier | Data | Speed | Duration | Price (UGX) |
|------|------|-------|----------|-------------|
| 🟦 **Basic** | 20 GB | 1 Mbps | Monthly | **15,000** |
| 🟪 **Premium** | 30 GB | 2 Mbps | Monthly | 25,000 |
| 🟨 **PRO 30** | 30 GB | 4 Mbps | 2 Months | 30,000 |
| 🟨 **PRO 60** | 60 GB | 10 Mbps | 2 Months | 95,000 |
|  **Annual 250** | 250 GB | 1 Mbps | 12 Months | 300,000 |
| 🟣 **Annual Unlimited** | Unlimited | 3 Mbps | 12 Months | 600,000 |

*(PRO & Annual plans require manual approval via WhatsApp. Basic/Premium are instant auto-activation.)*

---

## 🔄 Auto-Switch Architecture (Test ↔ Live)
Raven uses a **server-side environment detector**. No code changes are needed to switch modes.

| Mode | Trigger Condition | Behavior |
|------|-------------------|----------|
| 🟡 **TEST MODE** | `MIKROTIK_HOST` is empty OR `DUMMY_PASSWORD` exists OR router is unreachable | • Skips Pesapal → instant mock success<br>• Generates `TEST-XXXXXXX` vouchers<br>• SMS logged only (not sent)<br>• Admin shows 🟡 TEST MODE & disables real controls |
|  **LIVE MODE** | `MIKROTIK_HOST` is set + router responds on port 8728 + `DUMMY_PASSWORD` removed | • Real Pesapal payments<br>• Real `RVN-XXXXXXX` vouchers<br>• Real Yoola SMS & MikroTik provisioning<br>• Full admin controls active |

>  **You do NOT need to edit `.env` to toggle modes.** The backend reads your current state on every request and locks in automatically.

---

## 🗂️ Project Structure