import re

def validate_phone(phone):
    # Fixed: Changed {9} to {8} to match 12-digit international numbers
    return bool(re.match(r'^(07[0-9]{8}|2567[0-9]{8}|2547[0-9]{8}|2557[0-9]{8})$', phone))

def validate_voucher_code(code):
    return bool(re.match(r'^[A-Z]{3}-[A-Z0-9]{7}$', code.upper()))

def sanitize_input(text):
    return text.strip()[:255] if text else ''
