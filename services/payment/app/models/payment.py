from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, nullable=False, index=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="PLN")
    status = Column(String, nullable=False, default="pending") # pending, success, failed
    provider = Column(String, default="Stripe")
    external_payment_id = Column(String, nullable=True) # ID of Stripe payment
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())