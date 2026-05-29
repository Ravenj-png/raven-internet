import re
def validate_phone(phone: str) -> bool: return bool(re.match(r'^07[0-9]{8}$', phone))
def validate_voucher_code(code: str) -> bool: return bool(re.match(r'^[A-Z]{3}-[A-Z0-9]{7}$', code.upper()))
def validate_amount(amount: int, expected: int) -> bool: return amount == expected
def sanitize_input(text: str) -> str: return text.strip()[:255]
def generate_voucher_code() -> str:
    import random, string
    return f"RVN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=7))}"
