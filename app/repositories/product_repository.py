from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_all(self) -> list[Product]:
        return self.db.query(Product).all()

    def get_by_category(self, category_id: int) -> list[Product]:
        return self.db.query(Product).filter(Product.category_id == category_id).all()

    def create(self, **kwargs) -> Product:
        product = Product(**kwargs)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product_id: int, **kwargs) -> Product | None:
        product = self.get_by_id(product_id)
        if product is None:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)
            #пропускаем None, чтобы не затереть существующее значение
            #если юзер не прислал поле в PATCH запросе

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        self.db.delete(product)
        self.db.commit()