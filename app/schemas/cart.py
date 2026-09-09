from pydantic import BaseModel


class CartItem(BaseModel):
    product_id: int
    quantity: int


class CartPreviewRequest(BaseModel):
    items: list[CartItem]
    promo_code: str | None = None


class CartPreviewResponse(BaseModel):
    subtotal: float
    discount_amount: float
    total: float
    promo_valid: bool | None = None
    message: str | None = None