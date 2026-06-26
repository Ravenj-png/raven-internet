import uuid
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Student, Transaction
from services.payment_service import PaymentService
from utils.validators import validate_phone, sanitize_input
from utils.security import hash_phone
from utils.constants import PLANS

plans_bp = Blueprint('plans', __name__, url_prefix='/api/plans')
@plans_bp.route('/purchase', methods=['POST'])
@limiter.limit("3 per minute")
def purchase():
    d=request.json or {}; ph=sanitize_input(d.get('phone_number','')); pid=d.get('plan_id',''); amt=d.get('amount',0)
    if not validate_phone(ph) or pid not in PLANS: return jsonify({'message':'Invalid'}), 400
    pl=PLANS[pid]
    if amt!=pl['amount']: return jsonify({'message':'Price mismatch'}), 400
    s = Student.query.filter_by(phone_hash=hash_phone(ph)).first()
    if s and s.is_blocked: return jsonify({'message':'Account blocked'}), 403
    tx_ref=f"RAVEN_{uuid.uuid4().hex[:10].upper()}"
    if not s: s=Student(); s.set_phone(ph); db.session.add(s); db.session.flush()
    t=Transaction(student_id=s.id, tx_ref=tx_ref, amount=amt, plan_id=pid, status='pending')
    db.session.add(t); db.session.commit()
    res=PaymentService(current_app).initiate_payment(ph, amt, tx_ref, pid)
    if not res['success']: db.session.delete(t); db.session.commit(); return jsonify({'message':res.get('error')}), 400
    return jsonify({'success':True,'checkout_url':res['checkout_url'],'tx_ref':tx_ref})
