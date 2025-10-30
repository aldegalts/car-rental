from sqlalchemy import Column, BigInteger, ForeignKey, Text, Numeric, DateTime, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class ViolationEntity(Base):
    __tablename__ = 'violations'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    rental_id = Column(BigInteger, ForeignKey('rentals.id'), nullable=False)
    violation_type_id = Column(BigInteger, ForeignKey('violation_types.id'), nullable=False)
    description = Column(Text, nullable=False)
    fine_amount = Column(Numeric(10, 2), nullable=False)
    violation_date = Column(DateTime(timezone=False), nullable=False)
    is_paid = Column(Boolean, nullable=False, default=False)

    violation_type = relationship("ViolationTypeEntity", back_populates="violations")
    rental = relationship("RentalEntity", back_populates="violations")