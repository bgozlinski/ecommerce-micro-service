from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductPatch
from datetime import datetime, timezone

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        *,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        min_price_cents: Optional[int] = None,
        max_price_cents: Optional[int] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
) -> List[Product]:
    """List products with optional filtering and sorting.

    Defaults keep backward compatibility: only active products, sorted by created_at desc.
    """
    q = db.query(Product)

    if is_active is not None:
        q = q.filter(Product.is_active == bool(is_active))
    if category:
        q = q.filter(Product.category == category)
    if platform:
        q = q.filter(Product.platform == platform)
    if min_price_cents is not None:
        q = q.filter(Product.price_cents >= int(min_price_cents))
    if max_price_cents is not None:
        q = q.filter(Product.price_cents <= int(max_price_cents))
    if search:
        like = f"%{search}%"

        from sqlalchemy import or_, func
        q = q.filter(or_(func.lower(Product.name).like(like.lower()), func.lower(Product.description).like(like.lower())))

    sort_map = {
        "created_at": Product.created_at,
        "updated_at": Product.updated_at,
        "price_cents": Product.price_cents,
        "name": Product.name,
        "id": Product.id,
    }
    sort_col = sort_map.get(sort_by, Product.created_at)
    if (sort_dir or "desc").lower() == "asc":
        q = q.order_by(sort_col.asc())
    else:
        q = q.order_by(sort_col.desc())

    return q.offset(skip).limit(limit).all()

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

    product.updated_at = datetime.now(timezone.utc)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product