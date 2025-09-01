from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👨 Мужской")],
            [KeyboardButton(text="👩 Женский")]
        ],
        resize_keyboard=True
    )


def get_topics_keyboard(selected_topics=None):
    if selected_topics is None:
        selected_topics = []

    topics = [
        "🎬 Кино", "🎵 Музыка", "📚 Книги", "🏀 Спорт",
        "🎮 Игры", "🍳 Кулинария", "✈️ Путешествия", "💻 Технологии"
    ]

    keyboard = []
    for i in range(0, len(topics), 2):
        row = []
        # Добавляем галочку к выбранным темам
        topic1_text = f"✅ {topics[i]}" if topics[i] in selected_topics else topics[i]
        row.append(InlineKeyboardButton(text=topic1_text, callback_data=f"topic_{topics[i]}"))

        if i + 1 < len(topics):
            topic2_text = f"✅ {topics[i + 1]}" if topics[i + 1] in selected_topics else topics[i + 1]
            row.append(InlineKeyboardButton(text=topic2_text, callback_data=f"topic_{topics[i + 1]}"))

        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="✅ Готово", callback_data="topics_done")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_profile_action_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data="accept_profile"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data="reject_profile")
            ]
        ]
    )
