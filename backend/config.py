import os
class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY')
    PHONE_HASH_SECRET=os.environ.get('PHONE_HASH_SECRET')
    WG_SIGNING_PRIVATE_KEY_PEM=os.environ.get('WG_SIGNING_PRIVATE_KEY_PEM')
    WG_SERVER_PUBLIC_KEY=os.environ.get('WG_SERVER_PUBLIC_KEY')
    PESAPAL_CONSUMER_KEY=os.environ.get('PESAPAL_CONSUMER_KEY')
    PESAPAL_CONSUMER_SECRET=os.environ.get('PESAPAL_CONSUMER_SECRET')
    PESAPAL_IPN_URL=os.environ.get('PESAPAL_IPN_URL')
    YOOLA_SMS_API_KEY=os.environ.get('YOOLA_SMS_API_KEY')
    YOOLA_SMS_SENDER_ID=os.environ.get('YOOLA_SMS_SENDER_ID','RavenVPN')
    YOOLA_SMS_BASE_URL=os.environ.get('YOOLA_SMS_BASE_URL','https://api.yoola.com/v1')
    MIKROTIK_HOST=os.environ.get('MIKROTIK_HOST')
    MIKROTIK_USERNAME=os.environ.get('MIKROTIK_USERNAME','admin')
    MIKROTIK_PASSWORD=os.environ.get('MIKROTIK_PASSWORD')
    MIKROTIK_WG_PORT=int(os.environ.get('MIKROTIK_WG_PORT','51820'))
    MIKROTIK_PUBLIC_IP=os.environ.get('MIKROTIK_PUBLIC_IP')
    ALLOWED_ORIGINS=[o.strip() for o in os.environ.get('ALLOWED_ORIGINS','').split(',') if o.strip()]
    RATELIMIT_STORAGE_URL=os.environ.get('RATELIMIT_STORAGE_URL','memory://')
