from datetime import datetime, timedelta, timezone
import uuid
import bcrypt
from jose import jwt, JWTError

from app.core.config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(user_id: int) -> str:
    jti = uuid.uuid4().hex
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)
    token = jwt.encode(
        {"sub": str(user_id), "jti": jti, "exp": expire}, 
        settings.secret_key, algorithm=settings.algorithm
    )

    return token, jti

def decode_refresh_token(token: str | None) -> tuple[int, str] | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload["sub"])
        jti = payload["jti"]
    except (JWTError, KeyError, ValueError, TypeError):
        return None
    return user_id, jti