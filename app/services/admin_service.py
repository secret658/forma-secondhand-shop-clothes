from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.admin_action import AdminAction
from app.models.discount import Discount
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_like import ProductLike
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.repositories.discount_repository import DiscountRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.services.stats_service import StatsService


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.product_repository = ProductRepository(db)
        self.order_repository = OrderRepository(db)
        self.discount_repository = DiscountRepository(db)
        self.category_repository = CategoryRepository(db)

    def log_action(
        self, admin: User, action_type: str, target_product_id: int | None = None, details: str | None = None
    ) -> AdminAction:
        action = AdminAction(
            admin_id=admin.id,
            action_type=action_type,
            target_product_id=target_product_id,
            details=details,
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def update_product(self, admin: User, product_id: int, **kwargs) -> Product:
        product = self.product_repository.update(product_id, **kwargs)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

        self.log_action(
            admin=admin,
            action_type="update_product",
            target_product_id=product_id,
            details=f"Изменены поля: {list(kwargs.keys())}",
        )
        return product

    def delete_product(self, admin: User, product_id: int) -> None:
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

        already_ordered = (
            self.db.query(OrderItem).filter(OrderItem.product_id == product_id).first()
        )
        if already_ordered:
            #нельзя удалить товар который уже есть в чьем-то заказе
            #foreign key в order_items ссылается на product_id, удаление сломало бы историю заказов
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар уже фигурирует в заказах, удаление запрещено",
            )

        product_name = product.name

        #лайки и фото это просто метаданные, их можно и нужно снести вместе с товаром
        #без этого MySQL откажет в удалении из-за foreign key constraint
        self.db.query(ProductLike).filter(ProductLike.product_id == product_id).delete()
        self.db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()

        self.db.delete(product)

        self.log_action(
            admin=admin,
            action_type="delete_product",
            target_product_id=None,
            #target_product_id оставляем пустым, т.к. FK на удаленный товар тоже сломался бы
            details=f"Удален товар {product_name} (id={product_id})",
        )
        self.db.commit()

    def delete_category(self, admin: User, category_id: int) -> None:
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

        products_in_category = self.product_repository.get_by_category(category_id)
        if len(products_in_category) > 0:
            #не даем удалить категорию с товарами, иначе товары останутся
            #с category_id указывающим в никуда, это сломает выборки по категории
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"В категории {len(products_in_category)} товар(ов). Сначала удали или перенеси их.",
            )

        category_name = category.name
        self.category_repository.delete(category_id)

        self.log_action(
            admin=admin,
            action_type="delete_category",
            details=f"Удалена категория {category_name}",
        )

    def get_all_orders(self) -> list[Order]:
        return self.order_repository.get_all()

    def update_order_status(self, admin: User, order_id: int, new_status: str) -> Order:
        from app.models.order import OrderStatus

        try:
            new_status_enum = OrderStatus(new_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неизвестный статус"
            )

        order = self.order_repository.get_by_id(order_id)
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")

        old_status = order.status

        #списываем наличие только в момент первого перехода в completed
        #проверка old_status != COMPLETED защищает от повторного списания
        #если админ случайно дважды нажмет "выполнен"
        if new_status_enum == OrderStatus.COMPLETED and old_status != OrderStatus.COMPLETED:
            for item in order.items:
                product = (
                    self.db.query(Product)
                    .filter(Product.id == item.product_id)
                    .with_for_update()
                    .first()
                )
                if product is None or product.stock_quantity < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Недостаточно товара {item.product_id} на складе для подтверждения",
                    )
                product.stock_quantity -= item.quantity

        order.status = new_status_enum
        self.db.commit()

        self.log_action(
            admin=admin,
            action_type="update_order_status",
            details=f"Заказ #{order_id}: {old_status.value} -> {new_status_enum.value}",
        )
        self.db.refresh(order)
        return order

    def get_all_actions(self) -> list[AdminAction]:
        return self.db.query(AdminAction).order_by(AdminAction.created_at.desc()).all()

    def get_dashboard(self) -> dict:
        stats_service = StatsService(self.db)
        return {
            "overall": stats_service.get_overall_stats(),
            "top_products": stats_service.get_top_products(limit=5),
            "by_category": stats_service.get_stats_by_category(),
        }

    def create_discount(self, admin: User, data: dict) -> Discount:
        discount = self.discount_repository.create(**data)

        self.log_action(
            admin=admin,
            action_type="create_discount",
            details=f"Создана скидка id={discount.id}, scope={discount.scope}",
        )
        return discount

    def get_all_discounts(self) -> list[Discount]:
        return self.discount_repository.get_all()