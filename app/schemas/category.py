from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    discount_percent: float = 0


class CategoryOut(BaseModel):
    id: int
    name: str
    discount_percent: float

    class Config:
        from_attributes = True