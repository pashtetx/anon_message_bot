from .base import Base
from sqlalchemy import Column, UUID, String, Integer, Boolean, DateTime, Text, ForeignKey
import uuid
from sqlalchemy.orm import relationship, Session
from aiogram import Bot
from utils.prepare_content import prepare_response_text
from keyboard.inline_kb import answer_keyboard


class Message(Base):

    __tablename__ = "messages"

    message_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)

    sender_id = Column(ForeignKey("users.user_id"))
    receiver_id = Column(ForeignKey("users.user_id"))

    sender = relationship("User", backref="sended_messages", foreign_keys=[sender_id])
    receiver = relationship("User", backref="received_messages", foreign_keys=[receiver_id])

    async def send(self, bot: Bot):
        text = prepare_response_text(self.text, self.sender, self.receiver.is_admin)
        await bot.send_message(chat_id=self.receiver.tg_user_id, text=text, parse_mode="HTML", reply_markup=answer_keyboard(self.message_id))
    
    async def answer(self, bot: Bot, text: str):

        new_message = Message(
            text = text,
            receiver=self.sender,
            sender=self.receiver,
        )

        await new_message.send(bot=bot)

def get_message_by_id(session: Session, message_id: UUID) -> Message:
    return session.query(Message).filter_by(message_id=message_id).first()


