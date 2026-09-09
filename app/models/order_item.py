from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="items")

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product = relationship("Product", back_populates="order_items")

    quantity = Column(Integer, nullable=False, default=1)

    price_at_purchase = Column(Numeric(10, 2), nullable=False)
#цена ОДНОЙ единицы товара на момент покупки, уже с учётом скидки юзера+товара+категории
#снова snapshot, теперь на уровне конкретной позиции а не всего заказа