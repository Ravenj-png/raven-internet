import uuid
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Student, Transaction
from services.payment_service import PaymentService
from utils.validators import validate_phone, validate_amount, sanitize_input
from utils.security import hash_phone

plans_bp = Blueprint('plans', __name__, url_prefix='/api/plans')
PLANS = {'daily': {'amount': 950, 'mb': 1024, 'hours': 24}, 'weekly': {'amount': 6500, 'mb': 7168, 'hours': 168}}

@plans_bp.route('/purchase', methods=['POST'])
@limiter.limit("3 per minute")
def purchase():
    try:
        data = request.get_json() or {}
        phone, plan_id, amount = sanitize_input(data.get('phone_number','')), data.get('plan_id',''), data.get('amount',0)
        if not validate_phone(phone) or plan_id not in PLANS: return jsonify({'message': 'Invalid input'}), 400
        plan = PLANS[plan_id]
        if not validate_amount(amount, plan['amount']): return jsonify({'message': f'Expected {plan["amount"]}'}), 400
        tx_ref = f"RAVEN_{uuid.uuid4().hex[:10].upper()}"
        student = Student.query.filter_by(phone_hash=hash_phone(phone)).first()
        if not student: student = Student(); student.set_phone(phone); db.session.add(student); db.session.flush()
        txn = Transaction(student_id=student.id, tx_ref=tx_ref, amount=amount, plan_id=plan_id, status='pending')
        db.session.add(txn); db.session.commit()
        res = PaymentService(current_app).initiate_payment(phone, amount, tx_ref)
        if not res['success']: return jsonify({'message': res.get('error')}), 400
        return jsonify({'success': True, 'checkout_url': res['checkout_url'], 'tx_ref': tx_ref}), 200
    except Exception as e: current_app.logger.error(f"Purchase failed: {e}"); db.session.rollback(); return jsonify({'message': 'Failed'}), 500
