from datetime import datetime

from pydantic import BaseModel


class AdminActionOut(BaseModel):
    id: int
    admin_id: int
    action_type: str
    target_product_id: int | None
    details: str | None
    created_at: datetime

    class Config:
        from_attributes = True