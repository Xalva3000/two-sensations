from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.main import (
    get_main_menu_keyboard,
    get_settings_keyboard,
)

# menu_router
router = Router()
# menu_view_profile -> profile.py
# menu_topics -> topics.py
# menu_search -> matching.py


@router.callback_query(F.data == "menu_settings")
async def menu_settings(callback: CallbackQuery):
    menu_title = "Настройки"
    await callback.message.edit_text(
        text=f"_____{menu_title}_____",
        reply_markup=get_settings_keyboard()
    )

@router.callback_query(F.data == "companions_back_to_main_menu")
async def companions_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data.startswith("menu_close"))
async def menu_close(callback: CallbackQuery):
    await callback.message.delete()
