from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from db.models import User
from sqlalchemy.orm import Session
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from db.models.user import User, delete_user

async def send_message(user: User, text: str, reply_markup: InlineKeyboardMarkup, bot: Bot, session: Session):
    try:
        await bot.send_message(chat_id=user.tg_user_id, text=text, reply_markup=reply_markup)
    except TelegramForbiddenError:
        delete_user(session=session, user=user)