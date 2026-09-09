from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.discount import Discount
from app.repositories.discount_repository import DiscountRepository


class DiscountService:
    def __init__(self, db: Session):
        self.repository = DiscountRepository(db)

    def _validate(self, code: str) -> Discount:
        #общая проверка, используется и в preview и в реальном применении
        #чтобы не дублировать одни и те же условия в двух местах
        discount = self.repository.get_by_code(code)

        if discount is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Промокод не найден"
            )

        if not discount.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Промокод неактивен"
            )

        now = datetime.now(timezone.utc)
        if now < discount.start_date or now > discount.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Срок действия промокода истек"
            )

        if discount.usage_limit is not None and discount.used_count >= discount.usage_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Лимит использований промокода исчерпан",
            )

        return discount

    def validate_only(self, code: str) -> Discount:
        #для превью в корзине, used_count не трогаем
        return self._validate(code)

    def validate_and_apply(self, code: str) -> Discount:
        #для реального оформления заказа, инкрементим used_count
        discount = self._validate(code)
        updated_discount = self.repository.increment_used_count(discount.id)
        return updated_discount