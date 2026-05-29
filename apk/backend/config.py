import os
from datetime import timedelta
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI and not DEBUG:
        raise RuntimeError("DATABASE_URL must be set in production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    PHONE_HASH_SECRET = os.environ.get('PHONE_HASH_SECRET')
    WG_SIGNING_PRIVATE_KEY_PEM = os.environ.get('WG_SIGNING_PRIVATE_KEY_PEM')
    WG_SERVER_PUBLIC_KEY = os.environ.get('WG_SERVER_PUBLIC_KEY', 'SERVER_PUBKEY_PLACEHOLDER')
    ARGON2_TIME_COST = int(os.environ.get('ARGON2_TIME_COST', 2))
    ARGON2_MEMORY_COST = int(os.environ.get('ARGON2_MEMORY_COST', 102400))
    if not PHONE_HASH_SECRET and not DEBUG: raise RuntimeError("PHONE_HASH_SECRET required in production")
    LAPTOP_API_URL = os.environ.get('LAPTOP_API_URL', 'http://localhost:5001')
    LAPTOP_API_TOKEN = os.environ.get('LAPTOP_API_TOKEN', 'dev-token')
    FLUTTERWAVE_SECRET_KEY = os.environ.get('FLUTTERWAVE_SECRET_KEY', '')
    FLUTTERWAVE_SECRET_HASH = os.environ.get('FLUTTERWAVE_SECRET_HASH', '')
    ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', '')
    ALLOWED_ORIGINS = [o.strip() for o in os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',') if o.strip()]
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
