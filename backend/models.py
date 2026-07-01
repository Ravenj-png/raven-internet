from extensions import db
import datetime as dt
from sqlalchemy import Index, or_

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    phone_hash = db.Column(db.String(64), unique=True, nullable=False)
    phone_display = db.Column(db.String(20)) # Last 4 digits for UI
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    is_blocked = db.Column(db.Boolean, default=False)

    def set_phone(self, phone):
        from utils.security import hash_phone
        self.phone_hash = hash_phone(phone)
        self.phone_display = phone[-4:] if len(phone) >= 4 else phone

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    session_token = db.Column(db.String(100), unique=True)
    voucher_code = db.Column(db.String(20), unique=True)
    public_key = db.Column(db.String(100))
    allowed_ip = db.Column(db.String(50))
    total_mb = db.Column(db.Integer, default=0)
    used_mb = db.Column(db.Integer, default=0)
    speed_mbps = db.Column(db.Integer, default=1)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    plan_id = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    
    # ✅ HARDENED STATE MACHINE
    status = db.Column(db.String(20), default='PENDING') 
    # States: PENDING, SUCCESS, FAILED, PENDING_REVIEW
    
    voucher_code = db.Column(db.String(20))
    idempotency_key = db.Column(db.String(100), unique=True, nullable=True)
    merchant_reference = db.Column(db.String(100), unique=True, nullable=True) # For Webhooks
    is_test = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    
    # ✅ INDEXES FOR SPEED & LOCKS
    __table_args__ = (
        Index('idx_tx_idem', 'idempotency_key'),
        Index('idx_tx_merchant_ref', 'merchant_reference'),
        Index('idx_tx_status', 'status'),
    )

class Voucher(db.Model):
    __tablename__ = 'vouchers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True)
    plan_id = db.Column(db.String(50))
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    is_test = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    
    __table_args__ = (
        Index('idx_voucher_code', 'code'),
        Index('idx_voucher_is_test', 'is_test'),
    )

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    message = db.Column(db.Text)
    priority = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class FailedAttempt(db.Model):
    __tablename__ = 'failed_attempts'
    id = db.Column(db.Integer, primary_key=True)
    phone_hash = db.Column(db.String(64))
    ip_address = db.Column(db.String(45))
    reason = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class VisitorLog(db.Model):
    __tablename__ = 'visitor_logs'
    id = db.Column(db.Integer, primary_key=True)
    anon_id = db.Column(db.String(36))
    device_type = db.Column(db.String(20))
    visited_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50)) # purchase_test, purchase_live, webhook_update
    phone = db.Column(db.String(20))
    plan_id = db.Column(db.String(50))
    metadata = db.Column(db.JSON) # Stores extra details like status, error msg
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
