from aiogram import Router, F
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import db
from LEXICON import TOPICS_LIST
from LEXICON.numbers import age_groups
from keyboards.main import get_companions_menu_keyboard, get_settings_keyboard

router = Router()

class ConfirmDeleteState(StatesGroup):
    confirm_outer_delete = State()
    confirm_income_delete = State()

class ConfirmCompanionDeleteState(StatesGroup):
    waiting_confirmation = State()

class IsReportUser(BaseFilter):
    """Фильтр сообщений от нажатия кнопки в которых содержатся исключительно цифры."""

    async def __call__(self, callback: CallbackQuery) -> bool:
        if "report" in callback.data:
            second_part = callback.data.split("_")[1]
            if second_part.isdigit():
                return True
        return False

class IsReportReason(BaseFilter):
    """Фильтр сообщений от нажатия кнопки в которых содержатся исключительно цифры."""

    async def __call__(self, callback: CallbackQuery) -> bool:
        if callback.data in ("report_spam", "report_content", "report_scam", "report_other", "report_cancel"):
            return True
        return False


def get_gender_text(gender_code):
    """Возвращает текстовое представление пола"""
    if gender_code == 1:
        return "Мужской"
    elif gender_code == 2:
        return "Женский"
    else:
        return "Не указан"

def get_companion_close_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Закрыть", callback_data="back_to_companions")],
    ])

# class ConfirmCompanionDeleteState(StatesGroup):
#     waiting_confirmation = State()

# def get_companion_action_keyboard(companion_id):
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(text="👎", callback_data=f"decrease_balance_{companion_id}"),
#             InlineKeyboardButton(text="⚠️ REPORT", callback_data=f"report_{companion_id}"),
#             InlineKeyboardButton(text="👍", callback_data=f"increase_balance_{companion_id}"),
#         ],
#         [
#             InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_companions")
#         ],
#     ])

# def get_companion_action_keyboard(companion_id, companion_type):
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(text="➖ Удалить", callback_data=f"remove_{companion_type}_{companion_id}"),
#             InlineKeyboardButton(text="⚠️ REPORT", callback_data=f"report_{companion_id}")
#         ],
#         [InlineKeyboardButton(text="➕ Написать", callback_data=f"message_{companion_id}")],
#         [InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="back_to_companions")]
#     ])

def get_companion_action_keyboard(companion_id, companion_type):
    """Клавиатура действий с companion"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖ Удалить", callback_data=f"remove_{companion_type}_{companion_id}"),
            InlineKeyboardButton(text="⚠️ Пожаловаться", callback_data=f"report_{companion_id}")
        ],
        [InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="back_to_companions")]
    ])

@router.callback_query(F.data == "menu_view_outer_companion")
async def view_outer_companion(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user or not user.get('outer_companion_telegram_id'):
        await callback.answer("У вас нет собеседника, которого вы нашли")
        return

    companion = await db.get_companion_info(user['outer_companion_telegram_id'])
    if not companion:
        await callback.answer("Собеседник не найден")
        return

    await show_companion_profile(callback, companion, "outer")


@router.callback_query(F.data == "menu_view_income_companion")
async def view_income_companion(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user or not user.get('income_companion_telegram_id'):
        await callback.answer("У вас нет собеседника, который вас нашел")
        return

    companion = await db.get_companion_info(user['income_companion_telegram_id'])
    if not companion:
        await callback.answer("Собеседник не найден")
        return

    await show_companion_profile(callback, companion, "income")


# async def show_companion_profile(callback: CallbackQuery, companion, companion_type):
#     topics_text = ", ".join([TOPICS_LIST[i - 1] for i in companion.get('topics', [])]) if companion.get(
#         'topics') else "Не указаны"
#
#     profile_text = (
#         f"👤 Профиль собеседника:\n\n"
#         f"📝 Имя: {companion['first_name']}\n"
#         f"🎂 Возраст: {age_groups.get(companion['age'], 'Не указан')}\n"
#         f"👫 Пол: {'Мужской' if companion['gender'] == 1 else 'Женский'}\n"
#         f"🏙️ Город: {companion.get('city', 'Не указан')}\n"
#         f"📚 Темы: {topics_text}\n"
#     )
#
#     if companion.get('about'):
#         profile_text += f"\n📖 О себе:\n{companion['about']}\n"
#
#     keyboard = get_companion_action_keyboard(companion['telegram_id'])
#
#     if companion.get('photo_id'):
#         await callback.message.answer_photo(
#             companion['photo_id'],
#             caption=profile_text,
#             reply_markup=keyboard
#         )
#     else:
#         await callback.message.answer(profile_text, reply_markup=keyboard)

async def show_companion_profile(callback: CallbackQuery, companion, companion_type):
    try:
        # Проверяем валидность данных
        if not companion:
            await callback.answer("❌ Профиль собеседника не найден")
            return

        # Форматируем текст профиля
        profile_text = format_companion_profile(companion)

        # Получаем клавиатуру
        keyboard = get_companion_action_keyboard(companion['telegram_id'], companion_type)

        # Отправляем сообщение
        await send_companion_message(callback, companion, profile_text, keyboard)

    except Exception as e:
        print(f"Ошибка показа профиля companion: {e}")
        await callback.answer("❌ Ошибка загрузки профиля")


def format_companion_profile(companion):
    """Форматирует текст профиля собеседника"""
    # Базовая информация
    text = (
        f"👤 Профиль собеседника:\n\n"
        f"📝 Имя: {companion.get('first_name', 'Не указано')}\n"
        f"🎂 Возраст: {age_groups.get(companion.get('age'), 'Не указан')}\n"
        f"👫 Пол: {get_gender_text(companion.get('gender'))}\n"
        f"🏙️ Город: {companion.get('city', 'Не указан')}\n"
    )

    # Темы
    topics = companion.get('topics', [])
    if topics:
        valid_topics = [i for i in topics if 1 <= i <= len(TOPICS_LIST)]
        if valid_topics:
            topics_names = [TOPICS_LIST[i - 1] for i in valid_topics[:6]]
            text += f"📚 Темы: {', '.join(topics_names)}"
            if len(valid_topics) > 6:
                text += f" (+{len(valid_topics) - 6})"
            text += "\n"

    # О себе
    if companion.get('about'):
        about_me = companion['about']
        if len(about_me) > 200:
            about_me = about_me[:200] + "..."
        text += f"\n📖 О себе:\n{about_me}\n"

    return text




async def send_companion_message(callback, companion, profile_text, keyboard):
    """Отправляет сообщение с профилем собеседника"""
    photo_id = companion.get('photo_id')
    is_photo_confirmed = companion.get('is_photo_confirmed', False)

    # Проверяем можно ли отправить фото
    can_send_photo = photo_id and is_photo_confirmed

    if can_send_photo:
        try:
            await callback.message.answer_photo(
                photo_id,
                caption=profile_text,
                reply_markup=keyboard
            )
            return
        except Exception as e:
            print(f"Не удалось отправить фото companion: {e}")
            # Продолжаем с текстовым сообщением

    # Текстовое сообщение (fallback)
    await callback.message.answer(
        profile_text,
        reply_markup=keyboard
    )

# @router.callback_query(F.data.startswith("report_"))
# async def report_companion(callback: CallbackQuery):
#     companion_id = int(callback.data.replace('report_', ''))
#     # Логика репорта
#     await callback.answer("Репорт отправлен")

@router.callback_query(F.data.startswith("decrease_balance_"))
async def decrease_companion_balance(callback: CallbackQuery):
    # получение id собеседника из клавиатуры
    companion_id = int(callback.data.replace('decrease_balance_', ''))
    # отправка и сообщение
    await db.decrease_balance(companion_id)
    await callback.answer("Очки собеседника тают!")

@router.callback_query(F.data.startswith("increase_balance_"))
async def increase_companion_balance(callback: CallbackQuery):
    # получение id собеседника из клавиатуры
    companion_id = int(callback.data.replace('increase_balance_', ''))
    # отправка и сообщение
    await db.increase_balance(companion_id)
    await callback.answer("Очки собеседника взлетают!")

# @router.callback_query(F.data.startswith("message_"))
# async def message_companion(callback: CallbackQuery):
#     companion_id = int(callback.data.replace('message_', ''))
#     companion = await db.get_user(companion_id)
#     if companion and companion.get('username'):
#         await callback.answer(f"Напишите @{companion['username']}")
#     else:
#         await callback.answer("Username не доступен")


@router.callback_query(F.data == "back_to_companions")
async def back_to_companions(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass  # Игнорируем ошибки удаления

    # await callback.message.answer(
    #     "👥 Ваши собеседники:",
    #     reply_markup=get_companions_menu_keyboard()
    # )


@router.callback_query(F.data == "settings_remove_outer_companion")
async def confirm_remove_outer_companion(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_outer_delete")],
        [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete")]
    ])

    await callback.message.edit_text(
        "❓ Вы уверены, что хотите удалить собеседника, которого вы нашли?\n"
        "Это действие нельзя отменить.",
        reply_markup=keyboard
    )
    await state.set_state(ConfirmDeleteState.confirm_outer_delete)


@router.callback_query(F.data == "settings_remove_income_companion")
async def confirm_remove_income_companion(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_income_delete")],
        [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete")]
    ])

    await callback.message.edit_text(
        "❓ Вы уверены, что хотите удалить собеседника, который вас нашел?\n"
        "Это действие нельзя отменить.",
        reply_markup=keyboard
    )
    await state.set_state(ConfirmDeleteState.confirm_income_delete)


@router.callback_query(ConfirmDeleteState.confirm_outer_delete, F.data == "confirm_outer_delete")
async def process_outer_delete(callback: CallbackQuery, state: FSMContext):
    await db.remove_outer_companion(callback.from_user.id)
    await callback.message.edit_text(
        "✅ Собеседник, которого Вы нашли, удален из Вашего профиля",
        reply_markup=get_companion_close_keyboard()
    )
    await state.clear()


@router.callback_query(ConfirmDeleteState.confirm_income_delete, F.data == "confirm_income_delete")
async def process_income_delete(callback: CallbackQuery, state: FSMContext):
    await db.remove_income_companion(callback.from_user.id)
    await callback.message.edit_text(
        "✅ Собеседник, который Вас нашел, удален из Вашего профиля",
        reply_markup=get_companion_close_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚙️ Настройки:",
        reply_markup=get_companions_menu_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("remove_"))
async def remove_companion_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки удаления companion"""
    data_parts = callback.data.split('_')
    if len(data_parts) < 3:
        await callback.answer("❌ Ошибка запроса")
        return

    companion_type = data_parts[1]
    companion_id = int(data_parts[2])

    # Сохраняем данные в state для подтверждения
    await state.update_data(
        companion_type=companion_type,
        companion_id=companion_id
    )

    # Текст в зависимости от типа companion
    if companion_type == "outer":
        companion_text = "которого вы нашли"
    else:  # income
        companion_text = "который вас нашел"

    # Клавиатура подтверждения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_companion_delete")],
        [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_companion_delete")]
    ])

    await callback.message.answer(
        f"❓ Вы уверены, что хотите удалить собеседника {companion_text}?\n\n"
        "Это действие нельзя отменить. Вы потеряете контакт с этим пользователем.",
        reply_markup=keyboard
    )
    await state.set_state(ConfirmCompanionDeleteState.waiting_confirmation)


@router.callback_query(ConfirmCompanionDeleteState.waiting_confirmation, F.data == "confirm_companion_delete")
async def confirm_companion_delete(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления companion"""
    data = await state.get_data()
    companion_type = data.get('companion_type')
    companion_id = data.get('companion_id')

    if not companion_type or not companion_id:
        await callback.answer("❌ Ошибка данных")
        return

    # Удаляем companion в зависимости от типа
    if companion_type == "outer":
        await db.remove_outer_companion(callback.from_user.id)
        success_message = "✅ Собеседник, которого вы нашли, удален"
    else:  # income
        await db.remove_income_companion(callback.from_user.id)
        success_message = "✅ Собеседник, который вас нашел, удален"

    # Уведомляем пользователя
    await callback.message.edit_text(
        f"{success_message}\n\n"
        "Контакт удален из вашего профиля.",
        reply_markup=get_companion_close_keyboard()
    )
    await state.clear()


@router.callback_query(ConfirmCompanionDeleteState.waiting_confirmation, F.data == "cancel_companion_delete")
async def cancel_companion_delete(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления companion"""
    data = await state.get_data()
    companion_id = data.get('companion_id')
    companion_type = data.get('companion_type')

    # Возвращаемся к просмотру профиля companion
    companion = await db.get_companion_info(companion_id)
    if companion:
        await show_companion_profile(callback, companion, companion_type)
    else:
        await callback.message.edit_text(
            "👥 Ваши собеседники:",
            reply_markup=get_companion_close_keyboard()
        )

    await state.clear()
    await callback.answer("❌ Удаление отменено")



@router.callback_query(F.data.startswith("back_to_profile_"))
async def back_to_profile_handler(callback: CallbackQuery):
    """Возврат к профилю companion"""
    companion_id = int(callback.data.replace('back_to_profile_', ''))
    companion = await db.get_companion_info(companion_id)

    if companion:
        # Определяем тип companion
        user = await db.get_user(callback.from_user.id)
        companion_type = "outer" if user and user.get('outer_companion_telegram_id') == companion_id else "income"

        await show_companion_profile(callback, companion, companion_type)
    else:
        await callback.answer("❌ Профиль не найден")
        await callback.message.edit_text(
            "👥 Ваши собеседники:",
            reply_markup=get_companions_menu_keyboard()
        )


@router.callback_query(IsReportUser())
async def report_companion_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки жалобы"""
    companion_id = int(callback.data.replace('report_', ''))

    await state.update_data(reported_companion_id=companion_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Спам", callback_data="report_spam")],
        [InlineKeyboardButton(text="📵 Неприемлемый контент", callback_data="report_content")],
        [InlineKeyboardButton(text="👤 Мошенничество", callback_data="report_scam")],
        [InlineKeyboardButton(text="❌ Другое", callback_data="report_other")],
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data="report_cancel")]
    ])

    await callback.message.answer(
        "⚠️ Пожаловаться на пользователя\n\n"
        "Выберите причину жалобы:",
        reply_markup=keyboard
    )


@router.callback_query(IsReportReason())
async def process_report_reason(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора причины жалобы"""
    report_reason = callback.data

    reasons = {
        "report_spam": "🚫 Спам",
        "report_content": "📵 Неприемлемый контент",
        "report_scam": "👤 Мошенничество",
        "report_other": "❌ Другое"
    }

    if report_reason in reasons:
        data = await state.get_data()
        companion_id = data.get('reported_companion_id')

        # Здесь можно сохранить жалобу в базу
        # await db.save_report(callback.from_user.id, companion_id, reasons[report_reason])

        await callback.message.edit_text(
            f"✅ Жалоба отправлена: {reasons[report_reason]}\n\n"
            "Администрация рассмотрит вашу жалобу в ближайшее время.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Закрыть", callback_data=f"companions_cancel")]
            ])
        )
        await state.clear()

    elif report_reason == "report_cancel":
        await callback.message.delete()


@router.callback_query(F.data.startswith("companions_cancel"))
async def companions_cancel(callback: CallbackQuery):

    await callback.message.delete()
