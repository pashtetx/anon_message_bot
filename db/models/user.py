from .base import Base
from sqlalchemy import Column, UUID, String, Integer, Boolean, DateTime, BigInteger, JSON
import uuid
from sqlalchemy.orm import Session
from typing import Any, Optional
import logging
import random
from typing import List

class User(Base):

    __tablename__ = "users"

    user_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tg_user_id = Column(BigInteger, unique=True)

    username = Column(String(255), unique=True, nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)

    fake_username = Column(String(25), unique=True, nullable=True)

    is_admin = Column(Boolean, default=False)

    def __init__(self, **kw: Any):

        self.fake_username = "".join([random.choice("1234567890") for i in range(10)])

        super().__init__(**kw)
    
    def save(self, session: Session):
        session.add(self)
        session.commit()
        session.flush()

def get_users(session: Session, **kwargs) -> List[User]:
    return session.query(User).filter_by(**kwargs).all()

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

def get_user(session: Session, **kwargs):
    return session.query(User).filter_by(**kwargs).first()

def delete_user(session: Session, user: User):
    session.delete(user)
    session.commit()
    session.flush()

def get_random_user(session: Session, current_user: User):
    return random.choice(session.query(User).filter(User.user_id != current_user.user_id).all())