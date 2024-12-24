from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards.keyboards import main_kb
from config.config import settings

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id == settings.ADMIN_ID:
        await message.answer(
            text=(
                f"Привет, {message.from_user.full_name}! Это бот для массовой рассылки.\n\n"
                "*Используй меню ниже для работы:*\n"
                "1️⃣ *Добавить группу* — загрузите файл с чатами, чтобы создать новую группу для рассылки.\n"
                "2️⃣ *Удалить группу* — полностью удалите группу с чатами.\n"
                "3️⃣ *Удалить канал/чат* — удалите отдельный чат из всех групп, если он там есть.\n"
                "4️⃣ *Статистика групп* — показывает количество чатов в каждой группе рассылок.\n"
                "5️⃣ *Рассылка* — начните новую рассылку по выбранным группам или чатам.\n"
                "6️⃣ *Активные задачи* — покажет все активные и запланированные рассылки.\n"
                "7️⃣ *Очистить задачи* — удаляет все текущие и запланированные рассылки."
            ),
            reply_markup=main_kb(),
            parse_mode="Markdown",
        )
    else:
        await message.answer(
            text="Для использования бота свяжись с администратором.\n\n"
        )
