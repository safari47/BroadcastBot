from aiogram import Router, F
from keyboards.keyboards import main_kb
from aiogram.types import CallbackQuery
from database.dao import get_group_counts

router = Router()


@router.callback_query(F.data == "statistic")
async def show_statistics(call: CallbackQuery):
    groups_stats = await get_group_counts()
    
    if groups_stats:
        # Формируем разделённое сообщение
        stats_text = "\n\n".join(
            [
                f"*📌 {group['group_name']}*\n— *Количество записей*: {group['count']}"
                for group in groups_stats
            ]
        )
        message_text = f"*📊 Статистика групп:*\n\n{stats_text}"
    else:
        message_text = "❌ *Статистика недоступна.*\nНет данных о группах."
    
    await call.message.answer(
        message_text,
        reply_markup=main_kb(),  # Основная клавиатура
        parse_mode="Markdown"   # Указываем режим Markdown
    )
