from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from config.config import bot
from utils.csv_download import extract_data_from_csv
from database.dao import add_many, delete_chanel, delete_group
from keyboards.keyboards import main_kb
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from utils.csv_download import extract_data_from_csv
from keyboards.keyboards import cancel_keyboard, main_kb
import csv
router = Router()


class AddGroupState(StatesGroup):
    waiting_for_group_name = State()
    waiting_for_csv_file = State()


# Состояния для управления удалением групп и каналов
class DeleteGroupState(StatesGroup):
    waiting_for_group_name = State()


class DeleteChannelState(StatesGroup):
    waiting_for_channel_name = State()


# Обработчик команды "Добавить группу"
@router.callback_query(F.data == "add_group")
async def start_add_group(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Введите название группы для добавления в базу рассылки:",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddGroupState.waiting_for_group_name)


# Обработчик кнопки "Отмена"
@router.message(F.text == "❌ ОТМЕНА")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Действие отменено. Вы вернулись в главное меню.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Главное меню:", reply_markup=main_kb())


# Обрабатываем ввод названия группы
@router.message(AddGroupState.waiting_for_group_name)
async def receive_group_name(message: Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    await message.answer(
        "Принято! Теперь отправьте CSV-файл с данными или нажмите 'Отмена', чтобы выйти.",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddGroupState.waiting_for_csv_file)


# Обрабатываем отправленный файл
@router.message(AddGroupState.waiting_for_csv_file)
async def process_csv_file(message: Message, state: FSMContext):
    # Проверяем, был ли отправлен файл
    if not message.document:
        await message.answer(
            "❌ Ошибка: Пожалуйста, отправьте CSV-файл с данными или нажмите 'Отмена' для завершения.",
            reply_markup=cancel_keyboard()
        )
        return

    # Проверяем MIME-тип файла
    if message.document.mime_type != "text/csv" and not message.document.file_name.endswith(".csv"):
        await message.answer(
            "❌ Ошибка: Неверный тип файла. Пожалуйста, убедитесь, что вы отправляете CSV-файл.",
            reply_markup=cancel_keyboard()
        )
        return

    try:
        # Загружаем файл через Telegram API
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_content = await bot.download_file(file.file_path)

        # Проверка: файл не пустой
        if file_content.seek(0, 2) == 0:  # Проверяем длину файла (если 0, то файл пуст)
            await message.answer(
                "❌ Ошибка: Файл пустой. Убедитесь, что он содержит данные.",
                reply_markup=cancel_keyboard()
            )
            return
        
        file_content.seek(0)  # Сбрасываем указатель на начало файла для чтения

        # Получение данных из предыдущего шага
        state_data = await state.get_data()
        group_name = state_data.get("group_name", "Неизвестная группа")

        # Чтение содержимого CSV
        try:
            data_list = extract_data_from_csv(name=group_name, file_data=file_content.read())
        except (UnicodeDecodeError, csv.Error) as e:
            await message.answer(
                f"❌ Ошибка: Некорректный формат файла. Проверьте, что CSV имеет кодировку UTF-8 и правильную структуру.\n\nДетали: {e}",
                reply_markup=cancel_keyboard()
            )
            return

        # Проверка, удалось ли что-то извлечь
        if not data_list:
            await message.answer(
                "⚠️ Ошибка: Файл либо пустой, либо его структура неверна. Убедитесь, что данные указаны верно.",
                reply_markup=cancel_keyboard()
            )
            return

        # Добавляем обработанные данные в базу
        try:
            await add_many(data=data_list)
        except Exception as db_error:
            await message.answer(
                f"🔴 Ошибка сохранения данных в базу: {db_error}",
                reply_markup=cancel_keyboard()
            )
            return

        # Успешное добавление
        await message.answer(
            f"✅ Файл обработан успешно! В БД добавлено {len(data_list)} записей."
        )

        # Очистка состояния
        await state.clear()

        # Возврат в главное меню
        await message.answer("🔄 Возврат в главное меню.", reply_markup=ReplyKeyboardRemove())
        await message.answer("Главное меню:", reply_markup=main_kb())

    except UnicodeDecodeError:
        await message.answer(
            "❌ Ошибка: Файл не удалось прочитать. Убедитесь, что он находится в кодировке UTF-8.",
            reply_markup=cancel_keyboard()
        )
    except FileNotFoundError:
        await message.answer(
            "❌ Ошибка: Файл не найден или возникла проблема при загрузке. Попробуйте отправить его снова.",
            reply_markup=cancel_keyboard()
        )
    except Exception as error:
        await message.answer(
            f"🔴 Ошибка при обработке файла: {error}",
            reply_markup=cancel_keyboard()
        )


# Удаление группы
@router.callback_query(F.data == "delete_group")
async def start_delete_group(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Введите название группы для удаления из базы рассылки:",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(DeleteGroupState.waiting_for_group_name)


@router.message(DeleteGroupState.waiting_for_group_name)
async def process_delete_group(message: Message, state: FSMContext):
    group_name = message.text

    # Удаляем группу из базы
    deleted_count = await delete_group(name_group=group_name)

    await message.answer(
        f"✅ Группа *'{group_name}'* успешно удалена из БД. Всего удалено записей: {deleted_count}"
    )
    # Возврат в главное меню
    await state.clear()
    await message.answer("🔄 Возврат в главное меню.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Главное меню:", reply_markup=main_kb())


# Удаление канала
@router.callback_query(F.data == "delete_chanel")
async def start_delete_channel(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Введите название канала для удаления из базы рассылки:",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(DeleteChannelState.waiting_for_channel_name)


@router.message(DeleteChannelState.waiting_for_channel_name)
async def process_delete_channel(message: Message, state: FSMContext):
    channel_name = message.text

    # Удаляем канал из базы
    deleted_count = await delete_chanel(name_chanel=channel_name)

    await message.answer(
        f"✅ Канал *'{channel_name}'* успешно удалён из БД. Всего удалено записей: {deleted_count}"
    )
    # Возврат в главное меню
    await state.clear()
    await message.answer("🔄 Возврат в главное меню.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Главное меню:", reply_markup=main_kb())
