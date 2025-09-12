from aiogram import Router, F
from aiogram.types import CallbackQuery

from LEXICON.numbers import age_groups
from database import db
from keyboards.connection_keyboards import get_connection_response_keyboard, get_connection_request_keyboard

router = Router()


@router.callback_query(F.data.startswith("accept_outer_profile_"))
async def accept_outer_profile(callback: CallbackQuery):
    """Положительная реакция на запрос контакта"""
    user_id = callback.from_user.id
    # получение id принятого собеседника
    new_companion_id = int(callback.data.replace('accept_outer_profile_', ''))

    try:
        # Получаем информацию о пользователях
        user_info = await db.get_user(user_id)
        companion_info = await db.get_user(new_companion_id)
        await db.add_connection(user_id, new_companion_id)

    except Exception as adding_connection_error:
        print(f"Ошибка во время создания записи о связи:\n {adding_connection_error}")
        await callback.answer("Не удалось создать связь.")
        return
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
    await callback.message.answer(
        "⏳ Запрос на соединение отправлен!\n\n"
        "Ждем ответа от пользователя. Вы получите уведомление, "
        "когда он примет решение.",
        reply_markup=get_connection_response_keyboard()
    )


@router.callback_query(F.data.startswith("accept_request_"))
async def accept_connection_request(callback: CallbackQuery):
    from_user_id = int(callback.data.replace('accept_request_', ''))
    to_user_id = callback.from_user.id

    # Устанавливаем соединение
    await db.add_connection(to_user_id, from_user_id)

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
            reply_markup=get_connection_response_keyboard()
        )
    except Exception as e:
        print(f"Ошибка отправки подтверждения: {e}")

    # Уведомляем получателя
    await callback.message.edit_text(
        f"✅ Вы приняли запрос от {from_user_info['first_name']}!\n\n"
        f"💌 Напишите ему: @{from_username if from_username != 'пользователь' else 'username_not_set'}\n\n"
        f"Приятного общения!",
        reply_markup=get_connection_response_keyboard()
    )


@router.callback_query(F.data.startswith("reject_request_"))
async def reject_connection_request(callback: CallbackQuery):
    companion_id = int(callback.data.replace('reject_request_', ''))
    user_id = callback.from_user.id

    # проставляем связи статус отклонено
    await db.reject_connection(user_id, companion_id)
    # Получаем информацию о пользователе
    to_user_info = await db.get_user(companion_id)

    # Уведомляем инициатора об отказе
    try:
        await callback.bot.send_message(
            chat_id=companion_id,
            text=f"❌ Запрос отклонен\n\n"
                 f"Пользователь {to_user_info['first_name']} отклонил ваш запрос на соединение.",
            reply_markup=get_connection_response_keyboard()
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления об отказе: {e}")

    # Уведомляем получателя
    await callback.message.edit_text(
        f"❌ Вы отклонили запрос от пользователя",
        reply_markup=get_connection_response_keyboard()
    )


# @router.callback_query(F.data.startswith("remove_companion_"))
# async def remove_companion(callback: CallbackQuery, state: FSMContext):
#     data_parts = callback.data.split('_')
#     companion_id = int(data_parts[2])
#     user_id = callback.from_user.id
#
#     # Удаляем companion
#     await db.remove_connection(user_id, companion_id)
#
#     # Уведомляем companion о разрыве связи
#     try:
#         companion_user = await db.get_user(companion_id)
#         if companion_user:
#             await callback.bot.send_message(
#                 companion_id,
#                 f"❌ {callback.from_user.first_name} очищен из контактов по его инициативе.\n\n"
#                 f"Вы можете искать нового собеседника."
#             )
#     except Exception as e:
#         print(f"Ошибка уведомления companion: {e}")
#
#     await callback.answer("✅ Собеседник удален")
#     await callback.message.edit_text(
#         "✅ Собеседник удален из вашего профиля",
#         reply_markup=get_settings_keyboard()
#     )

# @router.callback_query(F.data.startswith("accept_outer_profile_"))
# async def accept_outer_profile(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     new_companion_id = int(callback.data.replace('accept_outer_profile_', ''))
#
#     # Проверяем, не отправляли ли уже запрос
#     existing_request = await db.get_connection_request(user_id, new_companion_id)
#     if existing_request and existing_request['status'] == 'pending':
#         await callback.answer("⏳ Запрос уже отправлен, ждем ответа")
#         return
#
#     if existing_request and existing_request['status'] == 'accepted':
#         await callback.answer("✅ Соединение уже установлено")
#         return
#
#     if existing_request and existing_request['status'] == 'rejected':
#         await callback.answer("❌ Запрос был отклонен ранее")
#         return


# @router.callback_query(F.data.startswith("accept_outer_profile_"))
# async def accept_outer_profile(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     companion_id = int(callback.data.replace('accept_outer_profile_', ''))
#
#     # Устанавливаем связь
#     await db.set_outer_companion(user_id, companion_id)
#     await db.set_income_companion(companion_id, user_id)
#
#     # Устанавливаем взаимность
#     await db.set_mutual_connection(user_id, companion_id, "outer")
#
#     # Получаем информацию для уведомлений
#     user_info = await db.get_user(user_id)
#     companion_info = await db.get_user(companion_id)
#
#     # Уведомляем инициатора
#     try:
#         await callback.bot.send_message(
#             user_id,
#             f"🎉 Ваш запрос принят! {companion_info['first_name']} согласился на общение.\n\n"
#             f"💌 Контакт: @{companion_info.get('username', 'username_not_set')}"
#         )
#     except Exception as e:
#         print(f"Ошибка уведомления пользователя {user_id}: {e}")
#
#     # Уведомляем companion
#     try:
#         await callback.bot.send_message(
#             companion_id,
#             f"💌 Вы приняли запрос от {user_info['first_name']}!\n\n"
#             f"Контакт: @{user_info.get('username', 'username_not_set')}"
#         )
#     except Exception as e:
#         print(f"Ошибка уведомления companion {companion_id}: {e}")
#
#     await callback.answer("✅ Соединение установлено!")
#     await callback.message.delete()



@router.callback_query(F.data == "connection_cancel")
async def back_to_companions(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass  # Игнорируем ошибки удаления
