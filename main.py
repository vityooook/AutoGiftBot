from loguru import logger
import asyncio
import signal

from app.loader import dp, bot
from app.services.commands import set_default_commands
from app.handlers import get_handlers_router
from app.database.engine import init_db
from app.services.gifts import GiftService




async def main():
    # Инициализируем базу данных
    await init_db()
    
    # Добавляем роутеры и команды
    dp.include_router(get_handlers_router())
    await set_default_commands(dp)
    
    # Удаляем веб-хук и пишем лог
    await bot.delete_webhook(drop_pending_updates=True)
    logger.debug("Bot started!")
    
    # Создаем сервис подарков
    gift_service = GiftService()
    logger.debug("Gift service created!")

    # Запускаем бота и сервис подарков
    await asyncio.gather(
        dp.start_polling(bot),
        gift_service.check_and_purchase_gifts()
    )


if __name__ == "__main__":
    asyncio.run(main())