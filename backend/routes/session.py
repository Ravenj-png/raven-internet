from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import Session

session_bp = Blueprint('session', __name__, url_prefix='/api/session')
@session_bp.route('/status', methods=['GET'])
@jwt_required()
def status():
    sid=get_jwt().get('session_id'); s=Session.query.get(sid)
    if not s or not s.is_active: return jsonify({'message':'Invalid'}), 401
    if s.student.is_blocked: return jsonify({'message':'Blocked'}), 403
    return jsonify({'success':True, 'remaining_mb':s.remaining_mb, 'speed_mbps':s.speed_mbps, 'expires_at':s.expires_at.isoformat()})
@session_bp.route('/disconnect', methods=['POST'])
@jwt_required()
def disconnect():
    sid=get_jwt().get('session_id'); s=Session.query.get(sid)
    if s: s.is_active=False; db.session.commit()
    return jsonify({'success':True})
