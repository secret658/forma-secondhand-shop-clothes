from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    price = Column(Numeric(10, 2), nullable=False)
#базовая цена, Numeric опять же, не Float

    discount_percent = Column(Numeric(5, 2), default=0)
#скидка конкретно на этот товар

    stock_quantity = Column(Integer, nullable=False, default=0)
#наличие на складе, это поле будет в центре внимания когда дойдём до race condition при покупке последней единицы

    image_url = Column(String(500), nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="products")

    created_at = Column(DateTime, default=datetime.utcnow)
#когда товар добавлен, пригодится для сортировки "новинки" на витрине

    order_items = relationship("OrderItem", back_populates="product")

    admin_actions = relationship("AdminAction", back_populates="target_product")