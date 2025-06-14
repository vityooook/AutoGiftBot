from aiogram import Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from app.loader import bot


async def set_default_commands(dp: Dispatcher) -> None:
    """Установка команд бота по умолчанию

    :param dp: Диспетчер бота
    """
    commands = [
        BotCommand(
            command="start",
            description="Запустить бота"
        ),
        BotCommand(
            command="refund",
            description="Настройки"
        )
    ]
    
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeDefault()
    ) 