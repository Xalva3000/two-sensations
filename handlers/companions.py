from aiogram import Router, F
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import db
from LEXICON import TOPICS_LIST
from LEXICON.numbers import age_groups
from keyboards.main import get_companions_slots_keyboard

router = Router()


def get_companion_close_keyboard():
     return InlineKeyboardMarkup(inline_keyboard=[
         [InlineKeyboardButton(text="Закрыть", callback_data="companion_close")],
     ])


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



def get_companion_action_keyboard(companion_id):
    """Клавиатура действий с companion"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖ Удалить", callback_data=f"remove_companion_{companion_id}"),
            InlineKeyboardButton(text="⚠️ Пожаловаться", callback_data=f"report_{companion_id}"),
        ],
        [InlineKeyboardButton(text="Закрыть", callback_data="companion_close")]
    ])


@router.callback_query(F.data =="menu_companions")
async def menu_companions(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Получаем слоты пользователя
    slots = await db.get_connections_by_slots(user_id)
    print(slots)
    # Формируем текст
    total_slots = len(slots)
    occupied_slots = sum(1 for slot in slots if not slot['is_empty'])

    text = (
        f"👥 Мои собеседники:\n\n"
        f"📊 Занято: {occupied_slots}/{total_slots} слотов\n\n"
        f"Выберите слот для управления:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_companions_slots_keyboard(slots)
    )


@router.callback_query(F.data.startswith("companion_close"))
async def companion_close(callback: CallbackQuery):
    await callback.message.delete()




async def show_companion_profile(callback: CallbackQuery, companion):
    topics_text = ", ".join([TOPICS_LIST[i - 1] for i in companion.get('topics', [])]) if companion.get(
        'topics') else "Не указаны"

    profile_text = (
        f"👤 Профиль собеседника:\n\n"
        f"📝 Имя: {companion['first_name']}\n"
        f"🎂 Возраст: {age_groups.get(companion['age'], 'Не указан')}\n"
        f"👫 Пол: {'Мужской' if companion['gender'] == 1 else 'Женский'}\n"
        f"🏙️ Город: {companion.get('city') or 'Не указан'}\n"
        f"📚 Темы: {topics_text}\n"
        f"🪢 Взаимность: {companion.get('is_mutual')}"
    )

    if companion.get('about'):
        profile_text += f"\n📖 О себе:\n{companion['about']}\n"

    # Получение клавиатуры удаление/репорт/закрыть
    reply_markup = get_companion_action_keyboard(companion['telegram_id'])

    if companion.get('photo_id'):
        await callback.message.answer_photo(
            companion['photo_id'],
            caption=profile_text,
            reply_markup=reply_markup
        )
    else:
        await callback.message.answer(
            profile_text,
            reply_markup=reply_markup
        )



def format_companion_profile(companion, companion_type):
    """Форматирует текст профиля собеседника"""

    is_mutual = False
    if companion_type == "outer":
        is_mutual = companion.get('outer_companion_mutual', False)
    else:
        is_mutual = companion.get('income_companion_mutual', False)

    # Добавляем статус взаимности в профиль
    mutual_status = "✅ Взаимная связь" if is_mutual else "⚪ Ожидает подтверждения"

    # Базовая информация
    text = (
        f"👤 Профиль собеседника:\n\n"
        f"📝 Имя: {companion.get('first_name', 'Не указано')}\n"
        f"🎂 Возраст: {age_groups.get(companion.get('age'), 'Не указан')}\n"
        f"👫 Пол: {get_gender_text(companion.get('gender'))}\n"
        f"🏙️ Город: {companion.get('city', 'Не указан')}\n"
        f"🔗 Статус: {mutual_status}\n"
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




@router.callback_query(F.data.startswith("remove_companion_"))
async def confirm_remove_companion(callback: CallbackQuery, state: FSMContext):
    companion_id = int(callback.data.replace("remove_companion_", ""))
    await state.update_data(companion_id=companion_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_companion_delete")],
        [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_companion_delete")]
    ])

    await callback.message.answer(
        "❓ Вы уверены, что хотите удалить собеседника?\n"
        "Это действие нельзя отменить.",
        reply_markup=keyboard
    )
    await state.set_state(ConfirmCompanionDeleteState.waiting_confirmation)

@router.callback_query(ConfirmCompanionDeleteState.waiting_confirmation, F.data == "confirm_companion_delete")
async def confirm_companion_delete(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления companion"""
    data = await state.get_data()
    seeker_id = callback.from_user.id
    companion_id = data.get('companion_id')

    # Удаляем companion в зависимости от типа
    await db.remove_connection(seeker_id, companion_id)
    success_message = "✅ Собеседник, которого вы нашли, удален"


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
    await state.clear()
    await callback.answer("❌ Удаление отменено")
    await callback.message.delete()



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


@router.callback_query(F.data.startswith("companion_slot_"))
async def handle_companion_slot(callback: CallbackQuery):
    """Обработчик нажатия на занятый слот"""
    companion_id = int(callback.data.replace('companion_slot_', ''))

    # Получаем информацию о собеседнике
    # """
    #     SELECT
    #         s.*, p.*,
    #         t.topics_mask
    #     FROM seekers s
    #         LEFT JOIN preferences p ON s.telegram_id = p.seeker_id
    #         LEFT JOIN topics t ON s.telegram_id = t.seeker_id
    #     WHERE s.telegram_id = $1
    # """
    companion = await db.get_companion_info(companion_id)
    if not companion:
        await callback.answer("❌ Собеседник не найден")
        return

    # Определяем тип связи
    # user_connections = await db.get_connections(callback.from_user.id)
    is_mutual = await db.is_mutual_connection(callback.from_user.id, companion.get('telegram_id'))
    companion['is_mutual'] = is_mutual
    # Показываем профиль с управлением
    await show_companion_profile(callback, companion)


@router.callback_query(F.data.startswith("empty_slot_"))
async def handle_empty_slot(callback: CallbackQuery):
    """Обработчик нажатия на пустой слот"""
    slot_number = int(callback.data.replace('empty_slot_', ''))

    await callback.answer(
        f"📭 Слот {slot_number} пустой\n"
        "Найдите нового собеседника через поиск!",
        show_alert=True
    )


@router.callback_query(F.data == "buy_slot")
async def buy_slot_handler(callback: CallbackQuery):
    """Обработчик покупки дополнительного слота"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    if not user:
        await callback.answer("❌ Пользователь не найден")
        return

    current_slots = user.get('companion_slots', 1)

    if current_slots >= 10:
        await callback.answer("✅ У вас максимальное количество слотов (10)")
        return

    # Стоимость покупки слота
    slot_cost = 200  # баллов
    new_slots_count = current_slots + 1

    if user.get('balance', 0) >= slot_cost:
        # Списание средств и увеличение слотов
        await db.deduct_balance(user_id, slot_cost)
        await db.upgrade_slots_amouunt(user_id, new_slots_count)

        await callback.answer(f"✅ Куплен дополнительный слот! Теперь слотов: {new_slots_count}")
        await menu_companions(callback)  # Обновляем меню
    else:
        await callback.answer(
            f"❌ Недостаточно баллов. Нужно: {slot_cost} баллов\n"
            f"Ваш баланс: {user.get('balance', 0)} баллов",
            show_alert=True
        )

