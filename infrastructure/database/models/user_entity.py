from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class UserEntity(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(BigInteger, ForeignKey("roles.id"), nullable=False)

    role = relationship("RoleEntity", back_populates="users")
    client = relationship("ClientEntity", back_populates="users", cascade="all, delete-orphan")
