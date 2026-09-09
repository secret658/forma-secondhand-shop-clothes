from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
#скидка на всю категорию, ровно то что обсуждали
#unique=True на name, чтобы не было двух категорий "джинсы" с разными id по ошибке

    products = relationship("Product", back_populates="category")