from aiogram.filters.callback_data import CallbackData
from uuid import UUID

class AnswerCallbackData(CallbackData, prefix="answer"):
    message_id: UUID