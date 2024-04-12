from typing import Any, Awaitable, Callable, Dict
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject


class AutoMessageMiddleware(BaseMiddleware):

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        state = data.get("state")
        state_data = await state.get_data()
        messages = state_data.get("message_delete")
        if messages:
            for message in messages:
                await message.delete()
        return await handler(event, data)