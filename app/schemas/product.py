from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    stock_quantity: int = Field(default=0, ge=0)
    category_id: int
    image_url: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    stock_quantity: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    image_url: str | None = None


class ProductImageOut(BaseModel):
    id: int
    url: str
    sort_order: int

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    discount_percent: float
    stock_quantity: int
    category_id: int
    image_url: str | None
    created_at: datetime
    likes_count: int = 0
    images: list[ProductImageOut] = []
    #images - вся галерея, image_url остается как обложка для карточек в каталоге
    #чтобы список товаров не тянул сразу все фото каждого товара

    class Config:
        from_attributes = True