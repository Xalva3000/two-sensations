from aiogram import Router, F
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



# class ConfirmCompanionDeleteState(StatesGroup):
#     waiting_confirmation = State()

def get_companion_action_keyboard(companion_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👎", callback_data=f"decrease_balance_{companion_id}"),
            InlineKeyboardButton(text="⚠️ REPORT", callback_data=f"report_{companion_id}"),
            InlineKeyboardButton(text="👍", callback_data=f"increase_balance_{companion_id}"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_companions")
        ],
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


async def show_companion_profile(callback: CallbackQuery, companion, companion_type):
    topics_text = ", ".join([TOPICS_LIST[i - 1] for i in companion.get('topics', [])]) if companion.get(
        'topics') else "Не указаны"

    profile_text = (
        f"👤 Профиль собеседника:\n\n"
        f"📝 Имя: {companion['first_name']}\n"
        f"🎂 Возраст: {age_groups.get(companion['age'], 'Не указан')}\n"
        f"👫 Пол: {'Мужской' if companion['gender'] == 1 else 'Женский'}\n"
        f"🏙️ Город: {companion.get('city', 'Не указан')}\n"
        f"📚 Темы: {topics_text}\n"
    )

    if companion.get('about_me'):
        profile_text += f"\n📖 О себе:\n{companion['about_me']}\n"

    keyboard = get_companion_action_keyboard(companion['telegram_id'])

    if companion.get('photo_id'):
        await callback.message.answer_photo(
            companion['photo_id'],
            caption=profile_text,
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(profile_text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("report_"))
async def report_companion(callback: CallbackQuery):
    companion_id = int(callback.data.replace('report_', ''))
    # Логика репорта
    await callback.answer("Репорт отправлен")

@router.callback_query(F.data.startswith("decrease_balance_"))
async def decrease_companion_balance(callback: CallbackQuery):
    companion_id = int(callback.data.replace('decrease_balance_', ''))
    print(companion_id)
    db.decrease_balance(companion_id)
    await callback.answer("Очки собеседника тают!")

@router.callback_query(F.data.startswith("increase_balance_"))
async def increase_companion_balance(callback: CallbackQuery):
    companion_id = int(callback.data.replace('increase_balance_', ''))
    print(companion_id)
    db.increase_balance(companion_id)
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
        reply_markup=get_companions_menu_keyboard()
    )
    await state.clear()


@router.callback_query(ConfirmDeleteState.confirm_income_delete, F.data == "confirm_income_delete")
async def process_income_delete(callback: CallbackQuery, state: FSMContext):
    await db.remove_income_companion(callback.from_user.id)
    await callback.message.edit_text(
        "✅ Собеседник, который Вас нашел, удален из Вашего профиля",
        reply_markup=get_companions_menu_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚙️ Настройки:",
        reply_markup=get_companions_menu_keyboard()
    )
    await state.clear()