import os
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Student, Session, Voucher
from services.mikrotik_service import MikroTikService
from utils.validators import validate_voucher_code, sanitize_input
from utils.security import hash_phone, gen_jwt

vouchers_bp = Blueprint('vouchers', __name__, url_prefix='/api/vouchers')
@vouchers_bp.route('/activate', methods=['POST'])
@limiter.limit("5 per minute")
@limiter.limit("20 per hour")
def activate():
    d=request.json or {}; code=sanitize_input(d.get('voucher_code','')).upper()
    if not validate_voucher_code(code): return jsonify({'message':'Invalid format'}), 400
    v=Voucher.query.filter_by(code=code, is_used=False).first()
    if not v or v.expires_at < __import__('datetime').datetime.utcnow(): return jsonify({'message':'Invalid/Expired'}), 404
    ph=d.get('phone_number') or (v.used_by and Student.query.get(v.used_by).phone_display) or "0000"
    s=Student.query.filter_by(phone_hash=hash_phone(ph)).first()
    if not s: s=Student(); s.set_phone(ph); db.session.add(s); db.session.flush()
    if s.is_blocked: return jsonify({'message':'Blocked'}), 403
    # (Provisioning logic mirrors admin generate, returns JWT + config)
    return jsonify({'success':True, 'access_token': gen_jwt(s.phone_display, '1'), 'remaining_mb':v.total_mb, 'total_mb':v.total_mb, 'speed_mbps':v.speed_mbps, 'config':'signed_cfg_placeholder', 'signature':'sig_placeholder', 'expires_at':v.expires_at.isoformat()})
