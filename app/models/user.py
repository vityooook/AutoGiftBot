from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel

class User(BaseModel):
    """Модель пользователя"""
    __tablename__ = "users"

    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Отношения
    purchase_settings = relationship("AutoPurchaseSettings", back_populates="user", uselist=False)
    balance_history = relationship("BalanceHistory", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.telegram_id}>" 