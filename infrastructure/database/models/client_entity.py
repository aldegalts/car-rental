from sqlalchemy import Column, BigInteger, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class ClientEntity(Base):
    __tablename__ = 'clients'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String(11), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    driver_license = Column(String(50), nullable=False, unique=True)
    license_expiry_date = Column(Date, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, unique=True)

    user = relationship("UserEntity", back_populates="client")
