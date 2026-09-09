import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_admin
from app.models.user import User
from app.repositories.product_image_repository import ProductImageRepository
from app.schemas.admin import AdminActionOut
from app.schemas.discount import DiscountCreate
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.schemas.product import ProductOut, ProductUpdate
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    admin: User = Depends(require_admin),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Разрешены только .jpg, .jpeg, .png, .webp",
        )

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Файл больше 5MB"
        )

    #случайное имя файла, чтобы не было конфликтов и нельзя было угадать/перезаписать чужой файл
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = Path("uploads") / filename
    filepath.write_bytes(contents)

    return {"url": f"/uploads/{filename}"}


@router.post("/products/{product_id}/images")
async def upload_product_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    #множественная загрузка галереи для уже созданного товара
    urls = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{file.filename}: разрешены только .jpg, .jpeg, .png, .webp",
            )
        contents = await file.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{file.filename}: больше 5MB"
            )
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = Path("uploads") / filename
        filepath.write_bytes(contents)
        urls.append(f"/uploads/{filename}")

    image_repository = ProductImageRepository(db)
    images = image_repository.add_images(product_id, urls)
    return images


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return service.update_product(admin=admin, product_id=product_id, **data.model_dump())


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    service.delete_product(admin=admin, product_id=product_id)
    return {"detail": "Товар удален"}


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    service.delete_category(admin=admin, category_id=category_id)
    return {"detail": "Категория удалена"}


@router.get("/orders", response_model=list[OrderOut])
def get_all_orders(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    service = AdminService(db)
    return service.get_all_orders()


@router.put("/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return service.update_order_status(admin=admin, order_id=order_id, new_status=data.status)


@router.get("/actions", response_model=list[AdminActionOut])
def get_actions(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    service = AdminService(db)
    return service.get_all_actions()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    service = AdminService(db)
    return service.get_dashboard()


@router.post("/discounts")
def create_discount(
    data: DiscountCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    discount = service.create_discount(admin=admin, data=data.model_dump())
    return discount


@router.get("/discounts")
def get_all_discounts(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    service = AdminService(db)
    return service.get_all_discounts()