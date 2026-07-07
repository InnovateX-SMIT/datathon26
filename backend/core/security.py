import bcrypt

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt directly."""
    pwd_bytes = password.encode('utf-8')
    # Truncate to 72 bytes if needed, which is the hard limit of bcrypt
    pwd_bytes = pwd_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False
