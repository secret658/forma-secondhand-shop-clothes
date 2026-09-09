from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.discount import DiscountScope, DiscountType
from app.repositories.product_repository import ProductRepository
from app.services.discount_service import DiscountService


class CartService:
    def __init__(self, db: Session):
        self.db = db
        self.product_repository = ProductRepository(db)
        self.discount_service = DiscountService(db)

    def preview(self, items: list, promo_code: str | None) -> dict:
        resolved = []
        subtotal = 0.0

        for item in items:
            product = self.product_repository.get_by_id(item.product_id)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Товар {item.product_id} не найден",
                )
            line_total = float(product.price) * item.quantity
            subtotal += line_total
            resolved.append({"product": product, "quantity": item.quantity, "line_total": line_total})

        if not promo_code:
            return {
                "subtotal": subtotal,
                "discount_amount": 0,
                "total": subtotal,
                "promo_valid": None,
                "message": None,
            }

        try:
            discount = self.discount_service.validate_only(promo_code)
        except HTTPException as e:
            #промокод невалидный, но корзину все равно показываем, просто без скидки
            return {
                "subtotal": subtotal,
                "discount_amount": 0,
                "total": subtotal,
                "promo_valid": False,
                "message": e.detail,
            }

        target_subtotal = self._get_target_subtotal(discount, resolved)
        discount_amount = self._calculate_discount_amount(discount, target_subtotal)

        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "total": subtotal - discount_amount,
            "promo_valid": True,
            "message": None,
        }

    def _get_target_subtotal(self, discount, resolved: list) -> float:
        if discount.scope == DiscountScope.ORDER:
            return sum(item["line_total"] for item in resolved)

        if discount.scope == DiscountScope.PRODUCT:
            return sum(
                item["line_total"] for item in resolved
                if item["product"].id == discount.product_id
            )

        if discount.scope == DiscountScope.CATEGORY:
            return sum(
                item["line_total"] for item in resolved
                if item["product"].category_id == discount.category_id
            )

        return 0

    def _calculate_discount_amount(self, discount, target_subtotal: float) -> float:
        if discount.discount_type == DiscountType.PERCENTAGE:
            return target_subtotal * float(discount.value) / 100

        #FIXED, скидка не может быть больше самой суммы на которую действует
        return min(float(discount.value), target_subtotal)