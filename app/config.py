from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    # Основные настройки бота
    BOT_TOKEN: str = Field(..., description="Токен Telegram бота из .env")
    DEBUG: bool = False
    
    # База данных
    DATABASE_URL: str = Field(..., description="URL базы данных из .env")
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/bot.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Создаем экземпляр настроек
settings = Settings() 