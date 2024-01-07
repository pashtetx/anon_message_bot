from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.user_filter import AnswerCallbackData, Cancel, GetWhoIsCallbackData, Agree
from filters.admin_filter import NewsletterStart

def answer_keyboard(message_id: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="Ответить 💭", callback_data=AnswerCallbackData(message_id=message_id).pack())
    builder.button(text="Узнать кто это 💌", callback_data=GetWhoIsCallbackData(message_id=message_id).pack())
    return builder.as_markup()

def cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Отмена ❌", callback_data=Cancel().pack())
    return builder.as_markup()

def agree_keyboard(message_id: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="Принять ✅", callback_data=Agree(message_id=message_id).pack())
    builder.button(text="Отказаться ❌", callback_data=Cancel().pack())
    return builder.as_markup()

def kb_start_newsletter():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data=NewsletterStart().pack())
    builder.button(text="Нет", callback_data=Cancel().pack())
    return builder.as_markup()