from loguru import logger
from notifiers.logging import NotificationHandler
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from app.config import Settings

settings = Settings()

# Уведомления об ошибках отправляются админам через БД
# Настройка добавляется в хендлерах после инициализации БД

# Set up logging, declare the bot and dispatcher
logger.add(
    "logs/logs.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="1 week",
    compression="zip",
    enqueue=True,
    backtrace=False,
    diagnose=False
)
# Create a new memory storage object
storage = MemoryStorage()
# Create a new bot object with the specified token and parse mode
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
# Create a new dispatcher object with the specified storage
dp = Dispatcher(storage=storage) 