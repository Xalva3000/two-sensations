from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from LEXICON import TOPICS_LIST
from LEXICON.numbers import age_groups
from database import db
from keyboards.main import get_profile_action_keyboard

router = Router()

# Список тем для отображения

def get_matching_close_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Закрыть", callback_data="matching_close")]
    ])

@router.callback_query(F.data == "menu_search")
async def menu_search(callback: CallbackQuery):
    user_id = callback.from_user.id
    await find_match(callback.message, user_id)


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
                "• Проверить позже",
                reply_markup=get_matching_close_keyboard(),
            )
            return

        # Форматируем текст профиля
        profile_text = format_profile_text(match)

        # Отправляем профиль
        await send_profile_message(message, match, profile_text)

    except Exception as e:
        await message.answer("❌ Произошла ошибка при поиске. Попробуйте позже.")


def format_profile_text(match):
    """Форматирует текст профиля для отображения"""
    text = (
        f"👤 {match.get('first_name', 'Пользователь')}\n"
        f"👫 Пол: {'Мужской' if match.get('gender') == 1 else 'Женский'}\n"
        f"🎂 Возраст: {age_groups.get(match.get('age'), 'Не указан')}\n"
        f"🎯 Ищу возраст: {age_groups.get(match.get('interested_age'), 'Не указан')}\n"
    )

    if match.get('city'):
        text += f"🏙️ Город: {match['city']}\n"

    if match.get('about'):
        text += f"\n📖 О себе:\n{match['about']}\n"

    # Темы
    match_topics = match.get('topics', [])
    if match_topics:
        topics_names = [TOPICS_LIST[i - 1] for i in match_topics if 1 <= i <= len(TOPICS_LIST)]
        if topics_names:
            text += f"\n🎯 Ощущения: {', '.join(topics_names[:8])}"  # Показываем первые 8 тем
            if len(topics_names) > 8:
                text += f" и ещё {len(topics_names) - 8}..."

    # Контактная информация
    # username = match.get('username')
    # if username:
    #     text += f"\n👤 @{username}"

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

    # user_id = callback.from_user.id
    # Получение отклоненного пользователя
    # new_companion_id = int(callback.data.replace('reject_profile_', ''))

    await callback.answer("Анкета отклонена")
    await callback.message.delete()



# @router.callback_query(F.data.startswith("accept_outer_profile_"))
# async def accept_outer_profile(callback: CallbackQuery):
#     # получение своего id
#     user_id = callback.from_user.id
#     # получение id принятого собеседника
#     new_companion_id = int(callback.data.replace('accept_outer_profile_', ''))
#
#     # Установка найденного пользователя в свои собеседники
#     await db.add_connection(user_id, new_companion_id)
#     await callback.answer("Контакт отправлен!")
#     await callback.message.delete()
#     await callback.message.answer(
#         "Вот контакт пользователя: @username\n"
#         "Свяжитесь с ним для общения!"
#     )

@router.callback_query(F.data.startswith("matching_close"))
async def matching_close(callback: CallbackQuery):
    await callback.message.delete()

