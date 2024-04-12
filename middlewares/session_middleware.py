from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker

import logging


class DBSessionMiddleware(BaseMiddleware):

    def __init__(self, session: async_sessionmaker) -> None:
        self.session = session
    
    async def __call__(self, handler, event, data):
        async with self.session() as session:
            logging.info("Created session!")
            data["session"] = session
            return await handler(event, data)
