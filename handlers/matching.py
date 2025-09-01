from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database import db
from keyboards.main import get_profile_action_keyboard

router = Router()

# Список тем для отображения
TOPICS_LIST = [
    "💼 Работа", "🎬 Кино", "🎵 Музыка", "📚 Книги",
    "🏀 Спорт", "🎮 Игры", "🍳 Кулинария", "✈️ Путешествия",
    "💻 Технологии", "🎨 Искусство", "🐶 Животные", "🌿 Природа",
    "🏋️ Фитнес", "🎭 Театр", "📺 Сериалы", "💰 Финансы",
    "🧠 Психология", "👶 Дети", "🚗 Авто", "🏠 Дом"
]


@router.callback_query(F.data == "menu_search")
async def menu_search(callback: CallbackQuery):
    await find_match(callback.message)


async def find_match(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user.get('gender') or not user.get('age'):
        await message.answer("Сначала заполните анкету!")
        return

    match = await db.get_random_user(message.from_user.id)

    if not match:
        await message.answer("Пока нет подходящих анкет. Попробуйте позже!")
        return

    # Формируем список тем для отображения
    match_topics = match.get('topics', [])
    topics_text = ""
    if match_topics:
        topics_names = [TOPICS_LIST[i - 1] for i in match_topics if 1 <= i <= 20]
        topics_text = f"📝 Темы: {', '.join(topics_names)}"

    age_groups = {
        1: "18-20", 2: "20-24", 3: "25-29", 4: "30-34",
        5: "35-39", 6: "40-44", 7: "45-49", 8: "50-54", 9: "55-60"
    }

    caption = (
        f"👤 {match['first_name']}\n"
        f"🎂 Возраст: {age_groups.get(match['age'], 'Не указан')}\n"
        f"👫 Пол: {'Мужской' if match['gender'] == 1 else 'Женский'}\n"
    )

    if match.get('city'):
        caption += f"🏙️ Город: {match['city']}\n"

    if topics_text:
        caption += f"{topics_text}\n"

    # Сохраняем ID найденного пользователя для последующих действий
    # Можно использовать FSM или временное хранилище

    await message.answer_photo(
        match.get('photo', 'AgACAgIAAxkBAAIB...'),  # Заглушка для фото
        caption=caption,
        reply_markup=get_profile_action_keyboard()
    )


@router.callback_query(F.data == "reject_profile")
async def reject_profile(callback: CallbackQuery):
    current_seeker_id = await db.get_seeker_id(callback.from_user.id)
    # Здесь нужно получить ID отклоняемого пользователя
    # Для реализации нужно хранить последнего показанного пользователя

    await callback.answer("Анкета отклонена")
    await callback.message.delete()

    # Показываем следующую анкету
    await find_match(callback.message)


@router.callback_query(F.data == "accept_profile")
async def accept_profile(callback: CallbackQuery):
    # Здесь логика принятия собеседника
    await callback.answer("Контакт отправлен!")
    await callback.message.delete()
    await callback.message.answer(
        "Вот контакт пользователя: @username\n"
        "Свяжитесь с ним для общения!"
    )