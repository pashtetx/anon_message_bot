from aiogram import Dispatcher
from aiogram.dispatcher.router import Router
from .user import UserMiddleware
from .session_middleware import DBSessionMiddleware
from .auto_message_delete import AutoMessageMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker


def register_middlewares(dp: Dispatcher, sessionmaker: async_sessionmaker):
    dp.update.middleware(DBSessionMiddleware(session=sessionmaker))
    dp.message.middleware(UserMiddleware())
    dp.update.middleware(AutoMessageMiddleware())