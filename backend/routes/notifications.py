from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import Session
from datetime import datetime, timedelta
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api')
@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    sid = get_jwt().get('session_id')
    s = Session.query.get(sid)
    if not s or not s.is_active: return jsonify([]), 200
    if s.student.is_blocked: return jsonify([]), 200
    alerts = []
    if s.remaining_mb < 200: alerts.append({'message': f"⚠️ Low data: {s.remaining_mb}MB", 'type': 'warning'})
    time_left = s.expires_at - datetime.utcnow()
    if timedelta(hours=0) < time_left < timedelta(hours=2): alerts.append({'message': f"⏰ Expires in {time_left.seconds//3600}h", 'type': 'warning'})
    return jsonify(alerts), 200
