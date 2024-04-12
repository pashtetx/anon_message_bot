from .base import Base
from sqlalchemy import Column, UUID, String, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
import uuid
import random
from datetime import datetime

class User(Base):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    
    joined_at: Mapped[datetime] = mapped_column(default=datetime.now)

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar: Mapped[int] = mapped_column(BigInteger, nullable=True)

    fake_username: Mapped[str] = mapped_column(String(25), unique=True, nullable=True)

    is_admin: Mapped[bool] = mapped_column(default=False)

    def __init__(self, **kw):
        self.fake_username = "".join([random.choice("1234567890") for i in range(10)])
        super().__init__(**kw)