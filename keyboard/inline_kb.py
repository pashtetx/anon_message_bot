from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.user_filter import AnswerCallbackData

def answer_keyboard(message_id: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="Ответить 💭", callback_data=AnswerCallbackData(message_id=message_id).pack())
    return builder.as_markup()

