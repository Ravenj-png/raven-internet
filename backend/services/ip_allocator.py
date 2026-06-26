from extensions import db
from models import Session
import time
class IPAllocator:
    SUBNET="10.0.0"; MIN_HOST=10; MAX_HOST=250
    @classmethod
    def assign_ip(cls, max_retries=5):
        for attempt in range(max_retries):
            try:
                used=db.session.query(Session.allowed_ip).with_for_update().filter(Session.allowed_ip.like(f"{cls.SUBNET}.%"),Session.is_active==True).all()
                used_hosts={int(ip[0].split('.')[-1].split('/')[0]) for ip in used if ip[0] and ip[0].startswith(f"{cls.SUBNET}.")}
                for h in range(cls.MIN_HOST,cls.MAX_HOST+1):
                    if h not in used_hosts: return f"{cls.SUBNET}.{h}/32"
                raise RuntimeError("Full")
            except Exception:
                if attempt==max_retries-1: raise
                time.sleep(0.1*(2**attempt))
