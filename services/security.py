import hashlib
import hmac
import secrets

ITERATIONS = 200_000

def hash_value(value: str) -> str:
    salt = secrets.token_hex(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        value.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS
    ).hex()
    return f"{salt}${derived_key}"

def verify_value(value: str, stored_hash: str) -> bool:
    try:
        salt, original_hash = stored_hash.split("$", 1)
    except ValueError:
        return False
    
    new_hash  = hashlib.pbkdf2_hmac(
        "sha256",
        value.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS
    ).hex()
    return hmac.compare_digest(new_hash, original_hash)