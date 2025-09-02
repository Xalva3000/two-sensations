from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards.main import get_main_menu_keyboard, get_photo_keyboard

router = Router()


class PhotoState(StatesGroup):
    waiting_for_photo = State()


@router.callback_query(F.data == "menu_photo")
async def menu_photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📸 Отправьте ваше фото:",
        reply_markup=get_photo_keyboard(),
    )
    await state.set_state(PhotoState.waiting_for_photo)


@router.message(PhotoState.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    seeker_id = message.from_user.id # await db.get_seeker_id(message.from_user.id)

    await db.add_photo(seeker_id, photo_id)
    await message.answer("✅ Фото сохранено!")
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()


@router.callback_query(PhotoState.waiting_for_photo, F.data == "photo_cancel")
async def photo_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()
