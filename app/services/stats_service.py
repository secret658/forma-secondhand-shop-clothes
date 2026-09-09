from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product


class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def get_overall_stats(self) -> dict:
        total_orders = self.db.query(func.count(Order.id)).scalar()

        total_revenue = (
            self.db.query(func.sum(OrderItem.price * OrderItem.quantity)).scalar() or 0
        )
        #or 0 на случай если заказов вообще нет, SUM по пустой таблице вернет None, не 0

        total_products_sold = self.db.query(func.sum(OrderItem.quantity)).scalar() or 0

        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "total_products_sold": total_products_sold,
        }

    def get_top_products(self, limit: int = 10) -> list[dict]:
        #группируем по продукту, считаем сумму количества и выручки с каждого
        results = (
            self.db.query(
                Product.id,
                Product.name,
                func.sum(OrderItem.quantity).label("total_sold"),
                func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": r.id,
                "product_name": r.name,
                "total_sold": r.total_sold,
                "total_revenue": float(r.total_revenue),
            }
            for r in results
        ]

    def get_stats_by_category(self) -> list[dict]:
        results = (
            self.db.query(
                Category.id,
                Category.name,
                func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue"),
                func.count(func.distinct(Order.id)).label("orders_count"),
            )
            .join(Product, Product.category_id == Category.id)
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .group_by(Category.id, Category.name)
            .all()
        )
        #distinct(Order.id) важен тут
        #без него если в одном заказе 2 товара из категории, заказ посчитается дважды

        return [
            {
                "category_id": r.id,
                "category_name": r.name,
                "total_revenue": float(r.total_revenue),
                "orders_count": r.orders_count,
            }
            for r in results
        ]