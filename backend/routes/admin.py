import os, html
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Student, Session, Transaction, Voucher, News
from utils.constants import PLANS
from utils.security import hash_phone, gen_wg_keys, sign_config
from services.mikrotik_service import MikroTikService
from services.ip_allocator import IPAllocator
from services.sms_service import SMSService
from services.usage_monitor import check_renewal_reminders
import hmac, datetime as dt

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def verify_admin_token():
    t = request.headers.get('X-Admin-Token'); k = os.environ.get('ADMIN_TOKEN')
    if not t or not k: return False
    return hmac.compare_digest(t.encode(), k.encode())

@admin_bp.before_request
def check(): 
    if not verify_admin_token(): return jsonify({'error':'Unauthorized'}), 401

@admin_bp.route('/stats', methods=['GET'])
def stats():
    today=dt.datetime.utcnow().date(); w=today-dt.timedelta(days=7)
    return jsonify({'active_users':Session.query.filter_by(is_active=True).count(),'total_users':Student.query.count(),
    'today_revenue':db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.status=='successful', db.func.date(Transaction.paid_at)==today).scalar() or 0,
    'week_revenue':db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.status=='successful', Transaction.paid_at>=w).scalar() or 0,
    'vouchers_used':Voucher.query.filter_by(is_used=True).count(),'vouchers_pending':Voucher.query.filter_by(is_used=False).count(),'failed_payments':Transaction.query.filter_by(status='failed').count()})

@admin_bp.route('/transactions', methods=['GET'])
def txns(): return jsonify([{'tx_ref':t.tx_ref,'phone':t.student.phone_display,'amount':t.amount,'status':t.status} for t in Transaction.query.order_by(Transaction.created_at.desc()).limit(50)])

@admin_bp.route('/live-users', methods=['GET'])
def live():
    users = Session.query.filter_by(is_active=True).filter(Session.expires_at > dt.datetime.utcnow()).join(Student).all()
    return jsonify({'users':[{'student_id':u.student_id,'phone':u.student.phone_display,'plan_tier':u.speed_mbps,'data_used_mb':u.used_mb,'expires_at':u.expires_at.strftime('%d/%m %H:%M')} for u in users]})

@admin_bp.route('/generate-voucher', methods=['POST'])
def gen():
    data=request.json or {}; ph=data.get('phone_number'); pid=data.get('plan_id'); pc=data.get('payment_confirmed', True); txn=data.get('txn_id','')
    pl=PLANS.get(pid)
    if not ph or not pl: return jsonify({'error':'Invalid'}), 400
    if pl['tier']=='annual' and not pc: return jsonify({'error':'Annual requires manual verification'}), 400
    if current_app.logger and txn: current_app.logger.info(f"Voucher Generated | {ph} | {pid} | TXN: {txn}")
    s = Student.query.filter_by(phone_hash=hash_phone(ph)).first()
    if not s: s=Student(); s.set_phone(ph); db.session.add(s); db.session.flush()
    priv, pub = gen_wg_keys(); ip = IPAllocator.assign_ip()
    cfg = f"[Interface]\nPrivateKey = {priv}\nAddress = {ip}\nDNS = 8.8.8.8\n\n[Peer]\nPublicKey = {current_app.config['WG_SERVER_PUBLIC_KEY']}\nEndpoint = {current_app.config['MIKROTIK_PUBLIC_IP']}:{current_app.config['MIKROTIK_WG_PORT']}\nAllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 25"
    signed, sig = sign_config(cfg, current_app.config['WG_SIGNING_PRIVATE_KEY_PEM'])
    mt = MikroTikService(current_app)
    if not mt.add_peer(pub, ip, f"RVN-{pub[:5]}", pl['speed']): return jsonify({'error':'MT Failed'}), 503
    sms=SMSService(current_app); sms.send_voucher_sms(ph, f"RVN-{pub[:5]}", {'duration':f"{pl['hours']//24}d", 'data':f"{pl['mb']//1024}GB", 'speed':f"{pl['speed']}Mbps"})
    sess = Session(student_id=s.id, session_token=os.urandom(24).hex(), voucher_code=f"RVN-{pub[:5]}", public_key=pub, allowed_ip=ip, total_mb=pl['mb'], speed_mbps=pl['speed'], expires_at=dt.datetime.utcnow()+dt.timedelta(hours=pl['hours']))
    db.session.add(sess); db.session.commit()
    return jsonify({'success':True,'voucher_code':f"RVN-{pub[:5]}",'expires_at':sess.expires_at.isoformat()})

@admin_bp.route('/news', methods=['POST'])
def news_post():
    data=request.json or {}; title=html.escape(data.get('title','')); msg=html.escape(data.get('message','')); p=data.get('priority',1)
    n=News(title=title, message=msg, priority=p); db.session.add(n); db.session.commit()
    return jsonify({'success':True})

@admin_bp.route('/send-renewal-reminders', methods=['POST'])
def remind():
    check_renewal_reminders(current_app)
    return jsonify({'message':'Reminders sent'})
