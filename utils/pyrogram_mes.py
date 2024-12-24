from config.config import broker, scheduler
import asyncio
from loguru import logger
from pyrogram.errors import RPCError, FloodWait
from pyrogram.types import Chat
from pyrogram import Client
from config.config import settings
from datetime import datetime, timedelta
from typing import List, Dict, Any


async def broadcast_message_chat(group: List[str], message: str) -> None:
    """
    Отправляет сообщение в список чатов (групп), используя клиента Pyrogram.

    Для каждого чата в списке выполняется попытка отправить сообщение.
    В случае ошибки (FloodWait, RPCError и другие) добавляются соответствующие записи в журнал.
    Для предотвращения FloodWait делается задержка между отправками сообщений.

    Аргументы:
        group (List[str]): Список строк, содержащих имена групп или ссылки на группы.
        message (str): Сообщение, которое будет отправлено в указанные чаты.

    Логирование:
        - Записываются успешные и неудачные попытки отправки сообщений.
        - Обрабатываются ошибки FloodWait, RPCError и другие исключения.

    Исключение:
        Функция не выбрасывает исключений, все ошибки обрабатываются локально.
    """
    u_bot: Client = Client(
        name=settings.LOGIN, api_id=settings.API_ID, api_hash=settings.API_HASH
    )

    good: int = 0  # Количество успешно отправленных сообщений
    bad: int = 0  # Количество ошибок при отправке
    total: int = len(group)

    # Асинхронная работа с клиентом Pyrogram
    async with u_bot:
        for idx, name in enumerate(group, start=1):
            try:
                # Извлекаем идентификатор чата из ссылки или имени
                group_name: str = name.split("/")[-1]
                chat: Chat = await u_bot.get_chat(group_name)
                chat_id: int = chat.id

                # Отправляем сообщение в чат
                await u_bot.send_message(chat_id=chat_id, text=message)

                # Увеличиваем счетчик успешных отправок
                good += 1
                logger.info(f"Сообщение успешно отправлено в {group_name}")

            except FloodWait as e:
                # Обрабатываем FloodWait (лимит частоты запросов)
                logger.warning(f"FloodWait: ожидание {e.value} секунд...")
                await asyncio.sleep(e.value)
            except RPCError as e:
                # Обработка ошибок от Pyrogram
                bad += 1
                logger.error(f"RPC ошибка при отправке в {name}: {e}")
            except Exception as e:
                # Обработка любых других ошибок
                bad += 1
                logger.exception(f"Непредвиденная ошибка в канале {name}: {e}")

            # Добавляем фиксированную задержку между запросами для предотвращения блокировок
            await asyncio.sleep(5)

        # Итоговый результат рассылки
        logger.info(f"Всего обработано: успешно {good}, ошибки {bad}, общее {total}")

    # Останавливаем клиент Pyrogram
    await u_bot.stop()


@broker.subscriber("broadcast_task_interval")
async def broadcast_task(data: Dict[str, Any]) -> None:
    """
    Обрабатывает задачу для периодической рассылки сообщений в чаты по заданному интервалу.

    Использует планировщик задач (scheduler) для автоматической рассылки сообщений по заданному интервалу времени.

    Аргументы:
        data (Dict[str, Any]): Словарь, содержащий:
            - "group": List[str] — список чатов для рассылки.
            - "message": str — текст сообщения.
            - "time": int — интервал (в минутах) между повторными рассылками.

    """
    group_list: List[str] = data["group"]
    message: str = data["message"]
    time: int = int(data["time"])

    # Добавление задачи в планировщик с триггером на интервал
    scheduler.add_job(
        func=broadcast_message_chat,
        args=[group_list, message],
        trigger="interval",
        minutes=time,
        name=f"Периодическая рассылка в {group_list}",
    )


@broker.subscriber("broadcast_task_now")
async def broadcast_task_now(data: Dict[str, Any]) -> None:
    """
    Обрабатывает задачу для немедленной рассылки сообщений в чаты с небольшой задержкой.

    Используется планировщик задач (scheduler) с триггером на определенную дату и время (+5 секунд от текущего момента).

    Аргументы:
        data (Dict[str, Any]): Словарь, содержащий:
            - "group": List[str] — список чатов для рассылки.
            - "message": str — текст сообщения.
    """
    run_time: datetime = datetime.now() + timedelta(seconds=5)
    group_list: List[str] = data["group"]
    message: str = data["message"]

    # Добавление задачи с фиксированной датой и временем выполнения
    scheduler.add_job(
        func=broadcast_message_chat,
        args=[group_list, message],
        trigger="date",
        run_date=run_time,
        name=f"Немедленная рассылка в {group_list}",
    )
