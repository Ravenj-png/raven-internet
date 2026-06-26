# 🦅 Raven VPN - Production Ready

## Deploy
1. **Backend**: Render → Root: `backend` → Add ALL env vars → Deploy
2. **PWA**: GitHub Pages → Source: `/pwa`
3. **Admin**: Access via direct URL (token-protected)
4. **APK**: `cd apk && flutter pub get && flutter build apk --release --split-per-abi`
5. **MikroTik**: SSH → `/import mikrotik/setup.rsc`

## Launch Checklist
- [ ] Run `cd backend && flask db migrate -m "Init" && flask db upgrade`
- [ ] Add ALL env vars from `.env.example` to Render
- [ ] Test: PWA → Pay → APK → Connect → Admin Dashboard
- [ ] Monitor via `/health` + UptimeRobot
