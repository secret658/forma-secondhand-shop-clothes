from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.stats import CategoryStat, OverallStats, TopProductStat
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overall", response_model=OverallStats)
def get_overall_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    service = StatsService(db)
    return service.get_overall_stats()


@router.get("/top-products", response_model=list[TopProductStat])
def get_top_products(
    limit: int = 10, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    service = StatsService(db)
    return service.get_top_products(limit=limit)


@router.get("/by-category", response_model=list[CategoryStat])
def get_stats_by_category(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    service = StatsService(db)
    return service.get_stats_by_category()