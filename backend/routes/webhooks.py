import os, hmac, hashlib
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import Student, Transaction
from utils.constants import PLANS

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhook')
@webhooks_bp.route('/pesapal', methods=['POST'])
def handle():
    sig=request.headers.get('pesapal_signature') or request.headers.get('X-Pesapal-Signature')
    if sig:
        secret=os.environ.get('PESAPAL_CONSUMER_SECRET')
        if secret and not hmac.compare_digest(sig, hmac.new(secret.encode(), request.data, hashlib.sha256).hexdigest()): return jsonify({'message':'Bad sig'}), 401
    d=request.json or {}; ref=d.get('id') or d.get('tx_ref')
    if not ref: return jsonify({'message':'Missing ref'}), 400
    t=Transaction.query.filter_by(tx_ref=ref).first()
    if not t: return jsonify({'message':'Not found'}), 404
    if t.status=='successful': return jsonify({'message':'Done'}), 200
    t.status=d.get('status','failed'); db.session.commit()
    return jsonify({'message':'OK'}), 200
