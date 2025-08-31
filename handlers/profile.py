from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards.profile import get_gender_keyboard, get_topics_keyboard
from keyboards.main import get_main_keyboard

router = Router()

class ProfileStates(StatesGroup):
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_photo = State()
    waiting_for_topics = State()

@router.message(F.text == "👤 Заполнить анкету")
@router.message(F.text == "✏️ Редактировать анкету")
async def start_profile(message: Message, state: FSMContext):
    await message.answer("Выберите ваш пол:", reply_markup=get_gender_keyboard())
    await state.set_state(ProfileStates.waiting_for_gender)

@router.message(ProfileStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    gender = "male" if "Мужской" in message.text else "female"
    await state.update_data(gender=gender)
    await message.answer("Введите ваш возраст:", reply_markup=None)
    await state.set_state(ProfileStates.waiting_for_age)

@router.message(ProfileStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 18 or age > 100:
            await message.answer("Пожалуйста, введите корректный возраст (18-100):")
            return
        await state.update_data(age=age)
        await message.answer("Отправьте ваше фото:")
        await state.set_state(ProfileStates.waiting_for_photo)
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@router.message(ProfileStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    
    data = await state.get_data()
    await message.answer(
        f"Отлично! Теперь выберите темы для обсуждения:",
        reply_markup=get_topics_keyboard()
    )
    await state.update_data(selected_topics=[])
    await state.set_state(ProfileStates.waiting_for_topics)

@router.callback_query(ProfileStates.waiting_for_topics, F.data.startswith("topic_"))
async def process_topic(callback: CallbackQuery, state: FSMContext):
    topic = callback.data.split("_", 1)[1]
    data = await state.get_data()
    selected_topics = data.get("selected_topics", [])
    
    if topic in selected_topics:
        selected_topics.remove(topic)
    else:
        selected_topics.append(topic)
    
    await state.update_data(selected_topics=selected_topics)
    await callback.answer(f"Тема {'добавлена' if topic in selected_topics else 'удалена'}")

@router.callback_query(ProfileStates.waiting_for_topics, F.data == "topics_done")
async def finish_profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_topics = data.get("selected_topics", [])
    
    if not selected_topics:
        await callback.answer("Выберите хотя бы одну тему!")
        return
    
    await db.update_user_profile(
        callback.from_user.id,
        data['gender'],
        data['age'],
        data['photo'],
        selected_topics
    )
    
    await callback.message.edit_text("Анкета заполнена! ✅")
    await callback.message.answer(
        "Главное меню",
        reply_markup=get_main_keyboard()
    )
    await state.clear()

