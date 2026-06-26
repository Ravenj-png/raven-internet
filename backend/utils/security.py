import hmac, hashlib, os, subprocess, base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from flask_jwt_extended import create_access_token
from datetime import timedelta

def hash_phone(ph):
    return hmac.new(os.environ.get('PHONE_HASH_SECRET','').encode(), ph.encode(), hashlib.sha256).hexdigest()
def gen_jwt(ph, sid): return create_access_token(identity=ph, additional_claims={"session_id":sid}, expires_delta=timedelta(seconds=3600))
def gen_wg_keys(): priv=subprocess.check_output(['wg','genkey']).decode().strip(); pub=subprocess.run(['wg','pubkey'], input=priv.encode(), capture_output=True).stdout.decode().strip(); return priv, pub
def sign_config(txt, pem): pk=serialization.load_pem_private_key(pem.encode(), None); sig=pk.sign(txt.encode(), ed25519.Ed25519()); return txt, base64.b64encode(sig).decode()
