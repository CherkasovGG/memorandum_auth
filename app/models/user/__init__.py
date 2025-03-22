from sqlalchemy import BigInteger, Column, String, LargeBinary
from sqlalchemy.dialects.postgresql import UUID

from core.db import Base
from core.db.mixins import TimestampMixin


class User(Base, TimestampMixin):

    __tablename__ = "users"

    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(LargeBinary, nullable=False)
