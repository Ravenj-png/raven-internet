import os
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Student, Session, Voucher
from services.mikrotik_service import MikroTikService
from utils.validators import validate_voucher_code, sanitize_input
from utils.security import hash_phone, gen_jwt
import datetime as dt

vouchers_bp = Blueprint('vouchers', __name__, url_prefix='/api/vouchers')

@vouchers_bp.route('/activate', methods=['POST'])
#@limiter.limit("5 per minute")
#@limiter.limit("20 per hour")
def activate():
    d = request.json or {}
    code = sanitize_input(d.get('voucher_code', '')).upper()
    
    if not validate_voucher_code(code):
        return jsonify({'message': 'Invalid format'}), 400
    
    v = Voucher.query.filter_by(code=code, is_used=False).first()
    if not v or v.expires_at < dt.datetime.utcnow():
        return jsonify({'message': 'Invalid/Expired'}), 404
    
    # ✅ REMOVED: phone number check — users just paste the code
    # ✅ Create a dummy student if needed (or skip entirely)
    # For simplicity, we'll create one with a dummy phone if not provided
    ph = d.get('phone_number', '0000000000')
    
    s = Student.query.filter_by(phone_hash=hash_phone(ph)).first()
    if not s:
        s = Student()
        s.set_phone(ph)
        db.session.add(s)
        db.session.flush()
    
    if s.is_blocked:
        return jsonify({'message': 'Blocked'}), 403
    
    # ✅ Mark voucher as used
    v.is_used = True
    db.session.commit()
    
    # ✅ Generate dummy config (for test mode)
    config = f"[Interface]\nPrivateKey = dummy\nAddress = 10.0.0.2/32\nDNS = 8.8.8.8\n\n[Peer]\nPublicKey = dummy\nEndpoint = dummy:51820\nAllowedIPs = 0.0.0.0/0"
    
    return jsonify({
        'success': True,
        'access_token': gen_jwt(s.phone_display, '1'),
        'remaining_mb': 1024,
        'total_mb': 1024,
        'speed_mbps': 1,
        'config': config,
        'signature': 'dummy_sig',
        'expires_at': v.expires_at.isoformat()
    }), 200
