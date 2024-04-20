from aiogram.types import Message, CallbackQuery
from db.models.proposal import Proposal
from aiogram.types import Message as TelegramMessage
from db.models import Message as Message
from db.models import Proposal
from aiogram import Bot

from sqlalchemy.orm import Session

from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
import logging

from aiogram.fsm.state import State, StatesGroup

from db.models.user import User

from utils.prepare_content import prepare_response_text, prepare_start_text
from filters.user_filter import AnswerCallbackData, Cancel, GetWhoIsCallbackData, Agree, Decline
from sqlalchemy.exc import IntegrityError
from keyboard.inline_kb import cancel_keyboard, agree_keyboard, answer_keyboard

class SendMessageState(StatesGroup):
    message_text = State()

async def get_link(message: TelegramMessage, bot: Bot, user: User):
    link = await create_start_link(bot, str(user.tg_user_id), encode=True)
    await message.answer(f"🔗 Ваша ссылка: <code>{link}</code>", parse_mode="HTML")

async def start(message: TelegramMessage, bot: Bot, user: User):
    text = prepare_start_text(user)
    await message.answer(text, parse_mode="HTML")

async def start_deep_link(message: TelegramMessage, command: CommandStart, user: User, session: Session, state: FSMContext):

    logging.info("Deep link starting...")

    args = command.args
    receiver_user_id = decode_payload(args)
    logging.info("Getting reciever user...")
    receiver_user = await User.objects.get(session=session, tg_user_id=int(receiver_user_id))
    
    if not receiver_user:
        logging.info(f"User doesn't exist. user_id={receiver_user}")
        return await message.answer("❌ Ссылка недействительна.")

    if receiver_user.id == user.id:
        logging.info("User try send message yourself.")
        return await message.answer("❌ Вы не можете отправить сообщение самому себе. ")

    await state.update_data({"receiver_user_id":receiver_user.id, "action":"send"})

    logging.info(f"Got reciever user - {receiver_user.username} ({receiver_user.id})")

    message = await message.answer(f"Введите сообщение чтобы отправить его получателю: ", reply_markup=cancel_keyboard())
    await state.set_state(SendMessageState.message_text)
    await state.update_data({"message_delete":[message]})
    logging.info("Deep link successfully ended!")

async def random(message: TelegramMessage, user: User, session: Session, state: FSMContext):
    await state.set_state(SendMessageState.message_text)
    await state.update_data({"action": "random"})
    message = await message.answer("Введите сообщение чтобы отправить его рандому:", reply_markup=cancel_keyboard())
    await state.update_data({"message_delete":[message]})

async def answer_message(callback: CallbackQuery, callback_data: AnswerCallbackData, state: FSMContext, session: Session):
    message_id = callback_data.message_id
    message = await Message.objects.get(session=session, id=message_id)
    await state.update_data({"receiver_user_id": message.sender.id, "action":"answer"})
    await state.set_state(SendMessageState.message_text)
    message = await callback.message.answer("Отправьте сообщение чтобы ответить: ", reply_markup=cancel_keyboard())
    await state.update_data({"message_delete":[message]})
    await callback.answer()

async def change_fake_username(message: TelegramMessage, user: User, session: Session, command: Command):
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
        await user.save(session)
    except IntegrityError:
        return await message.answer("❌ Это имя уже занято.")

    await message.answer("✅ Вы успешно сменили анонимное имя на: {fake_username}".format(fake_username=user.fake_username))

async def get_message_to_send(message: TelegramMessage, user: User, session: Session, state: FSMContext, bot: Bot):    
    if not message.text and not message.caption:
        logging.warn("Message doesn't have text.")
        return await message.answer("❌ Отправьте текст!")
    
    if message.text.find("<emoji") > 0 and message.text.find("</emoji>") > 0:
        logging.warn("Message contains special emojis.")
        return await message.answer("❌ Текст содержит специальные эмоджи! ")
    
    data = await state.get_data()
    receiver_user_id = data.get("receiver_user_id")
    action = data.get("action")
    
    if action == "send" or action == "answer":
        receiver_user = await User.objects.get(session, id=receiver_user_id)
    elif action == "random":
        receiver_user = await User.objects.random(session, id__not=user.id)

    orm_message = Message(text=message.text or message.caption, receiver=receiver_user, sender=user)
    await orm_message.save(session)
        
    while True:
        try:
            await orm_message.send_message(bot=bot)
            break
        except TelegramForbiddenError:
            if action == "send" or action == "answer":
                break
            elif action == "random":
                await session.delete(orm_message)
                await session.delete(receiver_user)
                receiver_user = await User.objects.random(session, id__not=user.id)
                orm_message = Message(text=message.text or message.caption, receiver=receiver_user, sender=user)
                await orm_message.save(session)
                await session.commit()
    await message.answer("✨ Сообщение успешно отправлено!")
    await state.clear()

async def cancel_callbackquery(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    
async def whois_callbackquery(callback: CallbackQuery, callback_data: GetWhoIsCallbackData, session: Session, bot: Bot):
    sender = await User.objects.get(session, tg_user_id=callback.from_user.id)
    reciever = await User.objects.get(session, id=callback_data.reciever_id)
    proposal = await Proposal.objects.get(session, sender=sender, reciever=reciever)
    if proposal:
        return await bot.answer_callback_query(callback.id, "Вы уже отправляли предложение этому пользователю!", show_alert=True)
    proposal = Proposal(sender=sender, reciever=reciever)
    await proposal.save(session)

    await callback.message.answer("✅ Сообщение отправлено. Если пользователь примет предложение, то вам придет его юзернейм, и он увидит ваш юзернейм!")
    await bot.send_message(chat_id=reciever.tg_user_id, text="От пользователя пришло предложение расскрыть юзернейм. <b>Вы согласны?</b>", reply_markup=agree_keyboard(proposal.id))
    await callback.answer()

async def accept_proposal(callback: CallbackQuery, callback_data: Agree, session: Session, bot: Bot):
    proposal = await Proposal.objects.get(session=session, id=callback_data.proposal_id)
    await proposal.accept(bot)
    await proposal.delete(session)
    await callback.answer()
    await callback.message.delete()

async def decline_proposal(callback: CallbackQuery, callback_data: Agree, session: Session, bot: Bot):
    proposal = await Proposal.objects.get(session=session, id=callback_data.proposal_id)
    await proposal.decline(bot)
    await proposal.delete(session)
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
    router.callback_query.register(accept_proposal, Agree.filter())
    router.callback_query.register(decline_proposal, Decline.filter())
    router.message.register(change_fake_username, Command("username"))