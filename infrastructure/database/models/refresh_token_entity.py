from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from datetime import datetime
from .base import Base

class RefreshTokenEntity(Base):
    __tablename__ = "refresh_tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
