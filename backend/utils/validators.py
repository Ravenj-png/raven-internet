import re, secrets, string

def validate_phone(phone):
    return bool(re.match(r'^(07[0-9]{8}|2567[0-9]{8}|2547[0-9]{8}|2557[0-9]{8})$', phone))

def validate_voucher_code(code):
    return bool(re.match(r'^[A-Z]{3}-[A-Z0-9]{7}$', code.upper()))

def sanitize_input(text):
    return text.strip()[:255] if text else ''

def generate_voucher_code():
    suffix = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(7)
    )
    return f"RVN-{suffix}"
