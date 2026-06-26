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
from services.wireguard_service import WireGuardService
from services.payment_service import PaymentService
from services.mikrotik_service import MikroTikService
from services.sms_service import SMSService
import logging, os, json
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__); app.config.from_object(Config)
    db.init_app(app); migrate.init_app(app, db); limiter.init_app(app); jwt.init_app(app)
    CORS(app, origins=app.config['ALLOWED_ORIGINS'])
    if not app.debug: Talisman(app, force_https=True, session_cookie_secure=True, frame_options='DENY')
    WireGuardService(app); PaymentService(app); MikroTikService(app); SMSService(app)
    app.register_blueprint(plans_bp); app.register_blueprint(vouchers_bp)
    app.register_blueprint(session_bp); app.register_blueprint(webhooks_bp)
    app.register_blueprint(admin_bp); app.register_blueprint(news_bp)
    app.register_blueprint(notifications_bp); app.register_blueprint(analytics_bp)
    app.register_blueprint(security_bp)
    @app.route('/health')
    def health():
        try: db.session.execute('SELECT 1'); db_ok=True
        except: db_ok=False
        mt_ok = MikroTikService(app).health_check()
        return jsonify({'status':'healthy' if db_ok and mt_ok else 'degraded'}), 200 if db_ok and mt_ok else 503
    if not os.path.exists('logs'): os.mkdir('logs')
    fh = RotatingFileHandler('logs/raven.log', maxBytes=10240, backupCount=5)
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app.logger.addHandler(fh); app.logger.setLevel(logging.INFO); return app
app = create_app()
if __name__=='__main__': app.run(host='0.0.0.0', port=5000)
