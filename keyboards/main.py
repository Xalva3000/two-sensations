from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_language_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Русский", callback_data="lang_ru"),
        InlineKeyboardButton("English", callback_data="lang_en")
    )
    return keyboard

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("👤 Заполнить анкету"),
        KeyboardButton("✏️ Редактировать анкету"),
        KeyboardButton("🔍 Найти собеседника")
    )
    return keyboard

