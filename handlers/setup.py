from aiogram import Dispatcher
from aiogram.dispatcher.router import Router
from .admin import register_admin_handlers
from .user import register_user_handlers
import logging


def register_routers(dp: Dispatcher):

    logging.info("Start register routers...")

    user_router = Router(name="User Router")
    register_user_handlers(router=user_router)

    admin_router = Router(name="Admin Router")
    register_admin_handlers(router=admin_router)

    dp.include_router(user_router)
    dp.include_router(admin_router)

    logging.info("Successfully register routers...")