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
from sqlalchemy import text, inspect

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    jwt.init_app(app)
    
    # ✅ CORS FIX
    CORS(app, 
         origins=['https://ravenj-png.github.io', 'https://raven-internet.onrender.com'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Admin-Token', 'X-Idempotency-Key', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['X-Request-ID']
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Admin-Token,X-Idempotency-Key')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    if not app.debug:
        Talisman(app, force_https=True, session_cookie_secure=True, frame_options='DENY')
    
    from services.wireguard_service import WireGuardService
    from services.payment_service import PaymentService
    from services.mikrotik_service import MikroTikService
    from services.sms_service import SMSService
    
    WireGuardService(app)
    PaymentService(app)
    MikroTikService(app)
    SMSService(app)
    
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
    
    @app.before_request
    def attach_request_id():
        g.request_id = f"RVNREQ-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    @app.after_request
    def add_request_id_header(response):
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'N/A')
        return response

    @app.route('/health')
    def health():
        try:
            db.session.execute(text('SELECT 1'))
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

    START_TIME = time.time()
    
    @app.route('/api/v1/system/info')
    def system_info():
        from utils.serializers import system_info_dict
        from config import is_router_online, PESAPAL_KEY, PESAPAL_SECRET
        
        db_ok = False
        try:
            db.session.execute(text('SELECT 1'))
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

    if not os.path.exists('logs'):
        os.mkdir('logs')
    fh = logging.FileHandler('logs/raven.log')
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(request_id)s]: %(message)s'))
    
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

# ✅ AUTO-FIX MISSING COLUMNS IN BOTH TABLES
with app.app_context():
    from models import Student, Session, Transaction, Voucher, News, Notification, FailedAttempt, VisitorLog, AuditLog
    try:
        inspector = inspect(db.engine)
        
        # ---- Fix transactions table ----
        if inspector.has_table('transactions'):
            columns = [col['name'] for col in inspector.get_columns('transactions')]
            columns_to_add_tx = [
                ('phone_number', 'VARCHAR(20) NOT NULL DEFAULT \'\''),
                ('voucher_code', 'VARCHAR(20) DEFAULT NULL'),
                ('merchant_reference', 'VARCHAR(100) DEFAULT NULL'),
                ('idempotency_key', 'VARCHAR(100) DEFAULT NULL'),
                ('is_test', 'BOOLEAN DEFAULT FALSE'),
                ('created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
                ('paid_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NULL')
            ]
            for col_name, col_def in columns_to_add_tx:
                if col_name not in columns:
                    app.logger.info(f"⚠️ Missing {col_name} in transactions — adding...")
                    db.session.execute(text(f'ALTER TABLE transactions ADD COLUMN {col_name} {col_def}'))
                    db.session.commit()
                    app.logger.info(f"✅ {col_name} added to transactions")
                else:
                    app.logger.info(f"✅ {col_name} already exists in transactions")
        else:
            app.logger.info("⚠️ transactions table does not exist — will create all tables")

        # ---- Fix vouchers table ----
        if inspector.has_table('vouchers'):
            columns = [col['name'] for col in inspector.get_columns('vouchers')]
            columns_to_add_vc = [
                ('is_test', 'BOOLEAN DEFAULT FALSE'),
                ('created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()')
            ]
            for col_name, col_def in columns_to_add_vc:
                if col_name not in columns:
                    app.logger.info(f"⚠️ Missing {col_name} in vouchers — adding...")
                    db.session.execute(text(f'ALTER TABLE vouchers ADD COLUMN {col_name} {col_def}'))
                    db.session.commit()
                    app.logger.info(f"✅ {col_name} added to vouchers")
                else:
                    app.logger.info(f"✅ {col_name} already exists in vouchers")
        else:
            app.logger.info("⚠️ vouchers table does not exist — will create all tables")
        
        # Create any missing tables (e.g., if tables were missing entirely)
        db.create_all()
        app.logger.info("✅ Database tables created/verified")
    except Exception as e:
        app.logger.error(f"❌ Database error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))from flask import Flask, jsonify, g
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
from sqlalchemy import text, inspect

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    jwt.init_app(app)
    
    # ✅ CORS FIX
    CORS(app, 
         origins=['https://ravenj-png.github.io', 'https://raven-internet.onrender.com'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Admin-Token', 'X-Idempotency-Key', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['X-Request-ID']
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Admin-Token,X-Idempotency-Key')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    if not app.debug:
        Talisman(app, force_https=True, session_cookie_secure=True, frame_options='DENY')
    
    from services.wireguard_service import WireGuardService
    from services.payment_service import PaymentService
    from services.mikrotik_service import MikroTikService
    from services.sms_service import SMSService
    
    WireGuardService(app)
    PaymentService(app)
    MikroTikService(app)
    SMSService(app)
    
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
    
    @app.before_request
    def attach_request_id():
        g.request_id = f"RVNREQ-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    @app.after_request
    def add_request_id_header(response):
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'N/A')
        return response

    @app.route('/health')
    def health():
        try:
            db.session.execute(text('SELECT 1'))
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

    START_TIME = time.time()
    
    @app.route('/api/v1/system/info')
    def system_info():
        from utils.serializers import system_info_dict
        from config import is_router_online, PESAPAL_KEY, PESAPAL_SECRET
        
        db_ok = False
        try:
            db.session.execute(text('SELECT 1'))
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

    if not os.path.exists('logs'):
        os.mkdir('logs')
    fh = logging.FileHandler('logs/raven.log')
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(request_id)s]: %(message)s'))
    
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

# ✅ AUTO-FIX ALL MISSING COLUMNS + CREATE TABLES
with app.app_context():
    from models import Student, Session, Transaction, Voucher, News, Notification, FailedAttempt, VisitorLog, AuditLog
    try:
        inspector = inspect(db.engine)
        
        # Check if the transactions table exists
        if inspector.has_table('transactions'):
            columns = [col['name'] for col in inspector.get_columns('transactions')]
            
            # ALL columns that should exist in the transactions table
            columns_to_add = [
                ('phone_number', 'VARCHAR(20) NOT NULL DEFAULT \'\''),
                ('voucher_code', 'VARCHAR(20) DEFAULT NULL'),
                ('merchant_reference', 'VARCHAR(100) DEFAULT NULL'),
                ('idempotency_key', 'VARCHAR(100) DEFAULT NULL'),
                ('is_test', 'BOOLEAN DEFAULT FALSE'),
                ('created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
                ('paid_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NULL')   # ← added for admin stats
            ]
            
            for col_name, col_def in columns_to_add:
                if col_name not in columns:
                    app.logger.info(f"⚠️ Missing {col_name} column — adding it...")
                    db.session.execute(text(f'ALTER TABLE transactions ADD COLUMN {col_name} {col_def}'))
                    db.session.commit()
                    app.logger.info(f"✅ {col_name} column added")
                else:
                    app.logger.info(f"✅ {col_name} column already exists")
        else:
            app.logger.info("⚠️ transactions table does not exist — will create all tables")
        
        # Create any missing tables (e.g., if the transactions table was missing entirely)
        db.create_all()
        app.logger.info("✅ Database tables created/verified")
    except Exception as e:
        app.logger.error(f"❌ Database error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
