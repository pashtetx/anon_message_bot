from typing import Any
from aiogram.filters import Filter
from aiogram.filters.callback_data import CallbackData
from db.models.user import User


class IsAdmin(Filter):

    async def __call__(self, message, session, **kwargs) -> Any:
        user = await User.objects.get(session=session, tg_user_id=message.from_user.id)
        return user.is_admin
    

class NewsletterStart(CallbackData, prefix="newsletter_start"):
    pass