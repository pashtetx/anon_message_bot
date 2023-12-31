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

    bot = Bot(token=config.get("TOKEN"))
    dp = Dispatcher()

    # Инициализуем базу данных
    setup_db(dp=dp, url=config.get("DB_URL"))

    # Устанавливаем промежуточные приложения
    register_middlewares(dp=dp)

    # Инициализируем роутеры, хендлеры
    register_routers(dp=dp)

    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start())