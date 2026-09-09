from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    url = Column(String(500), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    #sort_order определяет порядок в карусели, первое фото (0) обычно и есть обложка