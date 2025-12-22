from app.core.database import Base
from sqlalchemy import Column, Integer, String, func, DateTime

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    available_qty = Column(Integer, nullable=False)
    reserved_qty = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ProductKeys(Base):
    __tablename__ = "product_keys"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    key_value = Column(String, nullable=False)
    status = Column(String, nullable=False)
    orders_item_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
