import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

def get_real_ip():
    from flask import request
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

limiter = Limiter(key_func=get_real_ip, storage_uri=os.environ.get('RATELIMIT_STORAGE_URL','memory://'), headers_enabled=True, strategy='fixed-window', key_prefix='raven')
db = SQLAlchemy(); jwt = JWTManager(); migrate = Migrate()
