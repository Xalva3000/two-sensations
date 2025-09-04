from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from LEXICON import TOPICS_LIST
from LEXICON.numbers import age_groups
from keyboards.main import get_main_menu_keyboard, get_settings_keyboard

router = Router()


class AboutMeState(StatesGroup):
    waiting_for_about_me = State()


@router.callback_query(F.data == "menu_view_profile")
async def view_my_profile(callback: CallbackQuery):
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
        f"🏙️ Город: {user.get('city', 'Не указан')}\n"
        f"🎯 Интересует возраст: {age_groups.get(user['interested_age'], 'Любой')}\n"
        f"📚 Темы: {topics_text}\n"
    )

    if user.get('about'):
        profile_text += f"\n📖 О себе:\n{user['about']}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="profile_back")]
    ])

    await callback.message.edit_text(profile_text, reply_markup=keyboard)


@router.callback_query(F.data == "edit_about_me")
async def edit_about_me(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 Напишите о себе (максимум 250 символов):\n\n"
        "Расскажите о своих интересах, хобби, чем занимаетесь, "
        "что ищете в собеседнике.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="about_me_cancel")]
        ])
    )
    await state.set_state(AboutMeState.waiting_for_about_me)


@router.message(AboutMeState.waiting_for_about_me)
async def process_about_me(message: Message, state: FSMContext):
    about_me = message.text.strip()
    if len(about_me) > 250:
        await message.answer("❌ Слишком длинный текст. Максимум 250 символов.")
        return
    print(message.from_user.id,)
    await db.update_about_me(message.from_user.id, about_me)
    # await message.answer()
    await state.clear()
    menu_title = "✅ Информация о себе сохранена!"
    await message.answer(
        text=f"_____{menu_title}_____",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(AboutMeState.waiting_for_about_me, F.data == "about_me_cancel")
async def about_me_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "profile_back")
async def profile_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )