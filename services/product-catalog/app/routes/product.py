from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import product as product_crud
from app.schemas.user import ProductCreate, ProductBase
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.get("/products", response_model=list[ProductBase])
async def read_products(db: Session = Depends(get_db)):
    products = product_crud.get_products(db)
    return products

@router.get("/products/{product_id}", response_model=ProductBase)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.post("/products", response_model=ProductBase, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product = product_crud.create_product(db=db, product=product)
    return ProductCreate(product=ProductBase.model_validate(product))
