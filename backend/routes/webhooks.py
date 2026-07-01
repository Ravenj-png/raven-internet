from flask import Blueprint, request, jsonify, current_app, g
from extensions import db
from models import Transaction, AuditLog
from sqlalchemy import or_
import hmac, hashlib, os, datetime as dt

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

@webhooks_bp.route('/pesapal', methods=['POST'])
def pesapal_ipn():
    # ✅ HMAC VERIFY
    signature = request.headers.get('X-Pesapal-Signature')
    secret = os.environ.get('PESAPAL_CONSUMER_SECRET')
    payload = request.get_data()
    
    if not signature or not secret:
        return jsonify({'error': 'Missing signature or secret'}), 400
        
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return jsonify({'error': 'Invalid webhook signature'}), 401

    data = request.json or {}
    merchant_ref = data.get('merchant_reference')
    pesapal_status = data.get('payment_status') # COMPLETED, FAILED, etc.

    if not merchant_ref:
        return jsonify({'error': 'Missing merchant reference'}), 400

    # ✅ CORRECT QUERY USING or_ (Fixes previous bug)
    txn = Transaction.query.filter(
        or_(
            Transaction.idempotency_key == merchant_ref,
            Transaction.merchant_reference == merchant_ref
        )
    ).first()

    if not txn:
        current_app.logger.warning(f"Webhook ref not found: {merchant_ref} | ID: {g.request_id}")
        return jsonify({'error': 'Transaction not found'}), 404

    # ✅ RACE PROTECTION: Only SUCCESS is terminal. 
    # If it was FAILED/PENDING before but now SUCCESS, we update it.
    if txn.status != 'SUCCESS':
        old_status = txn.status
        if pesapal_status == 'COMPLETED':
            txn.status = 'SUCCESS'
            # Ensure voucher exists (in case payment succeeded but webhook arrived before local gen)
            if not txn.voucher_code:
                from routes.plans import generate_voucher_code
                try:
                    txn.voucher_code = generate_voucher_code(txn.plan_id, txn.is_test)
                except Exception as e:
                    current_app.logger.error(f"Voucher gen in webhook failed: {e}")
                    txn.status = 'PENDING_REVIEW' # Fallback if gen fails
        elif pesapal_status in ['FAILED', 'CANCELLED']:
            txn.status = 'FAILED'
        else:
            txn.status = 'PENDING_REVIEW'
            
        db.session.commit()
        
        # Audit Log
        try:
            log = AuditLog(
                action='pesapal_webhook',
                phone=txn.phone_number,
                plan_id=txn.plan_id,
                metadata={'old_status': old_status, 'new_status': txn.status, 'pesapal_status': pesapal_status},
                timestamp=dt.datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
        except: pass

        current_app.logger.info(f"Webhook updated {txn.id} from {old_status} to {txn.status} | ID: {g.request_id}")

    return jsonify({'success': True}), 200
