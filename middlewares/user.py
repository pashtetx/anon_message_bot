from typing import Any, Awaitable, Callable, Dict
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from db.models.user import get_user_or_create
import logging

class UserMiddleware(BaseMiddleware):

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        
        logging.info("UserMiddleware starting...")
        
        # Получаем сессию и данные для модели
        session = data.get("session")
        tg_id = event.from_user.id
        username = event.from_user.username
        first_name = event.from_user.first_name
        last_name = event.from_user.last_name
        
        # Ищем юзер, если не находим создаем...
        user = get_user_or_create(session, 
                tg_user_id=tg_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
        
        if user.username != username:
            user.username = username
            user.save(session=session)
        if user.first_name != first_name:
            user.first_name = first_name
            user.save(session=session)
        if user.last_name != last_name:
            user.last_name = last_name
            user.save(session=session)
    

        data["user"] = user

        logging.info("UserMiddleware successfully finded or create user!")

        return await handler(event, data)