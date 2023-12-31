from .base import Base
from sqlalchemy import Column, UUID, String, Integer, Boolean, DateTime, Text, ForeignKey
import uuid


class Message(Base):

    __tablename__ = "messages"

    message_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)

    sender_id = Column(ForeignKey("users.user_id"))
    receiver_id = Column(ForeignKey("users.user_id"))





