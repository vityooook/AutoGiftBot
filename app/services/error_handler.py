from loguru import logger
from functools import wraps
from typing import Callable, Any
import traceback

from app.loader import bot

ADMIN_ID = 487961820

async def send_error_notification(error: Exception, context: str = "") -> None:
    """Отправляет уведомление об ошибке администратору"""
    try:
        error_message = (
            f"🚨 Ошибка в боте!\n\n"
            f"Контекст: {context}\n"
            f"Тип ошибки: {type(error).__name__}\n"
            f"Сообщение: {str(error)}\n\n"
            f"Трейсбек:\n{traceback.format_exc()}"
        )
        await bot.send_message(ADMIN_ID, error_message)
        logger.error(f"Отправлено уведомление об ошибке: {error}")
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление об ошибке: {e}")

def handle_errors(context: str = "") -> Callable:
    """Декоратор для обработки ошибок в асинхронных функциях"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Ошибка в {func.__name__}: {e}")
                await send_error_notification(e, f"{context} ({func.__name__})")
                raise
        return wrapper
    return decorator 