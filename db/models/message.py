from .base import Base
from sqlalchemy import ForeignKey, Text
import uuid
from sqlalchemy.orm import relationship, Session, mapped_column, Mapped
from aiogram import Bot
from utils.prepare_content import prepare_response_text
from keyboard.inline_kb import answer_keyboard
from datetime import datetime

class Message(Base):

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    sender: Mapped["User"] = relationship(backref="sended_messages", foreign_keys=[sender_id], uselist=False, lazy="joined")
    receiver: Mapped["User"] = relationship(backref="received_messages", foreign_keys=[receiver_id], uselist=False, lazy="joined")

    async def send_message(self, bot: Bot):
        text = prepare_response_text(self.text, self.sender, self.receiver.is_admin)
        await bot.send_message(chat_id=self.receiver.tg_user_id, text=text, parse_mode="HTML", reply_markup=answer_keyboard(self.id, self.sender_id))

