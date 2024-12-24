import os
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings, SettingsConfigDict
from pyrogram import Client
from faststream import FastStream
from faststream.redis import RedisBroker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore


# Класс настроек
class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int
    API_ID: int
    API_HASH: str
    PHONE: str
    LOGIN: str
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    REDIS_PORT: int  # Порт для подключения к Redis
    REDIS_PASSWORD: str  # Пароль для подключения к Redis
    REDIS_HOST: str  # Хост Redis-сервера
    REDIS_DB: int
    # Загрузка переменных из .env
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


# Получаем параметры настроек
settings = Settings()

# Инициализируем aiogram бота и диспетчер
bot = Bot(
    token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

redis_url = f"rediss://:{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

# Инициализируем pyrogram клиента

broker = RedisBroker(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")

app = FastStream(broker)

# Инициализация APScheduler
scheduler = AsyncIOScheduler(
    jobstores={
        "default": RedisJobStore(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )
    }
)

# Настройка логирования через loguru
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(
    log_file_path,
    format=settings.FORMAT_LOG,
    level="INFO",
    rotation=settings.LOG_ROTATION,
)
