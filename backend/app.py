from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_talisman import Talisman
from config import Config
from extensions import limiter, db, jwt, migrate
from routes.vouchers import vouchers_bp
from routes.plans import plans_bp
from routes.session import session_bp
from routes.webhooks import webhooks_bp
from services.wireguard_service import WireGuardService
from services.payment_service import PaymentService
import logging, os
from logging.handlers import RotatingFileHandler

def create_app(config_class=Config):
    app = Flask(__name__); app.config.from_object(config_class)
    db.init_app(app); migrate.init_app(app, db); limiter.init_app(app); jwt.init_app(app)
    with app.app_context():
        db.create_all()
    CORS(app, origins=app.config['ALLOWED_ORIGINS'], supports_credentials=True)
    if not app.debug: Talisman(app, force_https=True, session_cookie_secure=True)
    WireGuardService(app); PaymentService(app)
    app.register_blueprint(vouchers_bp); app.register_blueprint(plans_bp); app.register_blueprint(session_bp); app.register_blueprint(webhooks_bp)
    @app.route('/health')
    def health(): return jsonify({'status': 'healthy'}), 200
    @app.errorhandler(404)
    def not_found(e): return jsonify({'message': 'Not found'}), 404
    @app.errorhandler(429)
    def ratelimit(e): return jsonify({'message': 'Rate limit exceeded'}), 429
    if not os.path.exists('logs'): os.mkdir('logs')
    fh = RotatingFileHandler('logs/raven.log', maxBytes=10240, backupCount=5)
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app.logger.addHandler(fh); app.logger.setLevel(logging.INFO)
    return app

app = create_app()
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
