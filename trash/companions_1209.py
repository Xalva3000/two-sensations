# @router.callback_query(F.data == "back_to_companions")
# async def back_to_companions(callback: CallbackQuery):
#     try:
#         await callback.message.delete()
#     except:
#         pass  # Игнорируем ошибки удаления
#
# #     await callback.message.answer(
# #         "👥 Ваши собеседники:",
# #         reply_markup=get_companions_menu_keyboard()
# #     )

# @router.callback_query(F.data == "menu_view_outer_companion")
# async def view_outer_companion(callback: CallbackQuery):
#     user = await db.get_user(callback.from_user.id)
#     if not user or not user.get('outer_companion_telegram_id'):
#         await callback.answer("У вас нет собеседника, которого вы нашли")
#         return
#
#     companion = await db.get_companion_info(user['outer_companion_telegram_id'])
#     if not companion:
#         await callback.answer("Собеседник не найден")
#         return
#
#     await show_companion_profile(callback, companion, "outer")
#
#
# @router.callback_query(F.data == "menu_view_income_companion")
# async def view_income_companion(callback: CallbackQuery):
#     user = await db.get_user(callback.from_user.id)
#     if not user or not user.get('income_companion_telegram_id'):
#         await callback.answer("У вас нет собеседника, который вас нашел")
#         return
#
#     companion = await db.get_companion_info(user['income_companion_telegram_id'])
#     if not companion:
#         await callback.answer("Собеседник не найден")
#         return
#
#     await show_companion_profile(callback, companion, "income")

# async def show_companion_profile(callback: CallbackQuery, companion, companion_type):
#     try:
#         # Проверяем валидность данных
#         if not companion:
#             await callback.answer("❌ Профиль собеседника не найден")
#             return
#
#         # Форматируем текст профиля
#         profile_text = format_companion_profile(companion, companion_type)
#
#         # Получаем клавиатуру
#         keyboard = get_companion_action_keyboard(companion['telegram_id'], companion_type)
#
#         # Отправляем сообщение
#         await send_companion_message(callback, companion, profile_text, keyboard)
#
#     except Exception as e:
#         print(f"Ошибка показа профиля companion: {e}")
#         await callback.answer("❌ Ошибка загрузки профиля")


# async def send_companion_message(callback, companion, profile_text, keyboard):
#     """Отправляет сообщение с профилем собеседника"""
#     photo_id = companion.get('photo_id')
#     is_photo_confirmed = companion.get('is_photo_confirmed', False)
#
#     # Проверяем можно ли отправить фото
#     can_send_photo = photo_id and is_photo_confirmed
#
#     if can_send_photo:
#         try:
#             await callback.message.answer_photo(
#                 photo_id,
#                 caption=profile_text,
#                 reply_markup=keyboard
#             )
#             return
#         except Exception as e:
#             print(f"Не удалось отправить фото companion: {e}")
#             # Продолжаем с текстовым сообщением
#
#     # Текстовое сообщение (fallback)
#     await callback.message.answer(
#         profile_text,
#         reply_markup=keyboard
#     )

# @router.callback_query(F.data.startswith("report_"))
# async def report_companion(callback: CallbackQuery):
#     companion_id = int(callback.data.replace('report_', ''))
#     # Логика репорта
#     await callback.answer("Репорт отправлен")

# @router.callback_query(F.data.startswith("decrease_balance_"))
# async def decrease_companion_balance(callback: CallbackQuery):
#     # получение id собеседника из клавиатуры
#     companion_id = int(callback.data.replace('decrease_balance_', ''))
#     # отправка и сообщение
#     await db.decrease_balance(companion_id)
#     await callback.answer("Очки собеседника тают!")
#
# @router.callback_query(F.data.startswith("increase_balance_"))
# async def increase_companion_balance(callback: CallbackQuery):
#     # получение id собеседника из клавиатуры
#     companion_id = int(callback.data.replace('increase_balance_', ''))
#     # отправка и сообщение
#     await db.increase_balance(companion_id)
#     await callback.answer("Очки собеседника взлетают!")

# @router.callback_query(F.data.startswith("message_"))
# async def message_companion(callback: CallbackQuery):
#     companion_id = int(callback.data.replace('message_', ''))
#     companion = await db.get_user(companion_id)
#     if companion and companion.get('username'):
#         await callback.answer(f"Напишите @{companion['username']}")
#     else:
#         await callback.answer("Username не доступен")


#
# @router.callback_query(F.data == "settings_remove_income_companion")
# async def confirm_remove_income_companion(callback: CallbackQuery, state: FSMContext):
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_income_delete")],
#         [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete")]
#     ])
#
#     await callback.message.edit_text(
#         "❓ Вы уверены, что хотите удалить собеседника, который вас нашел?\n"
#         "Это действие нельзя отменить.",
#         reply_markup=keyboard
#     )
#     await state.set_state(ConfirmDeleteState.confirm_income_delete)
#
#
# @router.callback_query(ConfirmDeleteState.confirm_outer_delete, F.data == "confirm_outer_delete")
# async def process_outer_delete(callback: CallbackQuery, state: FSMContext):
#     await db.remove_outer_companion(callback.from_user.id)
#     await callback.message.edit_text(
#         "✅ Собеседник, которого Вы нашли, удален из Вашего профиля",
#         reply_markup=get_companion_close_keyboard()
#     )
#     await state.clear()
#
#
# @router.callback_query(ConfirmDeleteState.confirm_income_delete, F.data == "confirm_income_delete")
# async def process_income_delete(callback: CallbackQuery, state: FSMContext):
#     await db.remove_income_companion(callback.from_user.id)
#     await callback.message.edit_text(
#         "✅ Собеседник, который Вас нашел, удален из Вашего профиля",
#         reply_markup=get_companion_close_keyboard()
#     )
#     await state.clear()


# @router.callback_query(F.data == "cancel_delete")
# async def cancel_delete(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(
#         "⚙️ Настройки:",
#         reply_markup=get_companions_slots_keyboard()
#     )
#     await state.clear()


# @router.callback_query(F.data.startswith("remove_companion_confirm"))
# async def remove_companion_handler(callback: CallbackQuery, state: FSMContext):
#     """Обработчик кнопки удаления companion"""
#     data_parts = callback.data.split('_')
#     if len(data_parts) < 3:
#         await callback.answer("❌ Ошибка запроса")
#         return
#
#     companion_id = int(data_parts[2])
#
#     # Сохраняем данные в state для подтверждения
#     await state.update_data(
#         companion_id=companion_id
#     )
#
#
#     # Клавиатура подтверждения
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_companion_delete")],
#         [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_companion_delete")]
#     ])
#
#     await callback.message.answer(
#         f"❓ Вы уверены, что хотите удалить собеседника?\n\n"
#         "Это действие нельзя отменить. Вы потеряете контакт с этим пользователем.",
#         reply_markup=keyboard
#     )
#     await state.set_state(ConfirmCompanionDeleteState.waiting_confirmation)



# @router.callback_query(F.data.startswith("back_to_profile_"))
# async def back_to_profile_handler(callback: CallbackQuery):
#     """Возврат к профилю companion"""
#     companion_id = int(callback.data.replace('back_to_profile_', ''))
#     companion = await db.get_companion_info(companion_id)
#
#     if companion:
#         # Определяем тип companion
#         user = await db.get_user(callback.from_user.id)
#
#         await show_companion_profile(callback, companion)
#     else:
#         await callback.answer("❌ Профиль не найден")
#         await callback.message.edit_text(
#             "👥 Ваши собеседники:",
#             reply_markup=get_companions_slots_keyboard()
#         )
# def get_companion_close_keyboard():
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Закрыть", callback_data="back_to_companions")],
#     ])