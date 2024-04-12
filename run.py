from aiogram import Dispatcher, Bot
from dotenv import dotenv_values
from middlewares import register_middlewares
from handlers import register_routers
import logging
import sys
import asyncio
from db.setup import setup_db

async def start():
    # Конфиг из .env
    config = dotenv_values()

    bot = Bot(token=config.get("TOKEN"), parse_mode="HTML")
    dp = Dispatcher()

    # Инициализуем базу данных
    session_maker = await setup_db(url=config.get("DB_URL"))

    # Устанавливаем промежуточные приложения
    register_middlewares(dp=dp, sessionmaker=session_maker)

    # Инициализируем роутеры, хендлеры
    register_routers(dp=dp)

    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start())