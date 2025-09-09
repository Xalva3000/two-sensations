from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from LEXICON import TOPICS_LIST

#
# def get_language_keyboard():
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_1")],
#         [InlineKeyboardButton(text="English 🇺🇸", callback_data="lang_2")]
#     ])

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
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="menu_view_profile")],
        [InlineKeyboardButton(text="🎭 Выбрать ощущения", callback_data="menu_topics")],
        [InlineKeyboardButton(text="👥 Мои собеседники", callback_data="menu_companions")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")],
        [InlineKeyboardButton(text="🔍 Найти собеседника", callback_data="menu_search")]
    ])

def get_settings_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Изменить анкету ", callback_data="settings_restart_profile")],
        [InlineKeyboardButton(text="📞 Импорт моего контакта", callback_data="settings_import_contact")],
        [InlineKeyboardButton(text="✏️ Редактировать 'О себе'", callback_data="edit_about_me")],
        [InlineKeyboardButton(text="📸 Добавить фото", callback_data="menu_photo")],
        [InlineKeyboardButton(text="📸 Искать только с фото", callback_data="settings_photo_required")],
        [InlineKeyboardButton(text="🏙️ Указать город", callback_data="settings_city")],
        [InlineKeyboardButton(text="🌍 Поиск только в городе", callback_data="settings_city_only")],
        [InlineKeyboardButton(text="👁️ Скрыть себя из поиска", callback_data="settings_hide")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_back")],
    ])

def get_profile_action_keyboard(suggestion_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_outer_profile_{suggestion_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_profile_{suggestion_id}"),
        ],
        [
            InlineKeyboardButton(text="Закрыть", callback_data=f"companions_cancel"),
        ],
    ])


# def get_topics_keyboard(selected_topics=None):
#     topics = TOPICS_LIST
#     if selected_topics is None:
#         selected_topics = []
#
#     keyboard = []
#     for i in range(0, len(topics), 2):
#         row = []
#         # Первая тема в ряду
#         topic1_text = f"✅ {topics[i]}" if i + 1 in selected_topics else topics[i]
#         row.append(InlineKeyboardButton(text=topic1_text, callback_data=f"topic_{i + 1}"))
#
#         # Вторая тема в ряду (если есть)
#         if i + 1 < len(topics):
#             topic2_text = f"✅ {topics[i + 1]}" if i + 2 in selected_topics else topics[i + 1]
#             row.append(InlineKeyboardButton(text=topic2_text, callback_data=f"topic_{i + 2}"))
#
#         keyboard.append(row)
#
#     # Кнопки действий
#     keyboard.append([InlineKeyboardButton(text="✅ Сохранить", callback_data="topics_save")])
#     keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="topics_back")])
#
#     return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_topics_keyboard(selected_topics=None, is_registration=False):
    if selected_topics is None:
        selected_topics = []

    # Список из 36 тем
    topics = TOPICS_LIST

    keyboard = []

    # Разбиваем на 3 столбца по 12 тем в каждом
    topics_per_column = 12
    total_columns = 3

    # Создаем строки для каждого столбца
    for row in range(topics_per_column):
        keyboard_row = []
        for col in range(total_columns):
            topic_index = col * topics_per_column + row
            if topic_index < len(topics):
                topic_idx = topic_index + 1
                topic_text = topics[topic_index]

                # Сокращаем длинные названия
                if len(topic_text) > 10:
                    topic_text = topic_text.split(' ')[0]  # Берем только первое слово

                indicator = "✅ " if topic_idx in selected_topics else ""
                btn_text = f"{indicator}{topic_text}"

                keyboard_row.append(InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"topic_{topic_idx}"
                ))

        if keyboard_row:  # Добавляем только непустые строки
            keyboard.append(keyboard_row)

    # Кнопки действий
    keyboard.append([InlineKeyboardButton(text="💾 Сохранить выбранное", callback_data="topics_save")])

    if not is_registration:
        keyboard.append([InlineKeyboardButton(text="🗑️ Очистить все", callback_data="topics_clear")])
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="topics_back")])
    else:
        keyboard.append([InlineKeyboardButton(text="🗑️ Очистить все", callback_data="registration_topics_clear")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_topics_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎭 Выбрать ощущения", callback_data="topics_edit")],
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

def get_companions_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="👤 Тот, кого я нашел",
                callback_data="menu_view_outer_companion")],
            [InlineKeyboardButton(
                text="👤 Тот, кто меня нашел",
                callback_data="menu_view_income_companion")],
            # [InlineKeyboardButton(
            #     text="❌ Удалить найденного собеседника",
            #     callback_data="settings_remove_outer_companion")],
            # [InlineKeyboardButton(
            #     text="❌ Удалить нашедшего собеседника",
            #     callback_data="settings_remove_income_companion")],
            [InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="companions_back")]
        ])
