from aiogram import Router,F
from aiogram.types import CallbackQuery
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.config import bot, dp, scheduler

router=Router()


@router.callback_query(F.data == "active_task")
async def add_group(call: CallbackQuery):
    # Получаем список задач из scheduler
    jobs = scheduler.get_jobs()
    
    if not jobs:
        await call.message.answer("Нет запланированных задач.")
    else:
        # Форматируем информацию о задачах
        message_text = "Запланированные задачи:\n\n"
        for job in jobs:
            message_text += (
                f"ID задачи: {job.id}\n"
                f"Имя задачи: {job.name}\n"
                f"Триггер: {job.trigger}\n"
                f"Время следующего запуска: {job.next_run_time}\n"
                f"-----------------------------------\n"
            )
        await call.message.answer(message_text)
    
    await call.answer() 

@router.callback_query(F.data == "clear_task")
async def add_group(call: CallbackQuery):
    # Удаляем все задачи
    scheduler.remove_all_jobs()
    await call.message.answer("Все задачи были удалены.")
    await call.answer()