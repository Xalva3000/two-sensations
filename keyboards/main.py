from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_1")],
        [InlineKeyboardButton(text="English 🇺🇸", callback_data="lang_2")]
    ])

def get_gender_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужской", callback_data="gender_1")],
        [InlineKeyboardButton(text="👩 Женский", callback_data="gender_2")]
    ])

def get_age_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="18-20", callback_data="age_1")],
        [InlineKeyboardButton(text="20-24", callback_data="age_2")],
        [InlineKeyboardButton(text="25-29", callback_data="age_3")],
        [InlineKeyboardButton(text="30-34", callback_data="age_4")],
        [InlineKeyboardButton(text="35-39", callback_data="age_5")],
        [InlineKeyboardButton(text="40-44", callback_data="age_6")],
        [InlineKeyboardButton(text="45-49", callback_data="age_7")],
        [InlineKeyboardButton(text="50-54", callback_data="age_8")],
        [InlineKeyboardButton(text="55-60", callback_data="age_9")]
    ])

def get_interested_age_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="18-20", callback_data="iage_1")],
        [InlineKeyboardButton(text="20-24", callback_data="iage_2")],
        [InlineKeyboardButton(text="25-29", callback_data="iage_3")],
        [InlineKeyboardButton(text="30-34", callback_data="iage_4")],
        [InlineKeyboardButton(text="35-39", callback_data="iage_5")],
        [InlineKeyboardButton(text="40-44", callback_data="iage_6")],
        [InlineKeyboardButton(text="45-49", callback_data="iage_7")],
        [InlineKeyboardButton(text="50-54", callback_data="iage_8")],
        [InlineKeyboardButton(text="55-60", callback_data="iage_9")]
    ])

def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Заполнить анкету заново", callback_data="menu_restart")],
        [InlineKeyboardButton(text="🎭 Темы для общения", callback_data="menu_topics")],
        [InlineKeyboardButton(text="📸 Добавить фото", callback_data="menu_photo")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")],
        [InlineKeyboardButton(text="🔍 Найти собеседника", callback_data="menu_search")]
    ])

def get_settings_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏙️ Указать город", callback_data="settings_city")],
        [InlineKeyboardButton(text="🌍 Поиск только в городе", callback_data="settings_city_only")],
        [InlineKeyboardButton(text="📸 Только с фото", callback_data="settings_photo_required")],
        [InlineKeyboardButton(text="👁️ Скрыть из поиска", callback_data="settings_hide")],
        [InlineKeyboardButton(text="❌ Удалить собеседника", callback_data="settings_remove_companion")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_back")]
    ])

def get_profile_action_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data="accept_profile"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data="reject_profile")
        ]
    ])


def get_topics_keyboard(selected_topics=None):
    if selected_topics is None:
        selected_topics = []

    topics = [
        "💼 Работа", "🎬 Кино", "🎵 Музыка", "📚 Книги",
        "🏀 Спорт", "🎮 Игры", "🍳 Кулинария", "✈️ Путешествия",
        "💻 Технологии", "🎨 Искусство", "🐶 Животные", "🌿 Природа",
        "🏋️ Фитнес", "🎭 Театр", "📺 Сериалы", "💰 Финансы",
        "🧠 Психология", "👶 Дети", "🚗 Авто", "🏠 Дом"
    ]

    keyboard = []
    for i in range(0, len(topics), 2):
        row = []
        # Первая тема в ряду
        topic1_text = f"✅ {topics[i]}" if i + 1 in selected_topics else topics[i]
        row.append(InlineKeyboardButton(text=topic1_text, callback_data=f"topic_{i + 1}"))

        # Вторая тема в ряду (если есть)
        if i + 1 < len(topics):
            topic2_text = f"✅ {topics[i + 1]}" if i + 2 in selected_topics else topics[i + 1]
            row.append(InlineKeyboardButton(text=topic2_text, callback_data=f"topic_{i + 2}"))

        keyboard.append(row)

    # Кнопки действий
    keyboard.append([InlineKeyboardButton(text="✅ Сохранить", callback_data="topics_save")])
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="topics_back")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_topics_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎭 Выбрать темы", callback_data="topics_edit")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="topics_back_to_main")]
    ])

def get_boolean_choice_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="boolean_yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="boolean_no")
        ],
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data="boolean_cancel")]
    ])

def get_photo_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Отмена", callback_data="photo_cancel"),
        ],
    ])