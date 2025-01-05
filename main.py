import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from handlers.start import router as admin_router
from handlers.group import router as group_router
from handlers.stat import router as stat_router
from handlers.broadcast import router as broadcast_router
from handlers.task import router as task_router
from config.config import bot, dp, app, scheduler
from database.base import create_tables


# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command="start", description="Запуск бота")]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


# Функция, которая выполнится, когда бот запустится
async def start_bot():
    await set_commands()
    await create_tables()
    logger.info("Бот успешно запущен.")

    # Запускаем планировщик
    scheduler.start()
    logger.info("APScheduler успешно запущен.")


# Функция, которая выполнится, когда бот завершит свою работу
async def stop_bot():
    logger.warning("Бот остановлен!")
    if scheduler.running:
        scheduler.remove_all_jobs()
        scheduler.shutdown()  # Останавливаем планировщик при завершении
        logger.warning("APScheduler остановлен!")


async def start_faststream():
    """
    Запуск FastStream приложения.
    """
    await app.run()


async def main():
    # Роутеры для обработки разных типов взаимодействий
    dp.include_router(admin_router)
    dp.include_router(group_router)
    dp.include_router(stat_router)
    dp.include_router(broadcast_router)
    dp.include_router(task_router)
    # Регистрация событий бота
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    # Запуск FastStream и aiogram параллельно
    try:
        await bot.delete_webhook(drop_pending_updates=True)

        # Создаём задачи для работы aiogram и FastStream
        task_faststream = asyncio.create_task(start_faststream())
        task_aiogram = asyncio.create_task(
            dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        )

        # Запускаем обе задачи
        await asyncio.gather(task_faststream, task_aiogram)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
    