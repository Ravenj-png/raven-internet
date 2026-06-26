import re, secrets, string

def validate_phone(phone: str) -> bool:
    return bool(re.match(r'^(07[0-9]{8}|2567[0-9]{9}|2547[0-9]{9}|2557[0-9]{9})$', phone))

def validate_voucher_code(code: str) -> bool:
    return bool(re.match(r'^[A-Z]{3}-[A-Z0-9]{7}$', code.upper()))

def sanitize_input(text: str) -> str:  # ✅ ADD THIS
    if not text:
        return ''
    return text.strip()[:255]

def generate_voucher_code() -> str:
    suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))
    return f"RVN-{suffix}"
