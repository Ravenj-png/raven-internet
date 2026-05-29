import os, urllib.parse
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Student, Session, Voucher
from services.wireguard_service import WireGuardService
from services.ip_allocator import IPAllocator
from utils.validators import validate_voucher_code, validate_phone, sanitize_input
from utils.security import generate_jwt_token, hash_phone, sign_wg_config, generate_wg_keypair
from datetime import datetime, timedelta

vouchers_bp = Blueprint('vouchers', __name__, url_prefix='/api/vouchers')

@vouchers_bp.route('/activate', methods=['POST'])
@limiter.limit("5 per minute")
def activate_voucher():
    try:
        data = request.get_json() or {}
        code = sanitize_input(data.get('voucher_code', '')).upper()
        if not validate_voucher_code(code): return jsonify({'message': 'Invalid format'}), 400
        
        voucher = Voucher.query.filter_by(code=code, is_used=False).first()
        if not voucher or voucher.expires_at < datetime.utcnow(): return jsonify({'message': 'Invalid/expired'}), 404
        
        # ← FIX: Phone is optional - look up from voucher if not provided
        phone = data.get('phone_number')
        if not phone:
            if voucher.used_by:
                student = Student.query.get(voucher.used_by)
                phone = student.phone_display if student else "0000000000"
            else:
                phone = "0000000000"  # Placeholder for voucher-only activation
        
        student = Student.query.filter_by(phone_hash=hash_phone(phone)).first()
        if not student: student = Student(); student.set_phone(phone); db.session.add(student); db.session.flush()
        
        client_priv, client_pub = generate_wg_keypair()
        allowed_ip = IPAllocator.assign_ip()
        
        server_pub = current_app.config['WG_SERVER_PUBLIC_KEY']
        endpoint = urllib.parse.urlparse(current_app.config['LAPTOP_API_URL']).hostname
        
        config_text = f"""[Interface]
PrivateKey = {client_priv}
Address = {allowed_ip}
DNS = 8.8.8.8

[Peer]
PublicKey = {server_pub}
Endpoint = {endpoint}:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25"""
        
        config_signed, signature = sign_wg_config(config_text, current_app.config['WG_SIGNING_PRIVATE_KEY_PEM'])
        
        session = Session(student_id=student.id, session_token=os.urandom(24).hex(), voucher_code=code, public_key=client_pub, allowed_ip=allowed_ip, total_mb=voucher.total_mb, expires_at=datetime.utcnow() + timedelta(hours=voucher.duration_hours))
        
        # ← FIX: Check wg.add_peer() result and rollback on failure
        wg = WireGuardService(current_app)
        wg_result = wg.add_peer(client_pub, allowed_ip, code)
        
        if not wg_result['success']:
            current_app.logger.error(f"Failed to add peer: {wg_result.get('error')}")
            db.session.rollback()
            return jsonify({'message': 'Failed to provision VPN. Please try again.', 'error': wg_result.get('error')}), 503
        
        voucher.is_used = True; voucher.used_by = student.id; voucher.used_at = datetime.utcnow()
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'access_token': generate_jwt_token(student.phone_display, str(session.id)),
            'expires_at': session.expires_at.isoformat(),
            'config': config_signed,
            'signature': signature
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Activate failed: {e}"); db.session.rollback()
        return jsonify({'message': 'Activation failed'}), 500
