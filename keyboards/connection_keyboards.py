from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_connection_request_keyboard(from_user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_request_{from_user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_request_{from_user_id}")
        ]
    ])

def get_connection_response_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Закрыть", callback_data="connection_cancel")],
        ])

def get_profile_action_keyboard(companion_id, has_pending_request=False, is_connected=False):
    if has_pending_request:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏳ Запрос отправлен", callback_data="request_pending")]
        ])
    elif is_connected:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Уже соединены", callback_data="already_connected")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_outer_profile_{companion_id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_profile_{companion_id}")]
        ])