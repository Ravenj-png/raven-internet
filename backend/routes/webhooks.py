import os, urllib.parse
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Session, Transaction
from services.wireguard_service import WireGuardService
from services.ip_allocator import IPAllocator
from services.payment_service import PaymentService
from utils.security import generate_jwt_token, hash_phone, sign_wg_config, generate_wg_keypair
from datetime import datetime, timedelta

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhook')

@webhooks_bp.route('/flutterwave', methods=['POST'])
def flutterwave():
    sig = request.headers.get('verif-hash', '')
    if not PaymentService(current_app).verify_webhook_signature(sig): return jsonify({'message': 'Invalid sig'}), 401
    data = request.json or {}
    tx_ref = data.get('tx_ref')
    if not tx_ref: return jsonify({'message': 'Missing tx_ref'}), 400
    txn = db.session.query(Transaction).with_for_update().filter_by(tx_ref=tx_ref).first()
    if not txn: return jsonify({'message': 'Not found'}), 404
    if txn.status == 'successful': return jsonify({'message': 'Already processed'}), 200
    txn.status = data.get('status', 'failed')
    if txn.status == 'successful':
        txn.paid_at = datetime.utcnow()
        student = txn.student; plan_id = txn.plan_id
        plan = {'daily': {'mb': 1024, 'hours': 24}, 'weekly': {'mb': 7168, 'hours': 168}}.get(plan_id, {'mb': 1024, 'hours': 24})
        priv, pub = generate_wg_keypair()
        ip = IPAllocator.assign_ip()
        endpoint = urllib.parse.urlparse(current_app.config['LAPTOP_API_URL']).hostname
        config_text = f"""[Interface]
PrivateKey = {priv}
Address = {ip}
DNS = 8.8.8.8

[Peer]
PublicKey = {current_app.config['WG_SERVER_PUBLIC_KEY']}
Endpoint = {endpoint}:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25"""
        cfg_signed, sig_hex = sign_wg_config(config_text, current_app.config['WG_SIGNING_PRIVATE_KEY_PEM'])
        s = Session(student_id=student.id, session_token=os.urandom(24).hex(), voucher_code=f"AUTO_{tx_ref[-6:]}", public_key=pub, allowed_ip=ip, total_mb=plan['mb'], expires_at=datetime.utcnow() + timedelta(hours=plan['hours']))
        wg = WireGuardService(current_app)
        if not wg.health_check():
            current_app.logger.error("Laptop unreachable during webhook")
            db.session.rollback()
            return jsonify({'message': 'VPN server unavailable'}), 503
        wg_result = wg.add_peer(pub, ip, s.voucher_code)
        if not wg_result['success']:
            current_app.logger.error(f"Peer addition failed in webhook: {wg_result.get('error')}")
            db.session.rollback()
            return jsonify({'message': 'Failed to provision VPN'}), 503
        db.session.add(s); db.session.commit()
        return jsonify({'success': True, 'access_token': generate_jwt_token(student.phone_display, str(s.id)), 'config': cfg_signed, 'signature': sig_hex}), 200
    db.session.commit()
    return jsonify({'message': 'Processed'}), 200
