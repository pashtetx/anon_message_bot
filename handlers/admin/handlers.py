from aiogram.dispatcher.router import Router
from aiogram.types import Message, CallbackQuery
from db.models import User, Message
from aiogram.filters import Command
from filters.admin_filter import IsAdmin, NewsletterStart

from aiogram import Bot

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboard.inline_kb import cancel_keyboard, kb_start_newsletter

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from utils.send import send_message
from utils.parse_buttons import parse_buttons
from datetime import datetime


class Newsletter(StatesGroup):
    text = State()
    buttons = State()

async def newsletter_create(message: Message, user: User, state: FSMContext):
    message_question = await message.answer("Введите текст для рассылки: ", reply_markup=cancel_keyboard())
    await state.set_state(Newsletter.text)
    await state.update_data({
        "message_delete":[message_question],
    })

async def newsletter_text(message: Message, user: User, state: FSMContext):
    message_question = await message.answer("Введите кнопки для рассылки\nПример: button 1-https://google.com#button 2-https://telegram.com ", reply_markup=cancel_keyboard())
    await state.update_data({
        "text":message.text,
        "message_delete":[message_question],
    })
    await state.set_state(Newsletter.buttons)

async def newsletter_buttons(message: Message, user: User, state: FSMContext, session: Session, bot: Bot):
    message_show = await message.answer("Вот так выглядит ваша рассылка: ")

    data = await state.get_data()

    text = data.get("text")

    try:
        buttons = parse_buttons(message.text)
    except Exception:
        await message.answer("❌ Ошибка, попробуй написать заново.")

    message_preview = await send_message(user=user, text=text, reply_markup=buttons, bot=bot, session=session)
    message_start_news_letter = await message.answer("Запустить рассылку?", reply_markup=kb_start_newsletter())
    await state.update_data({
        "buttons":buttons,
        "message_delete":[message_start_news_letter, message_show, message_preview]
    })

    

async def start_newsletter(callback: CallbackQuery, callback_data: NewsletterStart, session: Session, state: FSMContext, bot: Bot):
    data = await state.get_data()

    text = data.get("text")
    buttons = data.get("buttons")

    users = await User.objects.all(session=session)

    for user in users:
        await send_message(user=user, text=text, reply_markup=buttons, bot=bot, session=session)

    await callback.answer()

async def analytic(message: Message, session: AsyncSession):
    users_count = await User.objects.count(session)
    today = datetime.now()
    today.replace(hour=0)
    today_joined_users = await User.objects.filter(joined_at__gt=today).count(session)
    messages_count = await Message.objects.count(session)
    
    response = (
        "📉 Аналитика",
        "",
        f"👥 Всего пользователей: {users_count}",
        f"🆕 За сегодня: {today_joined_users}",
        "",
        f"☁ Всего сообщений: {messages_count}",
    )
    
    await message.answer("\n".join(response))

def register_admin_handlers(router: Router):
    router.message.register(newsletter_create, Command("send"), IsAdmin())
    router.message.register(analytic, Command("analytic"), IsAdmin())
    router.message.register(newsletter_text, Newsletter.text)
    router.message.register(newsletter_buttons, Newsletter.buttons)
    router.callback_query.register(start_newsletter, NewsletterStart.filter())