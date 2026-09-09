from datetime import datetime

from pydantic import BaseModel, model_validator

from app.models.discount import DiscountScope, DiscountType


class DiscountCreate(BaseModel):
    code: str | None = None
    discount_type: DiscountType
    value: float
    scope: DiscountScope
    product_id: int | None = None
    category_id: int | None = None
    start_date: datetime
    end_date: datetime
    usage_limit: int | None = None

    @model_validator(mode="after")
    def validate_scope_matches_target(self) -> "DiscountCreate":
        if self.scope == DiscountScope.PRODUCT:
            if self.product_id is None:
                raise ValueError("product_id обязателен при scope=PRODUCT")
            if self.category_id is not None:
                raise ValueError("category_id должен быть пустым при scope=PRODUCT")

        elif self.scope == DiscountScope.CATEGORY:
            if self.category_id is None:
                raise ValueError("category_id обязателен при scope=CATEGORY")
            if self.product_id is not None:
                raise ValueError("product_id должен быть пустым при scope=CATEGORY")

        elif self.scope == DiscountScope.ORDER:
            if self.product_id is not None or self.category_id is not None:
                raise ValueError("product_id и category_id должны быть пустыми при scope=ORDER")

        return self