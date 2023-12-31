from aiogram.types import Message
from aiogram import Bot

from sqlalchemy.orm import Session

from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import logging

from aiogram.fsm.state import State, StatesGroup

from db.models.user import get_user_or_create, User, get_user

from utils.prepare_content import prepare_response_text, prepare_start_text


class SendMessageState(StatesGroup):
    message_text = State()

async def get_link(message: Message, bot: Bot, user: User):
    link = await create_start_link(bot, str(user.user_id), encode=True)
    await message.answer(f"🔗 Ваша ссылка: <code>{link}</code>", parse_mode="HTML")

async def start(message: Message, bot: Bot, user: User):
    text = prepare_start_text(user)
    await message.answer(text, parse_mode="HTML")

async def start_deep_link(message: Message, command: CommandStart, user: User, session: Session, state: FSMContext):

    logging.info("Deep link starting...")

    args = command.args
    reciever_user_id = decode_payload(args)
    logging.info("Getting reciever user...")
    reciever_user = get_user(session=session, user_id=reciever_user_id)
        
    if reciever_user.user_id == user.user_id:
        logging.info("User try send message yourself.")
        return await message.answer("❌ Вы не можете отправить сообщение самому себе. ")

    await state.update_data({"reciever_user":reciever_user})

    logging.info(f"Got reciever user - {reciever_user.username} ({reciever_user.user_id})")

    await message.answer(f"Введите сообщение чтобы отправить его @{reciever_user.username}: ")
    await state.set_state(SendMessageState.message_text)
    
    logging.info("Deep link successfully ended!")

async def get_message_to_send(message: Message, user: User, session: Session, state: FSMContext, bot):
    data = await state.get_data()

    reciever_user = data.get("reciever_user")

    text = prepare_response_text(message.text or message.caption, user, reciever_user.subscribed)

    await bot.send_message(text=text, chat_id=reciever_user.tg_user_id, parse_mode="HTML")
    await state.clear()



def register_user_handlers(router: Router):
    router.message.register(start_deep_link, CommandStart(deep_link=True))
    router.message.register(start, CommandStart())
    router.message.register(get_link, Command("link"))
    router.message.register(get_message_to_send, SendMessageState.message_text)