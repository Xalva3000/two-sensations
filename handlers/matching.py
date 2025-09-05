from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from LEXICON import TOPICS_LIST
from LEXICON.numbers import age_groups
from database import db
from keyboards.main import get_profile_action_keyboard

router = Router()

# Список тем для отображения



@router.callback_query(F.data == "menu_search")
async def menu_search(callback: CallbackQuery):
    user_id = callback.from_user.id
    await find_match(callback.message, user_id)


async def set_outer_companion(user_id: int, new_companion_id: int):
    await db.set_outer_companion(user_id, new_companion_id)

async def find_match(message: Message, user_id: int):
    user = await db.get_user(user_id)

    if not user or not user.get('gender') or not user.get('age'):
        await message.answer("Сначала заполните анкету!")
        return

    match = await db.get_random_user(user_id)
    if not match:
        await message.answer("Пока нет подходящих анкет. Попробуйте позже!")
        return

    # Формируем список тем для отображения
    match_topics = match.get('topics', [])
    topics_text = ""
    if match_topics:
        topics_names = [TOPICS_LIST[i - 1] for i in match_topics if 1 <= i <= 20]
        topics_text = f"📝 Темы: {', '.join(topics_names)}"

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
    photo = match.get('photo_id', match['photo_id'])
    if photo:
        await message.answer_photo(
            photo,
            caption=caption,
            reply_markup=get_profile_action_keyboard(match['telegram_id'])
        )
    else:
        await message.answer(
            text=caption,
            reply_markup=get_profile_action_keyboard(match['telegram_id'])
        )


@router.callback_query(F.data.startswith("reject_profile_"))
async def reject_profile(callback: CallbackQuery):

    user_id = callback.from_user.id # await db.get_seeker_id(callback.from_user.id)
    # Получение отклоненного пользователя
    new_companion_id = int(callback.data.replace('reject_profile_', ''))

    await callback.answer("Анкета отклонена")
    await callback.message.delete()

    # Показываем следующую анкету
    # await find_match(callback.message, user_id)


@router.callback_query(F.data.startswith("accept_outer_profile_"))
async def accept_outer_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    # получение id принятого собеседника
    new_companion_id = int(callback.data.replace('accept_outer_profile_', ''))
    await set_outer_companion(user_id, new_companion_id)
    # Здесь логика принятия собеседника
    await callback.answer("Контакт отправлен!")
    await callback.message.delete()
    await callback.message.answer(
        "Вот контакт пользователя: @username\n"
        "Свяжитесь с ним для общения!"
    )
