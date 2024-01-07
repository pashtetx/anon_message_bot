from aiogram.dispatcher.router import Router
from aiogram.types import Message, CallbackQuery
from db.models.user import User, get_users
from aiogram.filters import Command
from filters.admin_filter import IsAdmin, NewsletterStart

from aiogram import Bot

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboard.inline_kb import cancel_keyboard, kb_start_newsletter

from sqlalchemy.orm import Session
from utils.send import send_message
from utils.parse_buttons import parse_buttons

class Newsletter(StatesGroup):
    text = State()
    buttons = State()


async def newsletter_create(message: Message, user: User, state: FSMContext):
    await message.answer("Введите текст для рассылки: ", reply_markup=cancel_keyboard())
    await state.set_state(Newsletter.text)

async def newsletter_text(message: Message, user: User, state: FSMContext):
    await message.answer("Введите кнопки для рассылки: ", reply_markup=cancel_keyboard())
    await state.update_data({
        "text":message.text
    })
    await state.set_state(Newsletter.buttons)

async def newsletter_buttons(message: Message, user: User, state: FSMContext, session: Session, bot: Bot):
    await message.answer("Вот так выглядит ваша рассылка: ")

    data = await state.get_data()

    text = data.get("text")

    try:
        buttons = parse_buttons(message.text)
    except Exception:
        await message.answer("❌ Ошибка, попробуй написать заново.")

    await send_message(user=user, text=text, reply_markup=buttons, bot=bot, session=session)

    await state.update_data({
        "buttons":buttons
    })

    await message.answer("Запустить рассылку?", reply_markup=kb_start_newsletter())

async def start_newsletter(callback: CallbackQuery, callback_data: NewsletterStart, session: Session, state: FSMContext, bot: Bot):
    data = await state.get_data()

    text = data.get("text")
    buttons = data.get("buttons")

    users = get_users(session=session)

    for user in users:
        await send_message(user=user, text=text, reply_markup=buttons, bot=bot, session=session)

    await callback.answer()

def register_admin_handlers(router: Router):
    router.message.register(newsletter_create, Command("send"), IsAdmin())
    router.message.register(newsletter_text, Newsletter.text)
    router.message.register(newsletter_buttons, Newsletter.buttons)
    router.callback_query.register(start_newsletter, NewsletterStart.filter())