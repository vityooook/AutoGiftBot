from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from loguru import logger
from typing import List, Tuple, Optional
from decimal import Decimal

from app.database.models import User, AutoPurchaseSettings, BalanceHistory
from app.database.engine import get_session

@logger.catch()
async def get_user_settings(user_id: int) -> Optional[AutoPurchaseSettings]:
    """Получить настройки автопокупки пользователя

    :param session: Сессия базы данных
    :param user_id: ID пользователя
    :return: Настройки автопокупки или None, если настройки не найдены
    :raises SQLAlchemyError: При ошибке базы данных
    """
    async with get_session() as session:
        logger.debug(f"Getting auto purchase settings for user {user_id}")
        
        # Проверяем существование пользователя
        user = await session.get(User, user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return None
            
        stmt = select(AutoPurchaseSettings).where(AutoPurchaseSettings.user_id == user_id)
        result = await session.execute(stmt)
        settings = result.scalar_one_or_none()
        
        if not settings:
            logger.info(f"Creating new settings for user {user_id}")
            settings = AutoPurchaseSettings(
                user_id=user_id,
                is_enabled=False,
                min_price=0,
                max_price=0,
                supply_limit=0,
                purchase_cycles=1
            )
            session.add(settings)
            await session.commit()
            await session.refresh(settings)
            
        logger.debug(f"Found settings for user {user_id}")
        return settings
   
@logger.catch()
async def update_settings(
    user_id: int,
    is_enabled: bool = None,
    min_price: int = None,
    max_price: int = None,
    supply_limit: int = None,
    purchase_cycles: int = None
) -> None:
    """Обновить настройки автопокупки

    :param user_id: ID пользователя
    :param is_enabled: Включена ли автопокупка
    :param min_price: Минимальная цена
    :param max_price: Максимальная цена
    :param supply_limit: Лимит саплая
    :param purchase_cycles: Количество циклов покупки
    :raises SQLAlchemyError: При ошибке базы данных
    :raises ValueError: При некорректных значениях
    """
    async with get_session() as session:
        try:
            logger.debug(f"Updating auto purchase settings for user {user_id}")
            
            # Проверяем существование пользователя
            user = await session.get(User, user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")
                
            # Получаем текущие настройки
            stmt = select(AutoPurchaseSettings).where(AutoPurchaseSettings.user_id == user_id)
            result = await session.execute(stmt)
            current_settings = result.scalar_one_or_none()
            
            if not current_settings:
                # Если настройки не найдены, создаем новые с дефолтными значениями
                current_settings = AutoPurchaseSettings(
                    user_id=user_id,
                    is_enabled=False,
                    min_price=0,
                    max_price=0,
                    supply_limit=0,
                    purchase_cycles=1
                )
                session.add(current_settings)
                await session.commit()
                await session.refresh(current_settings)
                
            # Валидация значений
            update_data = {
                "is_enabled": current_settings.is_enabled,
                "min_price": current_settings.min_price,
                "max_price": current_settings.max_price,
                "supply_limit": current_settings.supply_limit,
                "purchase_cycles": current_settings.purchase_cycles
            }
            
            if is_enabled is not None:
                update_data["is_enabled"] = bool(is_enabled)
                
            if min_price is not None:
                min_price_decimal = int(min_price)
                if min_price_decimal < 0:
                    raise ValueError("Min price cannot be negative")
                if min_price_decimal > 1000000:
                    raise ValueError("Min price too high")
                if max_price is not None and min_price_decimal > max_price and max_price != 0:
                    raise ValueError("Min price cannot be greater than max price")
                update_data["min_price"] = int(min_price_decimal)
                
            if max_price is not None:
                max_price_decimal = int(max_price)
                if max_price_decimal < 0:
                    raise ValueError("Max price cannot be negative")
                if max_price_decimal > 1000000:
                    raise ValueError("Max price too high")
                if min_price is not None and max_price_decimal < min_price and max_price_decimal != 0:
                    raise ValueError("Max price cannot be less than min price")
                update_data["max_price"] = int(max_price_decimal)
                
            if supply_limit is not None:
                if not isinstance(supply_limit, int):
                    raise ValueError("Supply limit must be an integer")
                if supply_limit < 0:
                    raise ValueError("Supply limit cannot be negative")
                update_data["supply_limit"] = supply_limit
                
            if purchase_cycles is not None:
                if not isinstance(purchase_cycles, int):
                    raise ValueError("Purchase cycles must be an integer")
                if purchase_cycles <= 0:
                    raise ValueError("Purchase cycles must be positive")
                if purchase_cycles > 100:
                    raise ValueError("Purchase cycles too high")
                update_data["purchase_cycles"] = purchase_cycles

            stmt = update(AutoPurchaseSettings).where(
                AutoPurchaseSettings.user_id == user_id
            ).values(**update_data)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Updated settings for user {user_id}: {update_data}")
                
        except SQLAlchemyError as e:
            logger.error(f"Database error while updating settings: {e}")
            await session.rollback()
            raise
        except ValueError as e:
            logger.error(f"Validation error while updating settings: {e}")
            raise