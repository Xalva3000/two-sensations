from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="English", callback_data="lang_en")
            ]
        ]
    )

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Заполнить анкету")],
            [KeyboardButton(text="✏️ Редактировать анкету")],
            [KeyboardButton(text="🔍 Найти собеседника")]
        ],
        resize_keyboard=True
    )

