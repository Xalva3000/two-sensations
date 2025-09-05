from aiogram import Router, F
from aiogram.types import CallbackQuery

from LEXICON.numbers import age_groups
from database import db
from keyboards.connection_keyboards import get_connection_response_keyboard, get_connection_request_keyboard

router = Router()


@router.callback_query(F.data.startswith("accept_outer_profile_"))
async def accept_outer_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    # получение id принятого собеседника
    new_companion_id = int(callback.data.replace('accept_outer_profile_', ''))

    # Создаем запрос на соединение
    await db.create_connection_request(user_id, new_companion_id)

    # Получаем информацию о пользователях
    user_info = await db.get_user(user_id)
    companion_info = await db.get_user(new_companion_id)

    # Отправляем запрос собеседнику
    try:
        await callback.bot.send_message(
            chat_id=new_companion_id,
            text=f"👋 Запрос на соединение!\n\n"
                 f"Пользователь {user_info['first_name']} хочет связаться с вами.\n"
                 f"🎂 Возраст: {age_groups.get(user_info['age'], 'Не указан')}\n"
                 f"👫 Пол: {'Мужской' if user_info['gender'] == 1 else 'Женский'}\n\n"
                 f"Разрешить передачу контакта?",
            reply_markup=get_connection_request_keyboard(user_id)
        )
    except Exception as e:
        print(f"Ошибка отправки запроса: {e}")
        await callback.answer("Не удалось отправить запрос")
        return

    # Уведомляем инициатора
    await callback.answer("✅ Запрос отправлен!")
    await callback.message.edit_text(
        "⏳ Запрос на соединение отправлен!\n\n"
        "Ждем ответа от пользователя. Вы получите уведомление, "
        "когда он примет решение.",
        reply_markup=get_connection_response_keyboard(new_companion_id, False)
    )


@router.callback_query(F.data.startswith("accept_request_"))
async def accept_connection_request(callback: CallbackQuery):
    from_user_id = int(callback.data.replace('accept_request_', ''))
    to_user_id = callback.from_user.id

    # Обновляем статус запроса
    await db.update_connection_request(from_user_id, to_user_id, 'accepted')

    # Устанавливаем соединение
    await db.set_outer_companion(from_user_id, to_user_id)
    await db.set_income_companion(to_user_id, from_user_id)

    # Получаем информацию о пользователях
    from_user_info = await db.get_user(from_user_id)
    to_user_info = await db.get_user(to_user_id)

    # Отправляем подтверждение инициатору
    try:
        from_username = await db.get_user_username(from_user_id) or "пользователь"
        to_username = await db.get_user_username(to_user_id) or "пользователь"

        await callback.bot.send_message(
            chat_id=from_user_id,
            text=f"🎉 Ваш запрос принят!\n\n"
                 f"Пользователь {to_user_info['first_name']} принял ваш запрос на соединение.\n\n"
                 f"💌 Напишите ему: @{to_username if to_username != 'пользователь' else 'username_not_set'}\n\n"
                 f"Приятного общения!",
            reply_markup=get_connection_response_keyboard(to_user_id, True)
        )
    except Exception as e:
        print(f"Ошибка отправки подтверждения: {e}")

    # Уведомляем получателя
    await callback.message.edit_text(
        f"✅ Вы приняли запрос от {from_user_info['first_name']}!\n\n"
        f"💌 Напишите ему: @{from_username if from_username != 'пользователь' else 'username_not_set'}\n\n"
        f"Приятного общения!",
        reply_markup=get_connection_response_keyboard(from_user_id, True)
    )


@router.callback_query(F.data.startswith("reject_request_"))
async def reject_connection_request(callback: CallbackQuery):
    from_user_id = int(callback.data.replace('reject_request_', ''))
    to_user_id = callback.from_user.id

    # Обновляем статус запроса
    await db.update_connection_request(from_user_id, to_user_id, 'rejected')

    # Получаем информацию о пользователе
    to_user_info = await db.get_user(to_user_id)

    # Уведомляем инициатора об отказе
    try:
        await callback.bot.send_message(
            chat_id=from_user_id,
            text=f"❌ Запрос отклонен\n\n"
                 f"Пользователь {to_user_info['first_name']} отклонил ваш запрос на соединение.",
            reply_markup=get_connection_response_keyboard(to_user_id, False)
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления об отказе: {e}")

    # Уведомляем получателя
    await callback.message.edit_text(
        f"❌ Вы отклонили запрос от пользователя",
        reply_markup=get_connection_response_keyboard(from_user_id, False)
    )


@router.callback_query(F.data.startswith("accept_outer_profile_"))
async def accept_outer_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    new_companion_id = int(callback.data.replace('accept_outer_profile_', ''))

    # Проверяем, не отправляли ли уже запрос
    existing_request = await db.get_connection_request(user_id, new_companion_id)
    if existing_request and existing_request['status'] == 'pending':
        await callback.answer("⏳ Запрос уже отправлен, ждем ответа")
        return

    if existing_request and existing_request['status'] == 'accepted':
        await callback.answer("✅ Соединение уже установлено")
        return

    if existing_request and existing_request['status'] == 'rejected':
        await callback.answer("❌ Запрос был отклонен ранее")
        return

@router.callback_query(F.data == "connection_cancel")
async def back_to_companions(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass  # Игнорируем ошибки удаления
