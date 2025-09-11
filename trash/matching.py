
# async def find_match(message: Message, user_id: int):
#     user = await db.get_user(user_id)
#
#     if not user or not user.get('gender') or not user.get('age'):
#         await message.answer("Сначала заполните анкету!")
#         return
#
#     match = await db.get_random_user(user_id)
#     if not match:
#         await message.answer("Пока нет подходящих анкет. Попробуйте позже!")
#         return
#
#     # Формируем список тем для отображения
#     match_topics = match.get('topics', [])
#     topics_text = ""
#     if match_topics:
#         topics_names = [TOPICS_LIST[i - 1] for i in match_topics if 1 <= i <= 20]
#         topics_text = f"📝 Темы: {', '.join(topics_names)}"
#
#     profile_text = (
#         f"👤 {match['first_name']}\n"
#         f"🎂 Возраст: {age_groups.get(match['age'], 'Не указан')}\n"
#         f"👫 Пол: {'Мужской' if match['gender'] == 1 else 'Женский'}\n"
#     )
#
#     if match.get('city'):
#         profile_text += f"🏙️ Город: {match['city']}\n"
#
#     if user.get('about'):
#         profile_text += f"\n📖 О себе:\n{user['about']}\n"
#
#     if topics_text:
#         profile_text += f"{topics_text}\n"
#
#     # Сохраняем ID найденного пользователя для последующих действий
#     # Можно использовать FSM или временное хранилище
#     photo = match.get('photo_id', match['photo_id'])
#     if photo:
#         await message.answer_photo(
#             photo,
#             caption=profile_text,
#             reply_markup=get_profile_action_keyboard(match['telegram_id'])
#         )
#     else:
#         await message.answer(
#             text=profile_text,
#             reply_markup=get_profile_action_keyboard(match['telegram_id'])
#         )
