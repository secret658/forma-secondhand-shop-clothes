from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product_like import ProductLike


class LikeRepository:
    def __init__(self, db: Session):
        self.db = db

    def toggle_like(self, user_id: int, product_id: int) -> bool:
        existing = (
            self.db.query(ProductLike)
            .filter(ProductLike.user_id == user_id, ProductLike.product_id == product_id)
            .first()
        )
        if existing:
            self.db.delete(existing)
            self.db.commit()
            return False

        like = ProductLike(user_id=user_id, product_id=product_id)
        self.db.add(like)
        self.db.commit()
        return True

    def get_likes_count(self, product_id: int) -> int:
        return (
            self.db.query(func.count(ProductLike.id))
            .filter(ProductLike.product_id == product_id)
            .scalar()
        )

    def get_likes_count_bulk(self, product_ids: list[int]) -> dict[int, int]:
        if not product_ids:
            return {}
        results = (
            self.db.query(ProductLike.product_id, func.count(ProductLike.id))
            .filter(ProductLike.product_id.in_(product_ids))
            .group_by(ProductLike.product_id)
            .all()
        )
        counts = {product_id: count for product_id, count in results}
        return {pid: counts.get(pid, 0) for pid in product_ids}

    def has_user_liked(self, user_id: int, product_id: int) -> bool:
        return (
            self.db.query(ProductLike)
            .filter(ProductLike.user_id == user_id, ProductLike.product_id == product_id)
            .first()
            is not None
        )

    def get_liked_product_ids(self, user_id: int) -> list[int]:
        #список id товаров, которые лайкнул конкретный юзер
        #нужен для вкладки "Избранное"
        rows = self.db.query(ProductLike.product_id).filter(ProductLike.user_id == user_id).all()
        return [r[0] for r in rows]