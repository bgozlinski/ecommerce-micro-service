from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductPatch
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


def update_product(db: Session, product_id: int, dto: ProductPatch) -> Optional[Product]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    if dto.name is not None:
        product.name = dto.name
    if dto.description is not None:
        product.description = dto.description
    if dto.price_cents is not None:
        product.price_cents = dto.price_cents
    if dto.currency is not None:
        product.currency = dto.currency
    if dto.category is not None:
        product.category = dto.category
    if dto.platform is not None:
        product.platform = dto.platform
    if dto.is_active is not None:
        product.is_active = bool(dto.is_active)

    product.updated_at = datetime.utcnow()

    db.add(product)
    db.commit()
    db.refresh(product)
    return product