import requests, time, json
from flask import current_app, g
from extensions import db
from models import Transaction
from sqlalchemy import or_

def validate_idempotency(key):
    """Returns (txn, cached_status) if exists, else (None, None)"""
    if not key: return None, None
    txn = Transaction.query.filter_by(idempotency_key=key).first()
    if txn:
        # Return current state so we can rebuild response dynamically
        return txn, txn.status 
    return None, None

def safe_external_call(service, payload, timeout=5):
    """Wraps external APIs with strict timeouts and error mapping"""
    # Service-specific timeouts
    timeouts = {'pesapal': 5, 'mikrotik': 12, 'sms': 8, 'default': 5}
    actual_timeout = timeouts.get(service, timeouts['default'])
    
    try:
        start = time.time()
        
        if service == 'pesapal':
            # REPLACE WITH YOUR REAL PESAPAL CALL
            # resp = requests.post(PESAPAL_URL, json=payload, headers=..., timeout=actual_timeout)
            # Mocking for structure:
            resp = {'status_code': 200, 'json': lambda: {'redirect_url': 'https://pesapal.com/mock'}}
            
            if resp['status_code'] == 200:
                return {'status': 'SUCCESS', 'data': resp['json']()}
            elif resp['status_code'] in [400, 422]:
                return {'status': 'FAILED', 'message': 'Invalid details'}
            else:
                return {'status': 'FAILED', 'message': 'Gateway Error'}
                
        elif service == 'mikrotik':
            # REPLACE WITH YOUR REAL MIKROTIK CALL
            # resp = requests.post(...)
            return {'status': 'SUCCESS', 'message': 'Provisioned'}

    except requests.exceptions.Timeout:
        return {'status': 'TIMEOUT', 'message': 'Service delayed. Check status later.'}
    except requests.exceptions.ConnectionError:
        return {'status': 'FAILED', 'message': 'Service unreachable'}
    except Exception as e:
        current_app.logger.error(f"External call failed: {e} | ID: {g.request_id}")
        return {'status': 'FAILED', 'message': 'Unexpected error'}
