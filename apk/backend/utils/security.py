import bcrypt, argon2, hmac, hashlib, os, subprocess, json, urllib.parse
from flask_jwt_extended import create_access_token
from datetime import timedelta
from config import Config
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

argon2_hasher = argon2.PasswordHasher(time_cost=Config.ARGON2_TIME_COST, memory_cost=Config.ARGON2_MEMORY_COST, parallelism=1, hash_len=32, salt_len=16)

def hash_phone(phone: str) -> str:
    return hmac.new(os.environ['PHONE_HASH_SECRET'].encode(), phone.encode(), hashlib.sha256).hexdigest()

def generate_jwt_token(phone: str, session_id: str) -> str:
    return create_access_token(identity=phone, additional_claims={"session_id": session_id}, expires_delta=timedelta(seconds=3600))

def verify_flutterwave_webhook(sig: str) -> bool:
    return hmac.compare_digest(sig, os.environ.get('FLUTTERWAVE_SECRET_HASH', ''))

def generate_wg_keypair() -> tuple[str, str]:
    private = subprocess.check_output(['wg', 'genkey']).decode().strip()
    public = subprocess.run(['wg', 'pubkey'], input=private.encode(), capture_output=True, check=True).stdout.decode().strip()
    return private, public

def sign_wg_config(config_text: str, private_key_pem: str) -> tuple[str, str]:
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    signature = private_key.sign(config_text.encode(), ed25519.Ed25519())
    return config_text, signature.hex()
