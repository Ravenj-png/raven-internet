from flask import Blueprint, request, jsonify, current_app
from utils.security import hash_phone
from models import FailedAttempt
from extensions import db
security_bp = Blueprint('security', __name__, url_prefix='/api/honeypot')
@security_bp.route('/admin/config', methods=['GET'])
def honeypot():
    try: db.session.add(FailedAttempt(ip=request.remote_addr, endpoint='/api/honeypot/admin/config', reason='honeypot_hit')); db.session.commit()
    except: pass
    return jsonify({'error':'Not found'}), 404
