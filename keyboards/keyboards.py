from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def main_kb():
    keyboard = [
        [InlineKeyboardButton(text="➕ ДОБАВИТЬ ГРУППУ", callback_data="add_group")],
        [InlineKeyboardButton(text="➖ УДАЛИТЬ ГРУППУ", callback_data="delete_group")],
        [InlineKeyboardButton(text="💭 УДАЛИТЬ КАНАЛ", callback_data="delete_chanel")],
        [InlineKeyboardButton(text="👥 СТАТИСТИКА ГРУПП", callback_data="statistic")],
        [InlineKeyboardButton(text="📩 РАССЫЛКА", callback_data="broadcast")],
        [
            InlineKeyboardButton(
                text="📌 ПОКАЗАТЬ АКТИВНЫЕ ТАСКИ", callback_data="active_task"
            )
        ],
        [InlineKeyboardButton(text="🗑 ОЧИСТИТЬ ВСЕ ТАСКИ", callback_data="clear_task")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def cancel_keyboard(n: int = 0):
    buttons = [[KeyboardButton(text="❌ ОТМЕНА")]]
    if n == 1:
        buttons.append([KeyboardButton(text="➡️ ПРОПУСТИТЬ")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Вернуться назад",
    )

    return keyboard


def confirm():
    buttons = [[KeyboardButton(text="✅ ДА"), KeyboardButton(text="❌ НЕТ")]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Подтвердить",
    )
    return keyboard
