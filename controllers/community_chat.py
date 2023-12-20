from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import community_chat
from utils import get_db_manager
from schemas import community_chat as community_chat_schema


async def get_community_chat_messages(db: Session):
    return community_chat.get_community_chat_messages(db)


async def handle_new_message(message: str, user_id: int):
    with get_db_manager() as db:
        chat_message, user = await community_chat.create_community_chat_message(
            db=db,
            message=community_chat_schema.CommunityChatMessageCreate(
                message_text=message, user_id=user_id
            ),
        )
        return chat_message, user
