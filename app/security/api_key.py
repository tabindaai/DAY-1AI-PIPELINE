import secrets
import hashlib
import hmac

def generate_api_key():
    return secrets.token_urlsafe(32)

def hash_api_key(api_key):
    return hashlib.sha256(
        api_key.encode()
    ).hexdigest()

def verify_api_key(api_key, stored_hash):
    incoming_hash = hash_api_key(api_key)

    return hmac.compare_digest(
        incoming_hash,
        stored_hash
    )