from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards.main import get_language_keyboard, get_gender_keyboard, get_age_keyboard, get_interested_age_keyboard, \
    get_main_menu_keyboard

router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_language = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_interested_age = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)

    if not user:
        await db.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name
        )
        await message.answer(
            "Привет! Выберите язык:",
            reply_markup=get_language_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_language)
    else:
        await message.answer(
            "Главное меню:",
            reply_markup=get_main_menu_keyboard()
        )


@router.callback_query(RegistrationStates.waiting_for_language, F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    language = int(callback.data.split("_")[1])
    await db.update_user_language(callback.from_user.id, language)

    text = "Язык установлен! Выберите ваш пол:" if language == 1 else "Language set! Choose your gender:"
    await callback.message.edit_text(text)
    await callback.message.answer(
        "Выберите пол:",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_gender)


@router.callback_query(RegistrationStates.waiting_for_gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = int(callback.data.split("_")[1])
    await db.update_user_gender(callback.from_user.id, gender)

    await callback.message.edit_text("Пол сохранен! Выберите ваш возраст:")
    await callback.message.answer(
        "Выберите возрастную категорию:",
        reply_markup=get_age_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_age)


@router.callback_query(RegistrationStates.waiting_for_age, F.data.startswith("age_"))
async def process_age(callback: CallbackQuery, state: FSMContext):
    age = int(callback.data.split("_")[1])
    await db.update_user_age(callback.from_user.id, age)

    await callback.message.edit_text("Возраст сохранен! Выберите интересующий возраст:")
    await callback.message.answer(
        "Выберите интересующую возрастную категорию:",
        reply_markup=get_interested_age_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_interested_age)


@router.callback_query(RegistrationStates.waiting_for_interested_age, F.data.startswith("iage_"))
async def process_interested_age(callback: CallbackQuery, state: FSMContext):
    interested_age = int(callback.data.split("_")[1])
    await db.update_user_interested_age(callback.from_user.id, interested_age)

    await callback.message.edit_text("Анкета заполнена! ✅")
    await callback.message.answer(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()