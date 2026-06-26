from datetime import datetime, timedelta
from models import Session
from services.sms_service import SMSService
def check_renewal_reminders(app):
    with app.app_context():
        cutoff = datetime.utcnow() + timedelta(days=3)
        active = Session.query.filter(Session.is_active==True, Session.expires_at <= cutoff, Session.expires_at > datetime.utcnow()).all()
        for s in active:
            sms = SMSService(app)
            sms.send_voucher_sms(s.student.phone_display, "RENEWAL", {'duration':'3 Days','data':'N/A','speed':'N/A'})
