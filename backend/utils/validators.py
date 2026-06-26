import re, secrets, string
def validate_phone(p): return bool(re.match(r'^(07[0-9]{8}|2567[0-9]{9}|2547[0-9]{9}|2557[0-9]{9})$', p))
def validate_voucher(c): return bool(re.match(r'^[A-Z]{3}-[A-Z0-9]{7}$', c.upper()))
def sanitize(t): return t.strip()[:255] if t else ''
def generate_voucher(): return f"RVN-{''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(7))}"
