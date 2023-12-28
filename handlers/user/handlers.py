from aiogram.types import Message
from aiogram import Bot

from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart, Command
import logging

from aiogram.fsm.state import State, StatesGroup

class SendMessageState(StatesGroup):
    message_text = State()

async def start(message: Message, bot: Bot):

    link = await create_start_link(bot, str(message.from_user.id), encode=True)

    await message.answer(f"Ваша ссылка: {link}")

async def start_deep_link(message: Message, command: CommandStart):

    args = command.args
    user_id = decode_payload(args)

    await message.answer(f"Введите сообщение чтобы отправить его {user_id}: ")
    


def register_user_handlers(router: Router):
    router.message.register(start_deep_link, CommandStart(deep_link=True))
    router.message.register(start, CommandStart())