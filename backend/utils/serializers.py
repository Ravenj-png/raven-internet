def tx_to_dict(txn):
    """Converts DB object to clean JSON dict"""
    if not txn: return None
    return {
        'id': txn.id,
        'phone': txn.phone_number,
        'plan': txn.plan_id,
        'amount': txn.amount,
        'status': txn.status,
        'voucher_code': txn.voucher_code,
        'created_at': txn.created_at.isoformat() if txn.created_at else None,
        'is_test': txn.is_test
    }

def system_info_dict(db_ok, router_ok, pesapal_ok, mode, uptime):
    return {
        'version': 'R V1.0.1',
        'api': 'v1',
        'mode': mode,
        'components': {
            'database': 'CONNECTED' if db_ok else 'DISCONNECTED',
            'router': 'CONNECTED' if router_ok else 'OFFLINE',
            'payment_gateway': 'CONFIGURED' if pesapal_ok else 'MISSING_KEYS'
        },
        'uptime_seconds': int(uptime),
        'build': 'local' # Or use env var
    }
