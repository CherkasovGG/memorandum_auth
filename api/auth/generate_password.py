import bcrypt

import jwt

from core.config import settings


def hash_password(password: str) -> bytes:
    """Шифруем пароль"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    """Проверка совпадения пароля"""
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)
