from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_gender_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("👨 Мужской"),
        KeyboardButton("👩 Женский")
    )
    return keyboard

def get_topics_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    topics = [
        "🎬 Кино", "🎵 Музыка", "📚 Книги", "🏀 Спорт",
        "🎮 Игры", "🍳 Кулинария", "✈️ Путешествия", "💻 Технологии"
    ]
    
    for i in range(0, len(topics), 2):
        if i + 1 < len(topics):
            keyboard.add(
                InlineKeyboardButton(topics[i], callback_data=f"topic_{topics[i]}"),
                InlineKeyboardButton(topics[i+1], callback_data=f"topic_{topics[i+1]}")
            )
        else:
            keyboard.add(InlineKeyboardButton(topics[i], callback_data=f"topic_{topics[i]}"))
    
    keyboard.add(InlineKeyboardButton("✅ Готово", callback_data="topics_done"))
    return keyboard

def get_profile_action_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Принять", callback_data="accept_profile"),
        InlineKeyboardButton("❌ Отклонить", callback_data="reject_profile")
    )
    return keyboard

