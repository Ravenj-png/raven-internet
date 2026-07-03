from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import Session
import datetime as dt

session_bp = Blueprint('session', __name__, url_prefix='/api/session')

@session_bp.route('/status', methods=['GET'])
@jwt_required()
def status():
    sid = get_jwt().get('session_id')
    s = Session.query.get(sid)
    
    if not s or not s.is_active:
        return jsonify({'active': False, 'message': 'Session not active'}), 200
    
    # ✅ Check if session has expired
    if s.expires_at < dt.datetime.utcnow():
        s.is_active = False
        db.session.commit()
        return jsonify({'active': False, 'message': 'Session expired'}), 200
    
    remaining_mb = s.total_mb - s.used_mb
    if remaining_mb <= 0:
        s.is_active = False
        db.session.commit()
        return jsonify({'active': False, 'message': 'Data used up'}), 200
    
    # ✅ Student blocked check
    if s.student.is_blocked:
        return jsonify({'active': False, 'message': 'Account blocked'}), 403
    
    return jsonify({
        'active': True,
        'remaining_mb': remaining_mb,
        'data_used_mb': s.used_mb,
        'total_mb': s.total_mb,
        'speed_mbps': s.speed_mbps,
        'expires_at': s.expires_at.isoformat()
    }), 200

@session_bp.route('/disconnect', methods=['POST'])
@jwt_required()
def disconnect():
    sid = get_jwt().get('session_id')
    s = Session.query.get(sid)
    if s:
        s.is_active = False
        db.session.commit()
    return jsonify({'success': True})
