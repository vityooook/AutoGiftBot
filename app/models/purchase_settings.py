from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class AutoPurchaseSettings(BaseModel):
    """Модель настроек автопокупки"""
    __tablename__ = "auto_purchase_settings"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    min_price = Column(Float, default=0.0)
    max_price = Column(Float, default=0.0)
    supply_limit = Column(Integer, default=0)
    purchase_cycles = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Отношения
    user = relationship("User", back_populates="purchase_settings")
    
    def __repr__(self):
        return f"<AutoPurchaseSettings user_id={self.user_id}>" 