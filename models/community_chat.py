from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from configuration.database import Base
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import user
from schemas import community_chat as community_chat_schema


class CommunityChatMessage(Base):
    __tablename__ = "community_chat_messages"

    message_id = Column(Integer, primary_key=True)
    message_text = Column(Text, nullable=False)
    created_at = Column("created_at", TIMESTAMP, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    user = relationship("User", back_populates="community_messages")


async def create_community_chat_message(
    db: Session, message: community_chat_schema.CommunityChatMessageCreate
):
    try:
        chat_message = CommunityChatMessage(
            message_text=message.message_text, user_id=message.user_id
        )

        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)

        userResp = (
            db.query(user.User).filter(user.User.user_id == chat_message.user_id).one()
        )

        return chat_message, userResp
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def get_community_chat_messages(db: Session):
    try:
        chats = db.query(CommunityChatMessage).all()
        return chats
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def update_chat_message(db: Session, message_id: int):
    return (
        db.query(CommunityChatMessage)
        .filter(CommunityChatMessage.message_id == message_id)
        .update({"message_text": "RESOLVED"})
    )
