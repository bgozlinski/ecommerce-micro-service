from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, func, DateTime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="PLN")
    category = Column(String)
    platform = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True))