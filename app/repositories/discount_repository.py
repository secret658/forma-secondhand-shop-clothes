from sqlalchemy.orm import Session

from app.models.discount import Discount


class DiscountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str) -> Discount | None:
        return self.db.query(Discount).filter(Discount.code == code).first()

    def get_all(self) -> list[Discount]:
        return self.db.query(Discount).all()

    def create(self, **kwargs) -> Discount:
        discount = Discount(**kwargs)
        self.db.add(discount)
        self.db.commit()
        self.db.refresh(discount)
        return discount

    def increment_used_count(self, discount_id: int) -> Discount:
        discount = (
            self.db.query(Discount)
            .filter(Discount.id == discount_id)
            .with_for_update()
            .first()
        )
        discount.used_count += 1
        self.db.commit()
        self.db.refresh(discount)
        return discount