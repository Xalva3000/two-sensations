from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.main import get_main_menu_keyboard, get_settings_keyboard

router = Router()


@router.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "menu_restart")
async def menu_restart(callback: CallbackQuery, state: FSMContext):
    from handlers.start import RegistrationStates
    from keyboards.main import get_language_keyboard

    await callback.message.edit_text(
        "Выберите язык:",
        reply_markup=get_language_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_language)


@router.callback_query(F.data == "menu_settings")
async def menu_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "Настройки:",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(F.data == "settings_back")
async def settings_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )


# @router.callback_query(F.data == "menu_photo")
# async def menu_photo(callback: CallbackQuery):
#     await callback.message.answer("Отправьте ваше фото:")
#     # Здесь будет обработка фото


# @router.callback_query(F.data == "menu_search")
# async def menu_search(callback: CallbackQuery):
#     from handlers.matching import find_match
#     await find_match(callback.message)