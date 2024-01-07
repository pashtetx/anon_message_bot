from aiogram.filters.callback_data import CallbackData
from uuid import UUID

class AnswerCallbackData(CallbackData, prefix="answer"):
    message_id: UUID

class GetWhoIsCallbackData(CallbackData, prefix="whois"):
    message_id: UUID

class Cancel(CallbackData, prefix="cancel"):
    pass

class Agree(CallbackData, prefix="agree"):
    message_id: UUID