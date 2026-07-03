import os
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Student, Session, Voucher
from services.mikrotik_service import MikroTikService
from utils.validators import validate_voucher_code, sanitize_input
from utils.security import hash_phone, gen_jwt
from utils.constants import PLANS
import datetime as dt
import secrets, string

vouchers_bp = Blueprint('vouchers', __name__, url_prefix='/api/vouchers')

@vouchers_bp.route('/activate', methods=['POST'])
# @limiter.limit("5 per minute")   # UNCOMMENT LATER
# @limiter.limit("20 per hour")
def activate():
    d = request.json or {}
    code = sanitize_input(d.get('voucher_code', '')).upper()
    device_id = d.get('device_id', 'unknown_device')

    if not validate_voucher_code(code):
        return jsonify({'message': 'Invalid format'}), 400

    v = Voucher.query.filter_by(code=code, is_used=False).first()
    if not v or v.expires_at < dt.datetime.utcnow():
        return jsonify({'message': 'Invalid/Expired'}), 404

    # ---------- ONE‑DEVICE CHECK ----------
    existing_session = Session.query.filter_by(voucher_code=code).first()
    if existing_session:
        if existing_session.device_id != device_id:
            return jsonify({'message': 'This voucher is already in use on another device'}), 403

    # ---------- STUDENT ----------
    ph = d.get('phone_number', '0000000000')
    s = Student.query.filter_by(phone_hash=hash_phone(ph)).first()
    if not s:
        s = Student()
        s.set_phone(ph)
        db.session.add(s)
        db.session.flush()

    if s.is_blocked:
        return jsonify({'message': 'Blocked'}), 403

    plan = PLANS.get(v.plan_id)
    if not plan:
        return jsonify({'message': 'Invalid plan'}), 400

    # ---------- STACKING LOGIC ----------
    active_session = Session.query.filter_by(student_id=s.id, is_active=True).first()

    if active_session:
        # Extend expiry, add data, update speed
        new_expiry = active_session.expires_at + dt.timedelta(hours=plan['hours'])
        active_session.expires_at = new_expiry
        active_session.total_mb += plan['mb']
        if plan['speed'] > active_session.speed_mbps:
            active_session.speed_mbps = plan['speed']
        v.is_used = True
        db.session.commit()

        config = f"[Interface]\nPrivateKey = {active_session.public_key}\nAddress = {active_session.allowed_ip}\nDNS = 8.8.8.8\n\n[Peer]\nPublicKey = dummy\nEndpoint = dummy:51820\nAllowedIPs = 0.0.0.0/0"
        return jsonify({
            'success': True,
            'access_token': gen_jwt(s.phone_display, str(active_session.id)),
            'remaining_mb': active_session.total_mb - active_session.used_mb,
            'total_mb': active_session.total_mb,
            'speed_mbps': active_session.speed_mbps,
            'config': config,
            'expires_at': active_session.expires_at.isoformat()
        }), 200

    else:
        # NEW SESSION
        priv = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        pub = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        ip = f"10.0.0.{secrets.randbelow(254)+2}/32"

        new_session = Session(
            student_id=s.id,
            session_token=gen_jwt(s.phone_display, 'temp'),
            voucher_code=v.code,
            public_key=pub,
            allowed_ip=ip,
            total_mb=plan['mb'],
            used_mb=0,
            speed_mbps=plan['speed'],
            expires_at=dt.datetime.utcnow() + dt.timedelta(hours=plan['hours']),
            is_active=True,
            device_id=device_id
        )
        db.session.add(new_session)
        v.is_used = True
        db.session.commit()

        config = f"[Interface]\nPrivateKey = {priv}\nAddress = {ip}\nDNS = 8.8.8.8\n\n[Peer]\nPublicKey = {pub}\nEndpoint = dummy:51820\nAllowedIPs = 0.0.0.0/0"
        return jsonify({
            'success': True,
            'access_token': gen_jwt(s.phone_display, str(new_session.id)),
            'remaining_mb': new_session.total_mb,
            'total_mb': new_session.total_mb,
            'speed_mbps': new_session.speed_mbps,
            'config': config,
            'expires_at': new_session.expires_at.isoformat()
        }), 200
