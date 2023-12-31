from .base import Base
from sqlalchemy import Column, UUID, String, Integer, Boolean, DateTime
import uuid
from sqlalchemy.orm import Session
from typing import Optional
import logging

class User(Base):

    __tablename__ = "users"

    user_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tg_user_id = Column(Integer, unique=True)

    username = Column(String(255), unique=True, nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)

    subscribed = Column(Boolean, default=False)
    expire_in = Column(DateTime, nullable=True)


def get_user_or_create(session: Session, tg_user_id: int, **kwargs) -> User:
    logging.info("Searching user...")
    user = session.query(User).filter_by(tg_user_id=tg_user_id).first()
    if not user:
        logging.info("User doesn't finded, creating user...")
        user = User(tg_user_id=tg_user_id, **kwargs)
        session.add(user)
        session.commit()
        logging.info("User created!")
        return user
    logging.info("User finded!")
    return user

def get_user(session: Session, user_id: UUID):
    return session.query(User).filter_by(user_id=user_id).first()
