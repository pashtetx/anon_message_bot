from aiogram.types import Message, CallbackQuery
from aiogram import Bot

from sqlalchemy.orm import Session

from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
import logging

from aiogram.fsm.state import State, StatesGroup

from db.models.user import get_user_or_create, User, get_user, get_random_user
from db.models.message import get_message_by_id, Message

from utils.prepare_content import prepare_response_text, prepare_start_text
from filters.user_filter import AnswerCallbackData, Cancel, GetWhoIsCallbackData, Agree
from sqlalchemy.exc import IntegrityError


from keyboard.inline_kb import cancel_keyboard, agree_keyboard, answer_keyboard


class SendMessageState(StatesGroup):
    message_text = State()

async def get_link(message: Message, bot: Bot, user: User):
    link = await create_start_link(bot, str(user.tg_user_id), encode=True)
    await message.answer(f"🔗 Ваша ссылка: <code>{link}</code>", parse_mode="HTML")

async def start(message: Message, bot: Bot, user: User):
    text = prepare_start_text(user)
    await message.answer(text, parse_mode="HTML")

async def start_deep_link(message: Message, command: CommandStart, user: User, session: Session, state: FSMContext):

    logging.info("Deep link starting...")

    args = command.args
    receiver_user_id = decode_payload(args)
    logging.info("Getting reciever user...")
    receiver_user = get_user(session=session, tg_user_id=receiver_user_id)
    
    if not receiver_user:
        logging.info(f"User doesn't exist. user_id={receiver_user}")
        return await message.answer("❌ Ссылка недействительна.")

    if receiver_user.user_id == user.user_id:
        logging.info("User try send message yourself.")
        return await message.answer("❌ Вы не можете отправить сообщение самому себе. ")

    await state.update_data({"receiver_user":receiver_user})

    logging.info(f"Got reciever user - {receiver_user.username} ({receiver_user.user_id})")

    await message.answer(f"Введите сообщение чтобы отправить его получателю: ", reply_markup=cancel_keyboard())
    await state.set_state(SendMessageState.message_text)
    
    logging.info("Deep link successfully ended!")


async def random(message: Message, user: User, session: Session, state: FSMContext):
    await state.set_state(SendMessageState.message_text)

    receiver_user = get_random_user(session, user)
    await state.update_data({
        "receiver_user": receiver_user,
    })

    await message.answer("Введите сообщение чтобы отправить его рандому:", reply_markup=cancel_keyboard())


async def answer_message(callback: CallbackQuery, callback_data: AnswerCallbackData, state: FSMContext, session: Session):
    message_id = callback_data.message_id
    message = get_message_by_id(session=session, message_id=message_id)

    await state.update_data({
        "receiver_user": message.sender
    })

    await state.set_state(SendMessageState.message_text)
    await callback.message.answer("Отправьте сообщение чтобы ответить: ", reply_markup=cancel_keyboard())
    await callback.answer()

async def change_fake_username(message: Message, user: User, session: Session, command: Command):
    logging.info("Start changing fake_username...")
    logging.info("Getting message text...")

    text = command.args

    if not text:
        logging.warn("Command doesn't have args.")
        return await message.answer("❌ Отправьте текст!")
    
    logging.info(f"Args: {text}")

    if text.find("<emoji") > 0:
        logging.warn("Args contains special emojis.")
        return await message.answer("❌ Текст содержит специальные эмоджи! ")
    
    if text == user.fake_username:
        logging.warn(f"Args equals user.fake_username, {text} == {user.fake_username}")
        return await message.answer("❌ У вас такое же имя.")
    

    user.fake_username = text
    try:
        session.add(user)
        session.commit()
        session.flush()
    except IntegrityError:
        return await message.answer("❌ Это имя уже занято.")

    await message.answer("✅ Вы успешно сменили анонимное имя на: {fake_username}".format(fake_username=user.fake_username))



async def get_message_to_send(message: Message, user: User, session: Session, state: FSMContext, bot):
    data = await state.get_data()

    receiver_user = data.get("receiver_user")

    if not message.text and not message.caption:
        logging.warn("Message doesn't have text.")
        return await message.answer("❌ Отправьте текст!")
    
    if message.text.find("<emoji") > 0 and message.text.find("</emoji>") > 0:
        logging.warn("Message contains special emojis.")
        return await message.answer("❌ Текст содержит специальные эмоджи! ")

    db_message = Message(
        text=message.text or message.caption,
        receiver=receiver_user,
        sender=user,
    )

    session.add(db_message)
    session.commit()
    session.flush()

    await db_message.send(bot=bot)
    await message.answer("✅ Сообщение успешно отправлено!")
    await state.clear()


async def cancel_callbackquery(callback: CallbackQuery, callback_data: str, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.delete()


async def whois_callbackquery(callback: CallbackQuery, callback_data: GetWhoIsCallbackData, session: Session, bot: Bot):
    await callback.message.answer("✅ Сообщение отправлено. Если пользователь примет предложение, то вам придет его юзернейм, и он увидит ваш юзернейм!")
    message = get_message_by_id(session=session, message_id=callback_data.message_id)
    await bot.send_message(chat_id=message.sender.tg_user_id, text="От пользователя пришло предложение расскрыть юзернейм. <b>Вы согласны?</b>",
                           reply_markup=agree_keyboard(message.message_id), parse_mode="HTML")
    
    text = prepare_response_text(message.text, message.sender, message.receiver.is_admin)

    await callback.message.edit_text(
        text=text,
        reply_markup=answer_keyboard(message_id=message.message_id, whois=False),
        parse_mode="HTML",
    )
    
    await callback.answer()

async def agree_callbackquery(callback: CallbackQuery, callback_data: Agree, session: Session, bot: Bot):
    message = get_message_by_id(session=session, message_id=callback_data.message_id)

    await bot.send_message(chat_id=message.receiver.tg_user_id, text=f"{message.sender.fake_username} это @{message.sender.username}")
    await bot.send_message(chat_id=message.sender.tg_user_id, text=f"{message.receiver.fake_username} это @{message.receiver.username}")

    await callback.answer()
    await callback.message.delete()


def register_user_handlers(router: Router):
    router.message.register(start_deep_link, CommandStart(deep_link=True))
    router.message.register(start, CommandStart())
    router.message.register(get_link, Command("link"))
    router.message.register(get_message_to_send, SendMessageState.message_text)
    router.message.register(random, Command("random"))
    router.callback_query.register(cancel_callbackquery, Cancel.filter())
    router.callback_query.register(answer_message, AnswerCallbackData.filter())
    router.callback_query.register(whois_callbackquery, GetWhoIsCallbackData.filter())
    router.callback_query.register(agree_callbackquery, Agree.filter())
    router.message.register(change_fake_username, Command("username"))