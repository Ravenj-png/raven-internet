from flask import Flask, jsonify
from flask_cors import CORS
from flask_talisman import Talisman
from config import Config
from extensions import limiter, db, jwt, migrate
from routes.plans import plans_bp
from routes.vouchers import vouchers_bp
from routes.session import session_bp
from routes.webhooks import webhooks_bp
from routes.admin import admin_bp
from routes.news import news_bp
from routes.notifications import notifications_bp
from routes.analytics import analytics_bp
from routes.security import security_bp
import logging, os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    jwt.init_app(app)
    
    # Enable CORS
    CORS(app, origins=app.config.get('ALLOWED_ORIGINS', ['*']))
    
    # Security headers (disable for local dev)
    if not app.debug:
        Talisman(app, force_https=True, session_cookie_secure=True, frame_options='DENY')
    
    # Import services
    from services.wireguard_service import WireGuardService
    from services.payment_service import PaymentService
    from services.mikrotik_service import MikroTikService
    from services.sms_service import SMSService
    
    WireGuardService(app)
    PaymentService(app)
    MikroTikService(app)
    SMSService(app)
    
    # Register blueprints
    app.register_blueprint(plans_bp)
    app.register_blueprint(vouchers_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(security_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        try:
            db.session.execute('SELECT 1')
            db_ok = True
        except:
            db_ok = False
        
        mt_ok = False
        try:
            mt_ok = MikroTikService(app).health_check()
        except:
            pass
        
        status = 'healthy' if db_ok and mt_ok else 'degraded'
        return jsonify({'status': status, 'database': 'ok' if db_ok else 'failed'}), 200 if db_ok else 503
    
    # Version endpoint
    @app.route('/api/version')
    def version():
        try:
            with open(os.path.join(os.path.dirname(__file__), 'version.json'), 'r') as f:
                v = __import__('json').load(f)
        except:
            v = {'version': '1.0.0', 'download_url': 'https://your-server.com/raven-vpn.apk', 'force_update': False}
        return jsonify(v)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'message': 'Not found'}), 404
    
    @app.errorhandler(429)
    def ratelimit(e):
        return jsonify({'message': 'Rate limit exceeded'}), 429
    
    # Setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    fh = logging.FileHandler('logs/raven.log')
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app.logger.addHandler(fh)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Raven VPN backend initialized")    
    return app

# Create app
app = create_app()

# Auto-create database tables
with app.app_context():
    # Import all models to ensure they're registered with SQLAlchemy
    from models import Student, Session, Transaction, Voucher, News, Notification, FailedAttempt, VisitorLog
    try:
        db.create_all()
        app.logger.info("✅ Database tables created/verified successfully")
    except Exception as e:
        app.logger.warning(f"⚠️ Table creation note: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
