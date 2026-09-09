from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AdminAction(Base):
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True, index=True)

    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin = relationship("User", back_populates="admin_actions")

    action_type = Column(String(50), nullable=False)

    target_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    target_product = relationship("Product", back_populates="admin_actions")

    details = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

