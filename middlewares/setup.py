from aiogram import Dispatcher
from aiogram.dispatcher.router import Router
from .user import UserMiddleware


def register_middlewares(dp: Dispatcher):
    dp.message.middleware(UserMiddleware())