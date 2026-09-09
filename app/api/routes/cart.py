from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.cart import CartPreviewRequest, CartPreviewResponse
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/preview", response_model=CartPreviewResponse)
def preview_cart(data: CartPreviewRequest, db: Session = Depends(get_db)):
    service = CartService(db)
    return service.preview(items=data.items, promo_code=data.promo_code)