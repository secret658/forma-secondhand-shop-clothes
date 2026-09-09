from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=1000)
    #le=1000 защита от абсурдных значений типа quantity=99999999
    #которые могли бы использоваться для DOS через тяжелые вычисления


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)
    #пустой заказ не имеет смысла, без min_length прошел бы валидацию


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price: float = Field(validation_alias="price_at_purchase")

    class Config:
        from_attributes = True
        populate_by_name = True


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: float
    created_at: datetime
    items: list[OrderItemOut]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str