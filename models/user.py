from fastapi import HTTPException, status
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    BOOLEAN,
)
from sqlalchemy.orm import relationship
from configuration.database import Base
from sqlalchemy.orm import Session
import bcrypt

from schemas import user as user_schema


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(Text, nullable=False)
    is_teacher = Column(BOOLEAN, default=False, nullable=False)
    phone_number = Column(String, nullable=False)

    community_messages = relationship(
        "CommunityChatMessage",
        back_populates="user",
    )
    tickets = relationship("Ticket", backref="user", foreign_keys="[Ticket.user_id]")

    sos = relationship("SOS", backref="user", foreign_keys="[SOS.user_id]")
    ticket_chat_messages = relationship(
        "TicketChatMessage",
        foreign_keys="[TicketChatMessage.user_id]",
        backref="user",
    )


async def get_user(db: Session, user_id: int):
    try:
        return db.query(User).filter(User.user_id == user_id).first()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def get_user_by_email(db: Session, email: str):
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


async def create_user(db: Session, user: user_schema.UserCreate):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt)
    try:
        db_user = User(
            email=user.email,
            name=user.name,
            hashed_password=hashed_password.decode("utf-8"),
            phone_number=user.phone_number,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
