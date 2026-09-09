from sqlalchemy.orm import Session

from app.models.product_image import ProductImage


class ProductImageRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_images(self, product_id: int, urls: list[str]) -> list[ProductImage]:
        images = []
        for i, url in enumerate(urls):
            image = ProductImage(product_id=product_id, url=url, sort_order=i)
            self.db.add(image)
            images.append(image)
        self.db.commit()
        for image in images:
            self.db.refresh(image)
        return images

    def get_by_product(self, product_id: int) -> list[ProductImage]:
        return (
            self.db.query(ProductImage)
            .filter(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order)
            .all()
        )

    def get_by_products_bulk(self, product_ids: list[int]) -> dict[int, list[ProductImage]]:
        #одним запросом подтягиваем картинки сразу для списка товаров, не по одному
        if not product_ids:
            return {}
        images = (
            self.db.query(ProductImage)
            .filter(ProductImage.product_id.in_(product_ids))
            .order_by(ProductImage.sort_order)
            .all()
        )
        result: dict[int, list[ProductImage]] = {pid: [] for pid in product_ids}
        for image in images:
            result[image.product_id].append(image)
        return result

    def delete_by_product(self, product_id: int) -> None:
        self.db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
        self.db.commit()