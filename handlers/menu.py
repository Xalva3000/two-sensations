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


# @router.callback_query(F.data == "menu_companions")
# async def menu_companions(callback: CallbackQuery):
#     user = await db.get_user(callback.from_user.id)
#
#     # Проверяем, есть ли у пользователя собеседники
#     has_outer = user and user.get('outer_companion_telegram_id')
#     has_income = user and user.get('income_companion_telegram_id')
#
#     if not has_outer and not has_income:
#         await callback.answer("У вас пока нет собеседников")
#         return
#
#     text = "👥 Ваши собеседники:\n\n"
#
#     await callback.message.edit_text(
#         text,
#         reply_markup=get_companions_menu_keyboard()
#     )



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

# @router.callback_query(F.data == "menu_photo")
# async def menu_photo(callback: CallbackQuery):
#     await callback.message.answer("Отправьте ваше фото:")
#     # Здесь будет обработка фото


# @router.callback_query(F.data == "menu_search")
# async def menu_search(callback: CallbackQuery):
#     from handlers.matching import find_match
#     await find_match(callback.message)
