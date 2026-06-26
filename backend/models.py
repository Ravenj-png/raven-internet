from extensions import db
from utils.security import hash_phone
from datetime import datetime

class Student(db.Model):
    __tablename__='students'
    id=db.Column(db.Integer, primary_key=True)
    phone_hash=db.Column(db.String(64), unique=True, index=True)
    phone_display=db.Column(db.String(20), nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    is_blocked=db.Column(db.Boolean, default=False)
    sessions=db.relationship('Session', backref='student', lazy=True)
    transactions=db.relationship('Transaction', backref='student', lazy=True)
    def set_phone(self, ph): self.phone_hash=hash_phone(ph); self.phone_display=f"***{ph[-4:]}"

class Session(db.Model):
    __tablename__='sessions'
    id=db.Column(db.Integer, primary_key=True)
    student_id=db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    session_token=db.Column(db.String(255), unique=True, index=True)
    voucher_code=db.Column(db.String(12), nullable=False)
    public_key=db.Column(db.String(255), nullable=False)
    allowed_ip=db.Column(db.String(50), unique=True, nullable=False, index=True)
    total_mb=db.Column(db.Integer, default=1024)
    used_mb=db.Column(db.Integer, default=0)
    remaining_mb=db.Column(db.Integer, default=1024)
    speed_mbps=db.Column(db.Integer, default=1)
    starts_at=db.Column(db.DateTime, default=datetime.utcnow)
    expires_at=db.Column(db.DateTime, nullable=False, index=True)
    is_active=db.Column(db.Boolean, default=True, index=True)

class Transaction(db.Model):
    __tablename__='transactions'
    id=db.Column(db.Integer, primary_key=True)
    student_id=db.Column(db.Integer, db.ForeignKey('students.id'))
    tx_ref=db.Column(db.String(100), unique=True, index=True)
    amount=db.Column(db.Integer, nullable=False)
    plan_id=db.Column(db.String(50), nullable=False)
    status=db.Column(db.String(20), default='pending')
    paid_at=db.Column(db.DateTime)
    referral_code=db.Column(db.String(20), nullable=True)

class Voucher(db.Model):
    __tablename__='vouchers'
    id=db.Column(db.Integer, primary_key=True)
    code=db.Column(db.String(12), unique=True, index=True)
    plan_id=db.Column(db.String(50))
    total_mb=db.Column(db.Integer)
    duration_hours=db.Column(db.Integer)
    speed_mbps=db.Column(db.Integer)
    is_used=db.Column(db.Boolean, default=False)
    expires_at=db.Column(db.DateTime)

class News(db.Model):
    __tablename__='news'
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100))
    message=db.Column(db.Text)
    priority=db.Column(db.Integer, default=1)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__='notifications'
    id=db.Column(db.Integer, primary_key=True)
    student_id=db.Column(db.Integer, db.ForeignKey('students.id'))
    message=db.Column(db.Text)
    type=db.Column(db.String(20), default='info')
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

class FailedAttempt(db.Model):
    __tablename__='failed_attempts'
    id=db.Column(db.Integer, primary_key=True)
    ip=db.Column(db.String(45), nullable=False, index=True)
    phone_hash=db.Column(db.String(64))
    endpoint=db.Column(db.String(100))
    reason=db.Column(db.String(50))
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

class VisitorLog(db.Model):
    __tablename__='visitor_logs'
    id=db.Column(db.Integer, primary_key=True)
    anon_id=db.Column(db.String(36), nullable=False, index=True)
    device=db.Column(db.String(20), default='unknown')
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
