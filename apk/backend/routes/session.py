from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db, limiter
from models import Session
from services.wireguard_service import WireGuardService

session_bp = Blueprint('session', __name__, url_prefix='/api/session')

@session_bp.route('/status', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def status():
    sid = get_jwt().get('session_id')
    s = Session.query.get(sid)
    if not s or not s.is_active or s.is_revoked: return jsonify({'message': 'Invalid session'}), 401
    if s.is_expired(): s.is_active = False; db.session.commit(); return jsonify({'message': 'Expired'}), 403
    stats = WireGuardService(current_app).get_peer_stats(s.public_key)
    if stats['success']: 
        used = int((stats['data'].get('bytes_received',0)+stats['data'].get('bytes_sent',0))/(1024*1024))
        s.used_mb = min(used, s.total_mb); s.calculate_remaining(); db.session.commit()
    return jsonify({'success': True, 'remaining_mb': s.remaining_mb, 'total_mb': s.total_mb, 'expires_at': s.expires_at.isoformat()}), 200

@session_bp.route('/disconnect', methods=['POST'])
@jwt_required()
def disconnect():
    sid = get_jwt().get('session_id')
    s = Session.query.get(sid)
    if s: WireGuardService(current_app).remove_peer(s.public_key); s.is_active = False; db.session.commit()
    return jsonify({'success': True}), 200
