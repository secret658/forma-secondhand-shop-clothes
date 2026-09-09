from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repository = OrderRepository(db)
        self.product_repository = ProductRepository(db)

    def create_order(self, user_id: int, items: list) -> Order:
        locked_products = []
        total_price = 0

        #сначала блокируем и проверяем ВСЕ товары, считаем сумму
        #и только потом создаем сам Order, чтобы total_price был известен сразу при INSERT
        for item in items:
            product = (
                self.db.query(Product)
                .filter(Product.id == item.product_id)
                .with_for_update()
                .first()
            )

            if product is None:
                self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Продукт {item.product_id} не найден",
                )

            if product.stock_quantity < item.quantity:
                self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточно товара {product.name} на складе",
                )

            line_total = float(product.price) * item.quantity
            total_price += line_total
            locked_products.append((product, item.quantity, line_total))

        order = Order(user_id=user_id, total_price=total_price)
        self.db.add(order)
        self.db.flush()
        #flush чтобы получить order.id до создания order_items

        for product, quantity, line_total in locked_products:
            #наличие тут НЕ списываем специально
            #списание происходит только когда админ подтвердит заказ (status=completed)
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price_at_purchase=product.price,
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)
        return order