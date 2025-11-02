# lib/utils/password.py  ✅ (Final fixed version)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_BCRYPT_LENGTH = 72  # bcrypt cannot hash longer than this


def hash_password(password: str) -> str:
    """
    Hash a plain password safely with bcrypt.
    Truncates password to 72 characters if too long to avoid errors.
    """
    if not password:
        raise ValueError("Password cannot be empty")

    # Truncate to max bcrypt limit
    if len(password.encode("utf-8")) > MAX_BCRYPT_LENGTH:
        password = password[:MAX_BCRYPT_LENGTH]

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.
    """
    if not plain_password or not hashed_password:
        return False

    if len(plain_password.encode("utf-8")) > MAX_BCRYPT_LENGTH:
        plain_password = plain_password[:MAX_BCRYPT_LENGTH]

    return pwd_context.verify(plain_password, hashed_password)
