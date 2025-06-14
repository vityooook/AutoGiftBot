from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, create_engine, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    balance = Column(Integer, default=0)
    admin = Column(Boolean, default=False)
    
    auto_purchase_settings = relationship("AutoPurchaseSettings", back_populates="user", uselist=False)
    balance_history = relationship("BalanceHistory", back_populates="user")

class AutoPurchaseSettings(Base):
    __tablename__ = "auto_purchase_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    is_enabled = Column(Boolean, default=False)
    min_price = Column(Integer, default=0)
    max_price = Column(Integer, default=0)
    supply_limit = Column(Integer, default=0)
    purchase_cycles = Column(Integer, default=1)
    
    user = relationship("User", back_populates="auto_purchase_settings")

class BalanceHistory(Base):
    __tablename__ = "balance_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    amount = Column(Integer)
    telegram_payment_charge_id = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="balance_history")

# Создаем асинхронный движок для SQLAlchemy
async def init_db(database_url: str):
    engine = create_async_engine(database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session 