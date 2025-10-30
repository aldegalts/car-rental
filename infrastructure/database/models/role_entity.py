from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from .base import Base


class RoleEntity(Base):
    __tablename__ = 'roles'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)

    users = relationship("UserEntity", back_populates="role", cascade="all, delete-orphan")
