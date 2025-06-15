from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from loguru import logger
from decimal import Decimal
from typing import Optional

from app.database.models import User, AutoPurchaseSettings, BalanceHistory
from app.database.engine import get_session

@logger.catch()
async def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь админом

    :param user_id: ID пользователя
    :return: True если пользователь админ, False в противном случае
    """
    async with get_session() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user and user.admin

@logger.catch()
async def get_or_create_user(user_id: int, username: str | None = None) -> User:
    """Получить пользователя или создать нового

    :param telegram_id: Telegram ID пользователя
    :param username: Имя пользователя в Telegram
    :return: Объект пользователя
    """
    async with get_session() as session:
        # Ищем пользователя
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Проверяем, является ли пользователь админом по умолчанию
            is_default_admin = user_id == 487961820
            logger.info(f"Creating new user {user_id}, is_default_admin: {is_default_admin}")
            
            # Создаем нового пользователя
            user = User(
                user_id=user_id,
                username=username,
                balance=0,
                admin=is_default_admin
            )
            session.add(user)
            await session.commit()
            logger.info(f"Created new user: {user_id}, admin: {user.admin}")
            
            # Создаем настройки автопокупки с дефолтными значениями
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
            logger.info(f"Created auto-purchase settings for user: {user_id}")
        else:
            # Обновляем имя пользователя, если оно изменилось
            if user.username != username:
                user.username = username
                await session.commit()
                logger.debug(f"Updated username for user {user_id}")

        return user

@logger.catch()
async def update_user_balance(user_id: int, amount: int, telegram_payment_charge_id: str) -> None:
    """Обновить баланс пользователя

    :param user_id: ID пользователя
    :param amount: Сумма для изменения баланса
    :raises ValueError: При некорректной сумме
    """
    if not isinstance(amount, int):
        raise ValueError("Amount must be a number")

    async with get_session() as session:
        try:
            # Проверяем существование пользователя
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User not found: {user_id}")
                raise ValueError(f"User not found: {user_id}")
                
            # Проверяем, не станет ли баланс отрицательным
            new_balance = user.balance + amount
            logger.info(f"Updating balance for user {user_id}: {user.balance} -> {new_balance}")
                
            # Обновляем баланс
            stmt = update(User).where(User.user_id == user_id).values(balance=new_balance)
            await session.execute(stmt)
            
            # Создаем запись в истории баланса
            balance_history = BalanceHistory(
                user_id=user_id,
                amount=amount,
                telegram_payment_charge_id=telegram_payment_charge_id
            )
            session.add(balance_history)
            
            await session.commit()
            logger.info(f"Successfully updated balance for user {user_id}: {new_balance}")
            logger.info(f"Created balance history record: user_id={user_id}, amount={amount}, charge_id={telegram_payment_charge_id}")
        except Exception as e:
            logger.error(f"Error updating user balance: {e}")
            await session.rollback()
            raise

@logger.catch()
async def get_user_balance(user_id: int) -> int:
    """Получить баланс пользователя

    :param user_id: ID пользователя
    :return: Текущий баланс пользователя
    :raises NoResultFound: Если пользователь не найден
    """
    async with get_session() as session:
        user = await session.get(User, user_id)
        if not user:
            raise NoResultFound(f"User not found: {user_id}")
            
        return user.balance 
    
@logger.catch()
async def get_transaction(telegram_payment_charge_id: str):

    async with get_session() as session:
        stmt = select(BalanceHistory).where(BalanceHistory.telegram_payment_charge_id == telegram_payment_charge_id)
        transaction = await session.execute(stmt)

        if not transaction:
            raise NoResultFound(f"Transaction not found: {telegram_payment_charge_id}")
            
        return transaction.scalar().amount

@logger.catch()
async def delete_transaction(telegram_payment_charge_id: str) -> int:
    """Удаление транзакции из истории

    :param telegram_payment_charge_id: ID транзакции
    :return: Сумма транзакции
    :raises ValueError: Если транзакция не найдена
    """
    async with get_session() as session:
        try:
            # Получаем транзакцию
            stmt = select(BalanceHistory).where(
                BalanceHistory.telegram_payment_charge_id == telegram_payment_charge_id
            )
            result = await session.execute(stmt)
            transaction = result.scalar_one_or_none()

            if not transaction:
                raise ValueError(f"Transaction not found: {telegram_payment_charge_id}")

            amount = transaction.amount
            
            # Удаляем транзакцию
            await session.delete(transaction)
            await session.commit()
            
            logger.info(f"Successfully deleted transaction: {telegram_payment_charge_id}, amount: {amount}")
            return amount

        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            await session.rollback()
            raise

@logger.catch()
async def decrease_user_balance(user_id: int, amount: int) -> None:
    """Уменьшение баланса пользователя

    :param user_id: ID пользователя
    :param amount: Сумма для уменьшения
    :raises ValueError: Если пользователь не найден или недостаточно средств
    """
    async with get_session() as session:
        try:
            # Получаем пользователя
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Проверяем баланс
            if user.balance < amount:
                raise ValueError(f"Insufficient balance: {user.balance} < {amount}")

            # Обновляем баланс
            new_balance = user.balance - amount
            stmt = update(User).where(User.user_id == user_id).values(balance=new_balance)
            await session.execute(stmt)
            await session.commit()

            logger.info(f"Successfully decreased balance for user {user_id}: {user.balance} -> {new_balance}")

        except Exception as e:
            logger.error(f"Error decreasing user balance: {e}")
            await session.rollback()
            raise

@logger.catch()
async def process_refund(user_id: int, telegram_payment_charge_id: str) -> None:
    """Обработка возврата средств

    :param user_id: ID пользователя
    :param telegram_payment_charge_id: ID транзакции
    :raises ValueError: Если транзакция не найдена или недостаточно средств
    """
    try:
        # Получаем сумму транзакции и удаляем её
        amount = await delete_transaction(telegram_payment_charge_id)
        
        # Уменьшаем баланс пользователя
        await decrease_user_balance(user_id, amount)
        
        logger.info(
            f"Successfully processed refund for user {user_id}: "
            f"amount={amount}, "
            f"transaction_id={telegram_payment_charge_id}"
        )

    except Exception as e:
        logger.error(f"Error processing refund: {e}")
        raise

@logger.catch()
async def get_total_balance() -> int:
    """Получить общий баланс всех пользователей

    :return: Общий баланс всех пользователей
    """
    async with get_session() as session:
        stmt = select(User.balance)
        result = await session.execute(stmt)
        balances = result.scalars().all()
        return sum(balances) if balances else 0