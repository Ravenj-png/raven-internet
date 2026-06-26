from flask import Blueprint, request, jsonify
from extensions import db, limiter
from models import VisitorLog, Session, Transaction, FailedAttempt
from datetime import datetime, timedelta
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')
@analytics_bp.route('/track', methods=['POST'])
@limiter.limit("50 per minute")
def track_visit():
    data = request.get_json(silent=True) or {}
    if not data.get('anon_id'): return '', 204
    exists = VisitorLog.query.filter(VisitorLog.anon_id==data['anon_id'], VisitorLog.created_at > datetime.utcnow()-timedelta(hours=24)).first()
    if not exists:
        db.session.add(VisitorLog(anon_id=data['anon_id'], device=data.get('device','unknown')))
        db.session.commit()
    return '', 204
@analytics_bp.route('/dashboard', methods=['GET'])
@limiter.limit("10 per minute")
def dashboard():
    today = datetime.utcnow().date()
    visits = VisitorLog.query.filter(VisitorLog.created_at >= today).count()
    android = round(VisitorLog.query.filter(VisitorLog.device=='android', VisitorLog.created_at>=today).count() / max(visits,1)*100, 1)
    rev = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.status=='successful', db.func.date(Transaction.paid_at)==today).scalar() or 0
    blocked = FailedAttempt.query.filter(FailedAttempt.created_at >= today).count()
    apk = VisitorLog.query.filter(VisitorLog.device=='apk_download').count()
    return jsonify({'visits_today':visits, 'android_ratio':android, 'revenue_today':rev, 'blocked_attempts':blocked, 'apk_downloads':apk})
