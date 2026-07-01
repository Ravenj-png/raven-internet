from flask import Blueprint, request, jsonify, current_app, g
from extensions import db, limiter
from models import Transaction, Voucher, AuditLog
from utils.serializers import tx_to_dict
from utils.transactions import safe_external_call, validate_idempotency
from config import is_test_mode
import datetime as dt, random, string

plans_bp = Blueprint('plans', __name__, url_prefix='/api/v1')

@plans_bp.route('/purchase', methods=['POST'])
@limiter.limit("5/minute")
def purchase_plan():
    data = request.json or {}
    phone = data.get('phone_number', '').strip()
    plan_id = data.get('plan_id')
    amount = data.get('amount', 0)
    idem_key = request.headers.get('X-Idempotency-Key')

    # 1. IDEMPOTENCY CHECK (BEFORE ANY DB WRITE)
    dup_txn, dup_status = validate_idempotency(idem_key)
    if dup_txn:
        # Rebuild response from DB state (no stale JSON cache)
        return jsonify({
            'success': dup_status == 'SUCCESS',
            'mode': 'TEST' if dup_txn.is_test else 'LIVE',
            'status': dup_status,
            'message': 'Request already processed',
            'voucher_code': dup_txn.voucher_code,
            'request_id': g.request_id
        }), 200 # ✅ Always 200 for valid replays

    # 2. CREATE PENDING RECORD + COMMIT IMMEDIATELY
    txn = Transaction(
        phone_number=phone, plan_id=plan_id, amount=amount, 
        status='PENDING', idempotency_key=idem_key, 
        merchant_reference=idem_key, # Map them for now
        is_test=is_test_mode()
    )
    db.session.add(txn)
    db.session.commit() 

    # 3. CALL EXTERNAL API (SAFE WRAPPER)
    if is_test_mode():
        result = {'status': 'SUCCESS', 'data': {'mock': True}}
    else:
        result = safe_external_call('pesapal', data, timeout=5)

    # 4. STATE TRANSITION → FINALITY
    if result['status'] == 'SUCCESS':
        txn.status = 'SUCCESS'
        # Generate Voucher Atomically
        txn.voucher_code = generate_voucher_code(txn.plan_id, txn.is_test)
    elif result['status'] == 'TIMEOUT':
        txn.status = 'PENDING_REVIEW' # ✅ Critical State
    else:
        txn.status = 'FAILED'
        
    db.session.commit()
    
    # 5. AUDIT LOG
    log_action('purchase_' + ('test' if is_test_mode() else 'live'), phone, plan_id, status=txn.status)

    # 6. RETURN CLEAN JSON
    return jsonify({
        'success': txn.status == 'SUCCESS',
        'mode': 'TEST' if is_test_mode() else 'LIVE',
        'status': txn.status,
        'message': result.get('message', 'Processing complete'),
        'voucher_code': txn.voucher_code,
        'request_id': g.request_id
    }), 200 # ✅ Always 200. Frontend checks .status

def generate_voucher_code(plan_id, is_test):
    """Atomic voucher generation"""
    prefix = "TEST-" if is_test else "RVN-"
    max_attempts = 10
    for _ in range(max_attempts):
        code = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        # Check uniqueness in DB
        if not Voucher.query.filter_by(code=code).first():
            # Create Voucher Record
            v = Voucher(code=code, plan_id=plan_id, is_test=is_test, 
                        expires_at=dt.datetime.utcnow() + dt.timedelta(hours=24))
            db.session.add(v)
            db.session.commit()
            return code
    raise Exception("Failed to generate unique voucher code")

def log_action(action_type, phone, plan_id, **kwargs):
    """Simple audit logger"""
    try:
        log = AuditLog(
            action=action_type,
            phone=phone,
            plan_id=plan_id,
            metadata=kwargs,
            timestamp=dt.datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        current_app.logger.warning(f"Audit log failed: {e}")
