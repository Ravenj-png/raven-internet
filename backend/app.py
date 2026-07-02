from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_talisman import Talisman
from config import Config, is_test_mode
from extensions import db, jwt, migrate, limiter
from routes.plans import plans_bp
from routes.vouchers import vouchers_bp
from routes.session import session_bp
from routes.webhooks import webhooks_bp
from routes.admin import admin_bp
from routes.news import news_bp
from routes.notifications import notifications_bp
from routes.analytics import analytics_bp
from routes.security import security_bp
from routes.rune import rune_bp
import logging
import os
import time
import uuid
import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    jwt.init_app(app)
    
    CORS(app, 
         origins=['https://ravenj-png.github.io', 'https://raven-internet.onrender.com'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Admin-Token', 'X-Idempotency-Key'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
         
    if not app.debug:
        Talisman(app, force_https=True, session_cookie_secure=True, frame_options='DENY')
    
    # Initialize Services
    from services.wireguard_service import WireGuardService
    from services.payment_service import PaymentService
    from services.mikrotik_service import MikroTikService
    from services.sms_service import SMSService
    
    WireGuardService(app)
    PaymentService(app)
    MikroTikService(app)
    SMSService(app)
    
    # Register Blueprints
    app.register_blueprint(plans_bp)
    app.register_blueprint(vouchers_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(rune_bp)
    
    # ✅ REQUEST ID MIDDLEWARE
    @app.before_request
    def attach_request_id():
        g.request_id = f"RVNREQ-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    @app.after_request
    def add_request_id_header(response):
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'N/A')
        return response

    # ✅ HEALTH CHECK
    @app.route('/health')
    def health():
        try:
            db.session.execute('SELECT 1')
            db_ok = True
        except:
            db_ok = False
        
        router_ok = False
        try:
            from config import is_router_online
            router_ok = is_router_online()
        except:
            pass
            
        return jsonify({
            'status': 'healthy' if db_ok else 'degraded',
            'database': 'ok' if db_ok else 'failed',
            'router': 'online' if router_ok else 'offline',
            'mode': 'TEST MODE - NO REAL TRANSACTIONS' if is_test_mode() else 'LIVE',
            'version': 'R V1.0.1'
        }), 200 if db_ok else 503

    # ✅ SYSTEM INFO
    START_TIME = time.time()
    
    @app.route('/api/v1/system/info')
    def system_info():
        from utils.serializers import system_info_dict
        from config import is_router_online, PESAPAL_KEY, PESAPAL_SECRET
        
        db_ok = False
        try:
            db.session.execute('SELECT 1')
            db_ok = True
        except:
            pass
        
        router_ok = is_router_online()
        pesapal_ok = bool(PESAPAL_KEY and PESAPAL_SECRET)
        mode = 'TEST' if is_test_mode() else 'LIVE'
        uptime = time.time() - START_TIME
        
        return jsonify(system_info_dict(db_ok, router_ok, pesapal_ok, mode, uptime)), 200

    @app.route('/api/version')
    def version():
        return jsonify({'version': 'R V1.0.1', 'force_update': False})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'message': 'Not found', 'request_id': getattr(g, 'request_id', None)}), 404

    # ✅ LOGGING SETUP (FIXED: Safe request_id fallback)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    fh = logging.FileHandler('logs/raven.log')
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(request_id)s]: %(message)s'))
    
    # ✅ CRITICAL FIX: Safe filter that never fails
    class RequestIDFilter(logging.Filter):
        def filter(self, record):
            try:
                record.request_id = getattr(g, 'request_id', 'N/A')
            except Exception:
                record.request_id = 'N/A'
            return True
    
    fh.addFilter(RequestIDFilter())
    app.logger.addHandler(fh)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Raven NetOps VPN backend initialized")
    
    return app

app = create_app()

# ✅ DATABASE INITIALIZATION (MOVED INSIDE APP CONTEXT)
with app.app_context():
    from models import Student, Session, Transaction, Voucher, News, Notification, FailedAttempt, VisitorLog, AuditLog
    try:
        db.create_all()
        app.logger.info("✅ Database tables created/verified")
    except Exception as e:
        app.logger.warning(f"⚠️ DB note: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
