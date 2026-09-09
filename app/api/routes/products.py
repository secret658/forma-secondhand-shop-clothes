from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, require_admin
from app.models.user import User
from app.repositories.like_repository import LikeRepository
from app.repositories.product_image_repository import ProductImageRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductOut)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    repository = ProductRepository(db)
    product = repository.create(**data.model_dump())
    return {**product.__dict__, "likes_count": 0, "images": []}


@router.get("/", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db)):
    product_repository = ProductRepository(db)
    like_repository = LikeRepository(db)

    products = product_repository.get_all()
    product_ids = [p.id for p in products]
    likes_map = like_repository.get_likes_count_bulk(product_ids)
    #в списке товаров галерею не подтягиваем специально, только обложку image_url
    #это осознанный trade-off, полная галерея грузится только на странице товара

    return [{**p.__dict__, "likes_count": likes_map[p.id], "images": []} for p in products]


@router.get("/liked", response_model=list[ProductOut])
def get_liked_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product_repository = ProductRepository(db)
    like_repository = LikeRepository(db)

    liked_ids = like_repository.get_liked_product_ids(current_user.id)
    if not liked_ids:
        return []

    all_products = product_repository.get_all()
    liked_products = [p for p in all_products if p.id in liked_ids]
    likes_map = like_repository.get_likes_count_bulk(liked_ids)

    return [{**p.__dict__, "likes_count": likes_map[p.id], "images": []} for p in liked_products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product_repository = ProductRepository(db)
    like_repository = LikeRepository(db)
    image_repository = ProductImageRepository(db)

    product = product_repository.get_by_id(product_id)
    likes_count = like_repository.get_likes_count(product_id)
    images = image_repository.get_by_product(product_id)
    #на детальной странице галерею подтягиваем полностью, тут это оправдано

    return {**product.__dict__, "likes_count": likes_count, "images": images}


@router.post("/{product_id}/like")
def toggle_like(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like_repository = LikeRepository(db)
    liked = like_repository.toggle_like(user_id=current_user.id, product_id=product_id)
    likes_count = like_repository.get_likes_count(product_id)
    return {"liked": liked, "likes_count": likes_count}