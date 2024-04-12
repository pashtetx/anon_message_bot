from aiogram.filters.callback_data import CallbackData
from uuid import UUID

class AnswerCallbackData(CallbackData, prefix="answer"):
    message_id: UUID

class GetWhoIsCallbackData(CallbackData, prefix="whois"):
    reciever_id: UUID

class Cancel(CallbackData, prefix="cancel"):
    pass

class Agree(CallbackData, prefix="agree"):
    proposal_id: UUID

class Decline(CallbackData, prefix="decline"):
    proposal_id: UUID