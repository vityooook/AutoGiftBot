from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class BalanceHistory(BaseModel):
    """Модель истории баланса"""
    __tablename__ = "balance_history"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    operation_type = Column(String, nullable=False)  # deposit, withdraw, purchase
    description = Column(String, nullable=True)
    
    # Отношения
    user = relationship("User", back_populates="balance_history")
    
    def __repr__(self):
        return f"<BalanceHistory user_id={self.user_id} amount={self.amount}>" 