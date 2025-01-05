from pyrogram import Client
from config.config import settings


bot = Client(
    name=settings.LOGIN,
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    phone_number=settings.PHONE,
)
bot.run()
