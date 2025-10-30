from sqlalchemy import Column, BigInteger, String, Numeric, Text
from sqlalchemy.orm import relationship

from .base import Base


class ViolationTypeEntity(Base):
    __tablename__ = 'violation_types'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type_name = Column(String(100), nullable=False)
    default_fine = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=False)

    violations = relationship("ViolationEntity", back_populates="violation_type", cascade="all, delete-orphan")
