from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.main import get_topics_keyboard, get_topics_menu_keyboard, get_main_menu_keyboard
from aiogram.fsm.state import State, StatesGroup

router = Router()


class TopicsState(StatesGroup):
    editing_topics = State()


@router.callback_query(F.data == "menu_topics")
async def menu_topics(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎭 Управление темами для общения:\n\n"
        "Выберите темы, которые вам интересны. Это поможет найти подходящего собеседника.",
        reply_markup=get_topics_menu_keyboard()
    )


@router.callback_query(F.data == "topics_back_to_main")
async def topics_back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "topics_edit")
async def topics_edit(callback: CallbackQuery, state: FSMContext):
    # Получаем текущие выбранные темы пользователя
    seeker_id = callback.from_user.id #  await db.get_seeker_id(callback.from_user.id)
    selected_topics = await db.get_user_topics(seeker_id)

    await callback.message.edit_text(
        "Выберите интересующие темы (можно выбрать несколько):\n"
        "✅ - тема выбрана\n"
        "Нажмите на тему, чтобы выбрать/отменить выбор\n\n"
        f"Выбрано тем: {len(selected_topics)}/20",
        reply_markup=get_topics_keyboard(selected_topics)
    )
    await state.set_state(TopicsState.editing_topics)
    await state.update_data(selected_topics=selected_topics)


@router.callback_query(TopicsState.editing_topics, F.data.startswith("topic_"))
async def process_topic_selection(callback: CallbackQuery, state: FSMContext):
    topic_number = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected_topics = data.get("selected_topics", [])

    # Добавляем или удаляем тему
    if topic_number in selected_topics:
        selected_topics.remove(topic_number)
        action = "удалена"
    else:
        selected_topics.append(topic_number)
        action = "добавлена"

    await state.update_data(selected_topics=selected_topics)

    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(
        reply_markup=get_topics_keyboard(selected_topics)
    )
    await callback.answer(f"Тема {action}")


@router.callback_query(TopicsState.editing_topics, F.data == "topics_save")
async def topics_save(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_topics = data.get("selected_topics", [])
    seeker_id = callback.from_user.id  # await db.get_seeker_id(callback.from_user.id)

    # Сохраняем все темы в базу
    for topic_num in range(1, 21):
        value = topic_num in selected_topics
        await db.update_topic(seeker_id, topic_num, value)

    await callback.message.edit_text(
        f"✅ Темы сохранены! Выбрано тем: {len(selected_topics)}\n"
        "Теперь мы сможем лучше подбирать собеседников по вашим интересам.",
        reply_markup=get_topics_menu_keyboard()
    )
    await state.clear()
    await callback.answer("Темы сохранены!")


@router.callback_query(TopicsState.editing_topics, F.data == "topics_back")
async def topics_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎭 Управление темами для общения:",
        reply_markup=get_topics_menu_keyboard()
    )
    await state.clear()