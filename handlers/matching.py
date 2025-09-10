from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from LEXICON import TOPICS_LIST
from LEXICON.numbers import age_groups
from database import db
from keyboards.connection_keyboards import get_connection_response_keyboard, get_connection_request_keyboard
from keyboards.main import get_profile_action_keyboard

router = Router()

# Список тем для отображения



@router.callback_query(F.data == "menu_search")
async def menu_search(callback: CallbackQuery):
    user_id = callback.from_user.id
    await find_match(callback.message, user_id)


async def set_outer_companion(user_id: int, new_companion_id: int):
    await db.set_outer_companion(user_id, new_companion_id)

# async def find_match(message: Message, user_id: int):
#     user = await db.get_user(user_id)
#
#     if not user or not user.get('gender') or not user.get('age'):
#         await message.answer("Сначала заполните анкету!")
#         return
#
#     match = await db.get_random_user(user_id)
#     if not match:
#         await message.answer("Пока нет подходящих анкет. Попробуйте позже!")
#         return
#
#     # Формируем список тем для отображения
#     match_topics = match.get('topics', [])
#     topics_text = ""
#     if match_topics:
#         topics_names = [TOPICS_LIST[i - 1] for i in match_topics if 1 <= i <= 20]
#         topics_text = f"📝 Темы: {', '.join(topics_names)}"
#
#     profile_text = (
#         f"👤 {match['first_name']}\n"
#         f"🎂 Возраст: {age_groups.get(match['age'], 'Не указан')}\n"
#         f"👫 Пол: {'Мужской' if match['gender'] == 1 else 'Женский'}\n"
#     )
#
#     if match.get('city'):
#         profile_text += f"🏙️ Город: {match['city']}\n"
#
#     if user.get('about'):
#         profile_text += f"\n📖 О себе:\n{user['about']}\n"
#
#     if topics_text:
#         profile_text += f"{topics_text}\n"
#
#     # Сохраняем ID найденного пользователя для последующих действий
#     # Можно использовать FSM или временное хранилище
#     photo = match.get('photo_id', match['photo_id'])
#     if photo:
#         await message.answer_photo(
#             photo,
#             caption=profile_text,
#             reply_markup=get_profile_action_keyboard(match['telegram_id'])
#         )
#     else:
#         await message.answer(
#             text=profile_text,
#             reply_markup=get_profile_action_keyboard(match['telegram_id'])
#         )

async def find_match(message: Message, user_id: int):
    try:
        user = await db.get_user(user_id)

        # Проверяем заполненность анкеты
        required_fields = ['gender', 'age', 'interested_age']
        if not user or any(not user.get(field) for field in required_fields):
            await message.answer(
                "❌ Сначала заполните анкету полностью!\n"
                "Нужно указать: пол, возраст и желаемый возраст"
            )
            return

        match = await db.get_random_user(user_id)

        if not match:
            await message.answer(
                "👀 Пока нет подходящих анкет.\n\n"
                "Попробуйте:\n"
                "• Изменить настройки поиска\n"
                "• Расширить критерии поиска\n"
                "• Проверить позже"
            )
            return

        # Форматируем текст профиля
        profile_text = format_profile_text(match)

        # Отправляем профиль
        await send_profile_message(message, match, profile_text)

    except Exception as e:
        print(f"Ошибка в find_match: {e}")
        await message.answer("❌ Произошла ошибка при поиске. Попробуйте позже.")


def format_profile_text(match):
    """Форматирует текст профиля для отображения"""
    text = (
        f"👤 {match.get('first_name', 'Пользователь')}\n"
        f"🎂 Возраст: {age_groups.get(match.get('age'), 'Не указан')}\n"
        f"👫 Пол: {'Мужской' if match.get('gender') == 1 else 'Женский'}\n"
    )

    if match.get('city'):
        text += f"🏙️ Город: {match['city']}\n"

    if match.get('about_me'):
        text += f"\n📖 О себе:\n{match['about_me']}\n"

    # Темы
    match_topics = match.get('topics', [])
    if match_topics:
        topics_names = [TOPICS_LIST[i - 1] for i in match_topics if 1 <= i <= len(TOPICS_LIST)]
        if topics_names:
            text += f"\n🎯 Темы: {', '.join(topics_names[:8])}"  # Показываем первые 8 тем
            if len(topics_names) > 8:
                text += f" и ещё {len(topics_names) - 8}..."

    # Контактная информация
    username = match.get('username')
    if username:
        if username.startswith('phone_'):
            text += f"\n📞 Телефон: {username.replace('phone_', '')}"
        else:
            text += f"\n👤 @{username}"

    return text


async def send_profile_message(message, match, profile_text):
    """Отправляет сообщение с профилем"""
    photo_id = match.get('photo_id')
    photo_confirmed = match.get('is_photo_confirmed')

    if photo_confirmed and photo_id:
        try:
            await message.answer_photo(
                photo_id,
                caption=profile_text,
                reply_markup=get_profile_action_keyboard(match['telegram_id'])
            )
            return
        except Exception as e:
            print(f"Не удалось отправить фото: {e}")

    # Fallback: текстовое сообщение
    await message.answer(
        text=profile_text,
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

    # Установка найденного пользователя в свои собеседники
    await set_outer_companion(user_id, new_companion_id)
    await callback.answer("Контакт отправлен!")
    await callback.message.delete()
    await callback.message.answer(
        "Вот контакт пользователя: @username\n"
        "Свяжитесь с ним для общения!"
    )

@router.callback_query(F.data.startswith("matching_close"))
async def matching_close(callback: CallbackQuery):

    await callback.message.delete()

