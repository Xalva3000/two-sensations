from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InputMediaPhoto

from database import db
from keyboards.profile import get_profile_action_keyboard

router = Router()

@router.message(F.text == "🔍 Найти собеседника")
async def find_match(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user['is_profile_completed']:
        await message.answer("Сначала заполните анкету!")
        return
    
    match = await db.get_random_user(user['id'], [])
    
    if not match:
        await message.answer("Пока нет подходящих анкет. Попробуйте позже!")
        return
    
    caption = (
        f"👤 {match['first_name']} {match['last_name'] or ''}\n"
        f"🎂 Возраст: {match['age']}\n"
        f"👫 Пол: {'Мужской' if match['gender'] == 'male' else 'Женский'}\n"
        f"📝 Темы: {', '.join(match['topics'])}"
    )
    
    await message.answer_photo(
        match['photo'],
        caption=caption,
        reply_markup=get_profile_action_keyboard()
    )

@router.callback_query(F.data == "reject_profile")
async def reject_profile(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    # Здесь нужно получить ID отклоняемого пользователя из контекста
    # Для простоты предположим, что мы храним его где-то
    
    await callback.answer("Анкета отклонена")
    await callback.message.delete()
    # Показываем следующую анкету
    await find_match(callback.message)

@router.callback_query(F.data == "accept_profile")
async def accept_profile(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    # Здесь нужно получить контакт принятого пользователя
    
    await callback.answer("Контакт отправлен!")
    await callback.message.delete()
    await callback.message.answer(
        "Вот контакт пользователя: @username\n"
        "Свяжитесь с ним для общения!"
    )

