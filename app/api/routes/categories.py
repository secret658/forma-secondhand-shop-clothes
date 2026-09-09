from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_admin
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    #публичный эндпоинт, без require_admin
    #нужен и обычным юзерам чтобы фильтровать товары по категории на витрине
    repository = CategoryRepository(db)
    return repository.get_all()


@router.post("/", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    repository = CategoryRepository(db)
    return repository.create(name=data.name, discount_percent=data.discount_percent)