from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards.main import (
    get_settings_keyboard,
    get_boolean_choice_keyboard,
    get_main_menu_keyboard,
    get_gender_keyboard,
)
from handlers.start import RegistrationStates

router = Router()


class SettingsState(StatesGroup):
    waiting_for_city = State()
    waiting_for_city_only = State()
    waiting_for_photo_required = State()
    waiting_for_hide = State()


class AboutMeState(StatesGroup):
    waiting_for_about_me = State()


@router.callback_query(F.data == "settings_restart_profile")
async def settings_restart_profile(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите пол:",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_gender)


@router.callback_query(F.data == "edit_about_me")
async def edit_about_me(callback: CallbackQuery, state: FSMContext):
    """Изменение поля: о себе"""
    await callback.message.edit_text(
        "📝 Напишите о себе (максимум 250 символов):\n\n"
        "Расскажите о своих интересах, хобби, чем занимаетесь, "
        "что ищете в собеседнике.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Отмена", callback_data="about_me_cancel")],
                [InlineKeyboardButton(text="✖️", callback_data="about_me_close")],
            ])
    )
    await state.set_state(AboutMeState.waiting_for_about_me)


@router.message(AboutMeState.waiting_for_about_me)
async def process_about_me(message: Message, state: FSMContext):
    """Прием и валидация текста поля 'о себе'"""
    about_me = message.text.strip()
    if len(about_me) > 250:
        await message.answer("❌ Слишком длинный текст. Максимум 250 символов.")
        return
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
    """Отмена ввода о себе"""
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

@router.callback_query(AboutMeState.waiting_for_about_me, F.data == "about_me_close")
async def about_me_close(callback: CallbackQuery, state: FSMContext):
    """Удаление сообщения ввода о себе"""
    await state.clear()
    await callback.message.delete()


@router.callback_query(F.data == "settings_import_contact")
async def settings_import_contact(callback: CallbackQuery):
    user = callback.from_user
    if user.username:
        # Сохраняем username в базу
        await db.update_username(user.id, user.username)

        await callback.message.edit_text(
            f"✅ Контакт обновлен!\n\n"
            f"Ваш контакт: @{user.username}\n\n"
            f"Теперь, если Ваша анкета будет кому-то\n"
            f"интересна, то Бот спросит у Вас разрешение\n"
            f"на передачу Вашего контакта.",
            reply_markup=get_settings_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ У вас не установлен username!\n\n"
            "Чтобы использовать эту функцию:\n"
            "1. Зайдите в настройки Telegram\n"
            "2. Выберите 'Имя пользователя'\n"
            "3. Установите уникальное имя\n"
            "4. Вернитесь и попробуйте снова",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="settings_import_contact")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="contact_import_cancel")]
            ])
        )

@router.callback_query(F.data == "settings_import_first_name")
async def settings_import_first_name(callback: CallbackQuery):
    user = callback.from_user
    if user.first_name:
        # Сохраняем username в базу
        await db.update_first_name(user.id, user.first_name)

        await callback.message.edit_text(
            f"✅ Имя обновлено!\n\n"
            f"Ваше имя: {user.first_name}\n\n"
            f"Если захотите изменить имя:\n"
            f"1. Измените его в настройках профиля Telegram,\n"
            f"2. и снова передайте(импортируйте) его боту здесь, в этих настройках.",
            reply_markup=get_settings_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ У вас не установлено имя!\n\n"
            "Чтобы использовать эту функцию:\n"
            "1. Зайдите в 'Мой профиль' в Telegram\n"
            "2. Нажмите кнопку 'Изменить информацию'\n"
            "3. Введите желаемое имя\n"
            "4. Вернитесь и попробуйте снова импортировать это имя",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="settings_import_first_name")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="first_name_import_cancel")]
            ])
        )


@router.callback_query(F.data == "contact_import_cancel")
async def contact_import_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚙️ Настройки:",
        reply_markup=get_settings_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "first_name_import_cancel")
async def first_name_import_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚙️ Настройки:",
        reply_markup=get_settings_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "settings_back")
async def settings_back(callback: CallbackQuery):
    menu_title = "Главное меню"
    await callback.message.edit_text(
        text=f"_____{menu_title}_____",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "settings_city")
async def settings_city(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🏙️ Введите название вашего города:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="city_cancel")],
            [InlineKeyboardButton(text="✖️", callback_data="city_close")],
        ])
    )
    await state.set_state(SettingsState.waiting_for_city)


@router.message(SettingsState.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    seeker_id = message.from_user.id # await db.get_seeker_id(message.from_user.id)

    await db.update_preferences(seeker_id, city=city)
    await message.answer(f"✅ Город сохранен: {city}")
    await message.answer(
        "⚙️ Настройки:",
        reply_markup=get_settings_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "city_cancel")
async def city_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚙️ Настройки:",
        reply_markup=get_settings_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "city_close")
async def city_close(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()



@router.callback_query(F.data == "settings_city_only")
async def settings_city_only(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🌍 Искать собеседников только в вашем городе?",
        reply_markup=get_boolean_choice_keyboard()
    )
    await state.set_state(SettingsState.waiting_for_city_only)


@router.callback_query(SettingsState.waiting_for_city_only, F.data.startswith("boolean_"))
async def process_city_only(callback: CallbackQuery, state: FSMContext):
    if callback.data == "boolean_cancel":
        await callback.message.edit_text(
            "⚙️ Настройки:",
            reply_markup=get_settings_keyboard()
        )
        await state.clear()
        return

    is_city_only = callback.data == "boolean_yes"
    seeker_id = callback.from_user.id # await db.get_seeker_id(callback.from_user.id)

    await db.update_preferences(seeker_id, is_city_only=is_city_only)

    status = "включен" if is_city_only else "выключен"
    await callback.message.edit_text(f"✅ Поиск только в городе {status}")
    await callback.message.answer(
        "⚙️ Настройки:",
        reply_markup=get_settings_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "settings_photo_required")
async def settings_photo_required(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📸 Показывать только пользователей с фотографией?",
        reply_markup=get_boolean_choice_keyboard()
    )
    await state.set_state(SettingsState.waiting_for_photo_required)


@router.callback_query(SettingsState.waiting_for_photo_required, F.data.startswith("boolean_"))
async def process_photo_required(callback: CallbackQuery, state: FSMContext):
    if callback.data == "boolean_cancel":
        await callback.message.edit_text(
            "⚙️ Настройки:",
            reply_markup=get_settings_keyboard()
        )
        await state.clear()
        return

    photo_required = callback.data == "boolean_yes"
    seeker_id = callback.from_user.id # await db.get_seeker_id(callback.from_user.id)

    await db.update_preferences(seeker_id, photo_required=photo_required)

    status = "включен" if photo_required else "выключен"
    await callback.message.edit_text(f"✅ Показ только с фото {status}")
    await callback.message.answer(
        "⚙️ Настройки:",
        reply_markup=get_settings_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "settings_hide")
async def settings_hide(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "👁️ Скрыть ваш профиль из поиска? Вы не будете появляться у других пользователей.",
        reply_markup=get_boolean_choice_keyboard()
    )
    await state.set_state(SettingsState.waiting_for_hide)


@router.callback_query(SettingsState.waiting_for_hide, F.data.startswith("boolean_"))
async def process_hide(callback: CallbackQuery, state: FSMContext):
    if callback.data == "boolean_cancel":
        await callback.message.edit_text(
            "⚙️ Настройки:",
            reply_markup=get_settings_keyboard()
        )
        await state.clear()
        return

    is_seekable = not (callback.data == "boolean_yes")  # Инвертируем для is_seekable
    seeker_id = callback.from_user.id # await db.get_seeker_id(callback.from_user.id)

    await db.update_preferences(seeker_id, is_seekable=is_seekable)

    status = "скрыт" if not is_seekable else "виден"
    await callback.message.edit_text(f"✅ Профиль {status} в поиске")
    await callback.message.answer(
        "⚙️ Настройки:",
        reply_markup=get_settings_keyboard()
    )
    await state.clear()


# @router.callback_query(F.data == "settings_remove_outer_companion")
# async def settings_remove_companion(callback: CallbackQuery):
#     await db.remove_outer_companion(callback.from_user.id)
#     await callback.answer("✅ Собеседник удален")
#     await callback.message.edit_text(
#         "✅ Собеседник, которого Вы нашли, удален из Вашего профиля",
#         reply_markup=get_settings_keyboard()
#     )
#
# @router.callback_query(F.data == "settings_remove_income_companion")
# async def settings_remove_income_companion(callback: CallbackQuery):
#     await db.remove_income_companion(callback.from_user.id)
#     await callback.answer("✅ Собеседник удален")
#     await callback.message.edit_text(
#         "✅ Собеседник, который Вас нашел, удален из Вашего профиля",
#         reply_markup=get_settings_keyboard()
#     )
#
# @router.callback_query(F.data == "settings_back")
# async def settings_back(callback: CallbackQuery):
#     await callback.message.edit_text(
#         "Главное меню:",
#         reply_markup=get_main_menu_keyboard()
#     )

