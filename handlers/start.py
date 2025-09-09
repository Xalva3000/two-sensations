from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from LEXICON import age_groups
from database import db
from keyboards.main import (
    get_gender_keyboard,
    get_age_keyboard,
    get_interested_age_keyboard,
    get_main_menu_keyboard,
    get_topics_keyboard,
)

router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_topics = State()  # Первым делом выбираем темы
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_interested_age = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)

    if not user:
        # Создаем нового пользователя
        await db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        # Автоматически сохраняем username если есть
        if message.from_user.username:
            await db.update_username(message.from_user.id, message.from_user.username)

        # Начинаем с ВЫБОРА ТЕМ (первый шаг)
        await message.answer(
            "👋 Добро пожаловать к Боту знакомств по общим ощущениям!\n\n"
            "Нажми на кнопки любимых ощущений, для настройки алгоритма поиска:\n"
            "(Готовность анкеты 1/4)",
            reply_markup=get_topics_keyboard(is_registration=True)
        )
        await state.set_state(RegistrationStates.waiting_for_topics)
    else:
        # Пользователь уже существует - показываем главное меню
        await message.answer(
            "Главное меню:",
            reply_markup=get_main_menu_keyboard()
        )


@router.callback_query(RegistrationStates.waiting_for_topics, F.data.startswith("topic_"))
async def process_topic_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора тем (первый шаг)"""
    topic_index = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected_topics = data.get("selected_topics", [])

    # Добавляем или удаляем тему
    if topic_index in selected_topics:
        selected_topics.remove(topic_index)
        action = "удалено"
    else:
        selected_topics.append(topic_index)
        action = "добавлено"

    await state.update_data(selected_topics=selected_topics)

    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(
        reply_markup=get_topics_keyboard(selected_topics, is_registration=True)
    )
    await callback.answer(f"Ощущение {action}")


@router.callback_query(RegistrationStates.waiting_for_topics, F.data == "topics_save")
async def save_topics_and_continue(callback: CallbackQuery, state: FSMContext):
    """Сохраняем темы и переходим к выбору пола"""
    data = await state.get_data()
    selected_topics = data.get("selected_topics", [])

    if not selected_topics:
        await callback.answer("❌ Выберите хотя бы одно ощущение!")
        return

    # Сохраняем темы во временный state
    await state.update_data(selected_topics=selected_topics)

    # Переходим к выбору пола
    await callback.message.edit_text("✅ Ощущения сохранены! Теперь укажите ваш пол:\n(Готовность анкеты 2/4)")
    await callback.message.answer(
        "Выберите пол:",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_gender)


@router.callback_query(RegistrationStates.waiting_for_topics, F.data == "topics_clear")
async def clear_topics(callback: CallbackQuery, state: FSMContext):
    """Очистка выбранных тем"""
    await state.update_data(selected_topics=[])
    await callback.message.edit_reply_markup(
        reply_markup=get_topics_keyboard([])
    )
    await callback.answer("Выбор сброшен")


@router.callback_query(RegistrationStates.waiting_for_gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Второй шаг - выбор пола"""
    gender = int(callback.data.split("_")[1])
    await db.update_user_gender(callback.from_user.id, gender)
    await state.update_data(gender=gender)
    await callback.message.edit_text("✅ Пол сохранен! Теперь укажите ваш возраст:\n(Готовность анкеты 3/4)")
    await callback.message.answer(
        "Выберите возрастную категорию:",
        reply_markup=get_age_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_age)


@router.callback_query(RegistrationStates.waiting_for_age, F.data.startswith("age_"))
async def process_age(callback: CallbackQuery, state: FSMContext):
    """Третий шаг - выбор возраста"""
    age = int(callback.data.split("_")[1])
    await state.update_data(age=age)
    await db.update_user_age(callback.from_user.id, age)

    await callback.message.edit_text("✅ Возраст сохранен! Теперь укажите, кого ищете:\n(Готовность анкеты 4/4)")
    await callback.message.answer(
        "Выберите интересующую возрастную категорию:",
        reply_markup=get_interested_age_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_interested_age)


@router.callback_query(RegistrationStates.waiting_for_interested_age, F.data.startswith("iage_"))
async def process_interested_age(callback: CallbackQuery, state: FSMContext):
    """Четвертый шаг - выбор интересующего возраста и завершение регистрации"""
    interested_age = int(callback.data.split("_")[1])
    await db.update_user_interested_age(callback.from_user.id, interested_age)

    # Получаем сохраненные темы из state и сохраняем в базу
    data = await state.get_data()
    age = data.get("age", 0)
    gender = data.get("gender", 0)
    selected_topics = data.get("selected_topics", [])

    print(data)
    if selected_topics:
        await db.set_user_topics(callback.from_user.id, selected_topics)

    # Завершаем регистрацию
    await callback.message.edit_text(
        "🎉 Регистрация завершена! ✅\n\n"
        f"• Выбрано ощущений: {len(selected_topics)}\n"
        f"• Пол: {'Мужской' if gender == 1 else 'Женский'}\n"
        f"• Возраст: {age_groups.get(age, 'Не указан')}\n"
        f"• Ищу: {age_groups.get(interested_age, 'Любой возраст')}\n\n"
        "Теперь вы можете начать поиск собеседников!"
    )
    await callback.message.answer(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()
