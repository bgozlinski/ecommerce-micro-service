from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import product as product_crud
from app.schemas import ProductCreate, ProductBase, ProductOut, ProductPatch
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.get("/products", response_model=list[ProductOut])
async def read_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: str | None = Query(None),
    platform: str | None = Query(None),
    min_price_cents: int | None = Query(None, ge=0),
    max_price_cents: int | None = Query(None, ge=0),
    is_active: bool | None = Query(True),
    search: str | None = Query(None, min_length=1),
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|price_cents|name|id)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):

    products = product_crud.get_products(
        db,
        skip=skip,
        limit=limit,
        category=category,
        platform=platform,
        min_price_cents=min_price_cents,
        max_price_cents=max_price_cents,
        is_active=is_active,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return products

@router.get("/products/{product_id}", response_model=ProductOut)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product = product_crud.create_product(db=db, product=product)
    return product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = product_crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return None

@router.patch("/products/{product_id}", response_model=ProductOut, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, dto: ProductPatch, db: Session = Depends(get_db)):
    updated = product_crud.update_product(db, product_id, dto)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated
