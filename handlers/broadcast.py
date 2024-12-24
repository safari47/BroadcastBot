from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import Router, F
from keyboards.keyboards import cancel_keyboard, confirm, main_kb
from aiogram.enums import ContentType
from database.dao import find_all
from utils.pyrogram_mes import broadcast_message_chat
from config.config import broker

router = Router()


class Broadcast(StatesGroup):
    message = State()
    time = State()
    group = State()
    confirm = State()


@router.callback_query(F.data == "broadcast")
async def start_broadcast(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Broadcast.message)
    await call.message.answer(
        "📢 Пожалуйста, отправьте сообщение для рассылки!\n\n"
        "Можно использовать:\n"
        "- Текст 🖊\n"
        "- Фото 🖼\n"
        "- Видео 🎥\n"
        "- Видео-сообщение (кружок) 📹\n\n"
        "Вы также можете добавить опциональную подпись к вашему содержимому.\n\n"
        "👉 Как только вы будете готовы, просто отправьте файл, видео или текст.",
        reply_markup=cancel_keyboard(),
    )


@router.message(Broadcast.message)
async def broadcast_message(message: Message, state: FSMContext):
    await state.update_data(message=message)
    await state.set_state(Broadcast.time)
    await message.answer(
        f"Введите число в минутах с каким интервалом отправлять или ниже кнопку пропустить, для отправки сразу единожды",
        reply_markup=cancel_keyboard(n=1),
    )


@router.message(Broadcast.time)
async def broadcast_time(message: Message, state: FSMContext):
    # Проверяем, что введенное число является числом или равно "➡️ ПРОПУСТИТЬ"
    if not (message.text.isdigit() or message.text == "➡️ ПРОПУСТИТЬ"):
        await message.answer(
            "Ошибка: Введите число или нажмите 'Пропустить'.",
            reply_markup=cancel_keyboard(n=1),
        )
        return
    await state.update_data(time=message.text)
    await state.set_state(Broadcast.group)
    await message.answer(
        "Принято! Теперь отправьте название группы каналов, куда будет рассылка.\n\n"
        "🗂 Укажите название группы или каналов одним сообщением.",
        reply_markup=cancel_keyboard(),
    )



@router.message(Broadcast.group)
async def broadcast_group(message: Message, state: FSMContext):
    # Сохраняем введённую группу
    group_data = await find_all(group_name=message.text)
    if len(group_data) == 0:
        await message.answer(
            "*Группа не найдена.*\nПожалуйста, проверьте правильность введённого названия группы.",
            reply_markup=cancel_keyboard(),
            parse_mode="Markdown",
        )
        return

    await state.update_data(group=message.text)
    data = await state.get_data()
    group_name = data["group"]
    message_data = data["message"]
    time = data["time"]

    # Формируем текст предпросмотра
    await message.answer(
        f"✅ *Предварительный просмотр сообщения:*\n\n👥 Группа для рассылки: {group_name},\n\n Интервал рассылки {time} минут",
        parse_mode="Markdown",
    )
    await message.answer(text=message_data.text)
    # Сообщаем о следующем шаге
    await message.answer(
        "Нажмите *'✅ ДА'* для подтверждения рассылки или *'❌ НЕТ'* для отмены.",
        reply_markup=confirm(),
        parse_mode="Markdown",
    )

    # Переходим к состоянию подтверждения
    await state.set_state(Broadcast.confirm)


@router.message(Broadcast.confirm)
async def broadcast_confirm(message: Message, state: FSMContext):
    # Записываем выбор пользователя в состояние
    user_choice = message.text
    if user_choice not in ["✅ ДА", "❌ НЕТ"]:
        await message.answer("⛔️ Используйте кнопки для выбора!")
        return

    await state.update_data(confirm=user_choice)

    if user_choice == "❌ НЕТ":
        # Отмена рассылки
        await message.answer(
            "❌ Рассылка отменена.", reply_markup=ReplyKeyboardRemove()
        )
        await message.answer("Возвращение в главное меню.", reply_markup=main_kb())
        await state.clear()
    elif user_choice == "✅ ДА":
        # Достаём данные из состояния
        data = await state.get_data()
        message_data = data["message"].text
        group_name = data["group"]
        time = data["time"]
        group_list = await find_all(group_name=group_name)
        data = {"group": group_list, "message": message_data, "time": time}
        if time.isdigit():
            await broker.publish(data, channel="broadcast_task_interval")
            await message.answer(
                f"�� Задача для рассылки успешно отправлена в планировщик.\n\nГруппа для рассылки: {group_name},\n\nИнтервал рассылки {time} минут.",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            await broker.publish(data, channel="broadcast_task_now")
            await message.answer(
                f"Задача для рассылки успешно отправлена в планировщик.\n\nГруппа для рассылки: {group_name},\n\nРассылка будет отправлена сразу.",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardRemove(),
            )

        # Очищаем состояние
        await state.clear()

        await message.answer("Главное меню:", reply_markup=main_kb())
