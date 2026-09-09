from pydantic import BaseModel


class TopProductStat(BaseModel):
    product_id: int
    product_name: str
    total_sold: int
    total_revenue: float


class CategoryStat(BaseModel):
    category_id: int
    category_name: str
    total_revenue: float
    orders_count: int


class OverallStats(BaseModel):
    total_orders: int
    total_revenue: float
    total_products_sold: int