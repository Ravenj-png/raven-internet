from extensions import db
from datetime import datetime, timedelta
from utils.security import hash_phone

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    phone_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    phone_display = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sessions = db.relationship('Session', backref='student', lazy=True)
    transactions = db.relationship('Transaction', backref='student', lazy=True)
    def set_phone(self, phone: str): self.phone_hash = hash_phone(phone); self.phone_display = f"***{phone[-4:]}"

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    voucher_code = db.Column(db.String(12), nullable=False)
    public_key = db.Column(db.String(255), nullable=False)
    allowed_ip = db.Column(db.String(50), unique=True, nullable=False, index=True)
    total_mb = db.Column(db.Integer, default=1024)
    used_mb = db.Column(db.Integer, default=0)
    remaining_mb = db.Column(db.Integer, default=1024)
    starts_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_revoked = db.Column(db.Boolean, default=False, index=True)
    is_connected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def calculate_remaining(self): self.remaining_mb = max(0, self.total_mb - self.used_mb)
    def is_expired(self) -> bool: return datetime.utcnow() > self.expires_at or self.remaining_mb <= 0

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    tx_ref = db.Column(db.String(100), unique=True, nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    plan_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Voucher(db.Model):
    __tablename__ = 'vouchers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(12), unique=True, nullable=False, index=True)
    plan_id = db.Column(db.String(50), nullable=False)
    total_mb = db.Column(db.Integer, default=1024)
    duration_hours = db.Column(db.Integer, default=24)
    is_used = db.Column(db.Boolean, default=False)
    used_by = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
