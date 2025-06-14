from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.database.engine import get_session
from app.database.crud.user import is_admin
from app.config import Settings

settings = Settings()
router = Router()

@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    """Обработчик команды /admin"""
    try:
        # Проверяем является ли пользователь админом
        if not await is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора")
            return

        # Проверяем наличие аргументов
        args = message.text.split()
        if len(args) != 2:
            await message.answer(
                "Использование: /admin <user_id>\n"
                "Пример: /admin 123456789"
            )
            return

        try:
            target_user_id = int(args[1])
        except ValueError:
            await message.answer("ID пользователя должен быть числом")
            return

        # Назначаем пользователя админом
        async with get_session() as session:
            stmt = select(User).where(User.user_id == target_user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                await message.answer(f"Пользователь с ID {target_user_id} не найден")
                return

            # Обновляем статус админа
            stmt = update(User).where(User.user_id == target_user_id).values(admin=True)
            await session.execute(stmt)
            await session.commit()

            await message.answer(f"Пользователь {target_user_id} назначен администратором")
            logger.info(f"User {target_user_id} was appointed as admin by {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in admin command: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
