from flask import Blueprint, request, jsonify
from extensions import db
from models import News
from datetime import datetime, timedelta
news_bp = Blueprint('news', __name__, url_prefix='/api')
@news_bp.route('/news', methods=['GET'])
def get_news():
    cutoff = datetime.utcnow() - timedelta(days=7)
    items = News.query.filter(News.created_at >= cutoff).order_by(News.priority.desc(), News.created_at.desc()).limit(10).all()
    res = jsonify([{'id':n.id,'title':n.title,'message':n.message,'priority':n.priority,'created_at':n.created_at.isoformat()} for n in items])
    res.headers['Cache-Control'] = 'no-cache'
    return res
