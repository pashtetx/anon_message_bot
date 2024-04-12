from typing import Any
from .base import Base
from sqlalchemy import ForeignKey
import uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped

from aiogram import Bot


class Proposal(Base):

    __tablename__ = "proposals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    reciever_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    sender: Mapped["User"] = relationship(backref="sent_proposals", foreign_keys=[sender_id], lazy="joined")
    reciever: Mapped["User"] = relationship(backref="recieved_proposals", foreign_keys=[reciever_id], lazy="joined")
    
    async def accept(self, bot: Bot):
        if self.sender.username:
            await bot.send_message(chat_id=self.sender.tg_user_id, text=f"{self.reciever.fake_username} это @{self.reciever.username}")
        else:
            await bot.send_message(chat_id=self.sender.tg_user_id, text=f"{self.reciever.fake_username} это {self.reciever.first_name} {self.reciever.last_name}")
        if self.reciever.username:
            await bot.send_message(chat_id=self.reciever.tg_user_id, text=f"{self.sender.fake_username} это @{self.sender.username}")
        else:
            await bot.send_message(chat_id=self.reciever.tg_user_id, text=f"{self.sender.fake_username} это {self.sender.firse_name} {self.reciever.last_name}")
    
    async def decline(self, bot: Bot):
        await bot.send_message(chat_id=self.sender.tg_user_id, text=f"{self.reciever.fake_username} отклонил запрос... 💔")

