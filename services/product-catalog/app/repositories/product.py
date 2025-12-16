from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.product import Product
from app.schemas.product import ProductCreate
from fastapi import HTTPException, status
from datetime import datetime

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100
) -> List[Product]:
    return (
        db.query(Product)
        .filter(Product.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> bool:
    product = get_product_by_id(db, product_id)
    if not product:
        return False
    if product.is_active:
        product.is_active = False
        product.updated_at = datetime.utcnow()
        db.commit()
    return True
