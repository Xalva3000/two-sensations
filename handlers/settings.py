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


@router.callback_query(F.data == "settings_restart_profile")
async def settings_restart_profile(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите пол:",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_gender)


@router.callback_query(F.data == "settings_import_contact")
async def settings_import_contact(callback: CallbackQuery, state: FSMContext):
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

@router.callback_query(F.data == "contact_import_cancel")
async def contact_import_cancel(callback: CallbackQuery, state: FSMContext):
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
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="city_cancel")]
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

