from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import db
from LEXICON import TOPICS_LIST
from LEXICON.numbers import age_groups

# profile router
router = Router()




@router.callback_query(F.data == "menu_view_profile")
async def view_my_profile(callback: CallbackQuery):
    """Сбор и вывод пользовательского профиля"""
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден")
        return

    # Получаем темы пользователя
    topics = await db.get_user_topics(callback.from_user.id)
    topics_text = ", ".join([TOPICS_LIST[i - 1] for i in topics]) if topics else "Не выбраны"
    profile_text = (
        f"👤 Ваш профиль:\n\n"
        f"📝 Имя: {user['first_name']}\n"
        f"🎂 Возраст: {age_groups.get(user['age'], 'Не указан')}\n"
        f"👫 Пол: {'Мужской' if user['gender'] == 1 else 'Женский'}\n"
        f"🏙️ Город: {user.get('city', 'Не указан') or 'Не указан'}\n"
        f"🎯 Интересует возраст: {age_groups.get(user['interested_age'], 'Любой')}\n"
        f"📚 Темы: {topics_text}\n"
    )

    if user.get('about'):
        profile_text += f"\n📖 О себе:\n{user['about']}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="profile_back")]
    ])

    # await callback.message.edit_text(profile_text, reply_markup=keyboard)

    photo = user.get('photo_id', user['photo_id'])
    if photo:
        await callback.message.answer_photo(
            photo,
            caption=profile_text,
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            text=profile_text,
            reply_markup=keyboard
        )


@router.callback_query(F.data == "profile_back")
async def profile_back(callback: CallbackQuery):
    """Удаление отображения своего профиля"""
    await callback.message.delete()
    # await callback.message.edit_text(
    #     "Главное меню:",
    #     reply_markup=get_main_menu_keyboard()
    # )
