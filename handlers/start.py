from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from database import db
from keyboards.main import get_language_keyboard, get_main_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await db.get_user(message.from_user.id)
    
    if not user:
        await db.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
        await message.answer(
            "Привет! Выберите язык / Hello! Choose your language:",
            reply_markup=get_language_keyboard()
        )
    else:
        await message.answer(
            "Добро пожаловать назад!",
            reply_markup=get_main_keyboard()
        )

@router.callback_query(F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery):
    language = callback.data.split("_")[1]
    await db.update_user_language(callback.from_user.id, language)
    
    if language == "ru":
        text = "Язык установлен! Теперь заполните анкету."
    else:
        text = "Language set! Now please fill out your profile."
    
    await callback.message.edit_text(text)
    await callback.message.answer(
        "Главное меню" if language == "ru" else "Main menu",
        reply_markup=get_main_keyboard()
    )
