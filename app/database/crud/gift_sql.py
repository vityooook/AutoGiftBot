from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.database.models import AutoPurchaseSettings, User
from app.database.engine import get_session


@logger.catch()
async def get_active_purchase_settings():
    """
    Получить все активные настройки автопокупки с балансом пользователя
    
    Returns:
        List[Tuple[AutoPurchaseSettings, int]]: Список кортежей (настройки, баланс)
    """
    async with get_session() as session:
        try:
            stmt = (
                select(AutoPurchaseSettings, User.balance)
                .join(User, AutoPurchaseSettings.user_id == User.user_id)
                .where(AutoPurchaseSettings.is_enabled == True)
            )
            
            result = await session.execute(stmt)
            return result.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting active purchase settings: {e}")
            raise
