from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    price_cents: int = Field(..., ge=0)
    currency: str = Field(default="PLN", min_length=3, max_length=3)
    category: Optional[str] = None
    platform: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    category: Optional[str] = None
    platform: Optional[str] = None
    is_active: Optional[bool] = None

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    platform: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("price_cents")
    @classmethod
    def validate_price(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError("price_cents must be >= 0")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v):
        if v is None:
            return v
        if len(v) != 3:
            raise ValueError("currency must be a 3-letter code")
        return v.upper()