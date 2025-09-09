from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import config
from database import db
from keyboards.main import get_main_menu_keyboard

ADMIN_IDS = config.ADMINS

router = Router()


def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📷 Модерация фото", callback_data="admin_moderate_photos")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="Закрыть", callback_data="admin_close")]
    ])

def get_admin_close_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Закрыть", callback_data="admin_close")]
    ])


def get_photo_moderation_keyboard(seeker_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"photo_approve_{seeker_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"photo_reject_{seeker_id}")
        ],
        [InlineKeyboardButton(text="Закрыть", callback_data="admin_close")]
    ])


@router.message(F.text == "/admin")
async def admin_command(message: Message):
    """Команда для доступа к админ-панели"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ запрещен")
        return

    await message.answer(
        "👨‍💼 Админ-панель:\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Команда для доступа к админ-панели"""
    data = await db.count_not_confirmed_photo()
    await callback.message.answer(
        text=f"Не подтвержденные фото: {data.get('count', 0)}",
        reply_markup=get_admin_close_keyboard()
    )


@router.callback_query(F.data == "admin_moderate_photos")
async def moderate_photos(callback: CallbackQuery):
    """Показывает фото для модерации"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return

    unconfirmed_photos = await db.get_unconfirmed_photos()

    if not unconfirmed_photos:
        await callback.message.edit_text(
            "✅ Нет фото для модерации!\n\n"
            "Все фото проверены.",
            reply_markup=get_admin_keyboard()
        )
        return

    # Берем первое фото из списка
    photo_data = unconfirmed_photos[0]
    seeker_id = photo_data['seeker_id']

    caption = (
        f"👤 Пользователь: {photo_data['first_name']}\n"
        f"🆔 ID: {seeker_id}\n\n"
        f"Фото на модерации:"
    )

    try:
        await callback.message.answer_photo(
            photo_data['photo_id'],
            caption=caption,
            reply_markup=get_photo_moderation_keyboard(seeker_id)
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка загрузки фото:\n{str(e)}\n\n"
            f"👤 Пользователь: {photo_data['first_name']}\n"
            f"🆔 ID: {seeker_id}",
            reply_markup=get_photo_moderation_keyboard(seeker_id)
        )


@router.callback_query(F.data.startswith("photo_approve_"))
async def approve_photo(callback: CallbackQuery):
    """Подтверждает фото"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return

    seeker_id = int(callback.data.replace('photo_approve_', ''))

    # Подтверждаем фото в базе
    await db.confirm_photo(seeker_id)

    # Отправляем уведомление пользователю
    try:
        await callback.bot.send_message(
            seeker_id,
            "✅ Ваше фото подтверждено администратором!\n\n"
            "Теперь ваш профиль будет показываться в поиске."
        )
    except Exception as e:
        print(f"Не удалось уведомить пользователя {seeker_id}: {e}")

    # Показываем следующее фото для модерации
    await callback.answer("✅ Фото подтверждено")
    await moderate_photos(callback)


@router.callback_query(F.data.startswith("photo_reject_"))
async def reject_photo(callback: CallbackQuery):
    """Отклоняет фото"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен")
        return

    seeker_id = int(callback.data.replace('photo_reject_', ''))

    # Отклоняем фото в базе
    await db.reject_photo(seeker_id)

    # Отправляем уведомление пользователю
    try:
        await callback.bot.send_message(
            seeker_id,
            "❌ Ваше фото отклонено администратором.\n\n"
            "Причина: не соответствует требованиям.\n"
            "Пожалуйста, загрузите другое фото.\n\n"
            "Требования к фото:\n"
            "• Четкое и качественное\n"
            "• Лицо должно быть хорошо видно\n"
            "• Без посторонних людей\n"
            "• Без неприемлемого содержания"
        )
    except Exception as e:
        print(f"Не удалось уведомить пользователя {seeker_id}: {e}")

    # Показываем следующее фото для модерации
    await callback.answer("❌ Фото отклонено")
    await moderate_photos(callback)


# @router.callback_query(F.data == "moderation_back")
# async def moderation_back(callback: CallbackQuery):
#     """Возврат в админ-панель"""
#     if callback.from_user.id not in ADMIN_IDS:
#         await callback.answer("❌ Доступ запрещен")
#         return
#
#     await callback.message.answer(
#         "👨‍💼 Админ-панель:",
#         reply_markup=get_admin_keyboard()
#     )


# @router.callback_query(F.data == "admin_back")
# async def admin_back(callback: CallbackQuery):
#     """Возврат из админ-панели"""
#     await callback.message.edit_text(
#         "Главное меню:",
#         reply_markup=get_main_menu_keyboard()  # Нужно импортировать
#     )

@router.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass  # Игнорируем ошибки удаления