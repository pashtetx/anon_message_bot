from typing import Any, Awaitable, Callable, Dict
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram import Dispatcher
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .models import Base
from .models import User, Message
import logging

class DBSessionMiddleware(BaseMiddleware):

    def __init__(self, session: sessionmaker) -> None:
        self.session = session
    
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        with self.session() as session:
            logging.info("Created session!")
            data["session"] = session
            return await handler(event, data)



def setup_db(dp: Dispatcher, url: str) -> None:

    logging.info("Initializing database...")
    engine = create_engine(url)
    logging.info("Create database engine...")

    session = sessionmaker()
    session.configure(bind=engine)

    logging.info("Metadata database creating...")
    Base.metadata.create_all(bind=engine)
    logging.info("Metadata database created!")

    dp.update.middleware.register(DBSessionMiddleware(session=session))