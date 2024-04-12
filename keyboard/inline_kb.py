from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.user_filter import AnswerCallbackData, Cancel, GetWhoIsCallbackData, Agree, Decline
from filters.admin_filter import NewsletterStart

import uuid

def answer_keyboard(message_id: int, reciever_id: uuid.UUID, whois=True):
    builder = InlineKeyboardBuilder()
    builder.button(text="Ответить 💭", callback_data=AnswerCallbackData(message_id=message_id).pack())
    if whois:
        builder.button(text="Узнать кто это 💌", callback_data=GetWhoIsCallbackData(reciever_id=reciever_id).pack())
    return builder.as_markup()

def cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Отмена 🥊", callback_data=Cancel().pack())
    return builder.as_markup()

def agree_keyboard(proposal_id: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="Принять 💍", callback_data=Agree(proposal_id=proposal_id).pack())
    builder.button(text="Отказаться 🔒", callback_data=Decline(proposal_id=proposal_id).pack())
    return builder.as_markup()

def kb_start_newsletter():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data=NewsletterStart().pack())
    builder.button(text="Нет", callback_data=Cancel().pack())
    return builder.as_markup()