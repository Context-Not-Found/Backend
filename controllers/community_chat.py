from sqlalchemy.orm import Session
from models import community_chat as community_chat_model, user as user_model
from utils import get_db_manager
from schemas import community_chat as community_chat_schema


async def get_community_chat_messages(db: Session):
    return await community_chat_model.get_community_chat_messages(db)


async def handle_new_connection(user_id: int):
    with get_db_manager() as db:
        user = await user_model.get_user(db, user_id)
        if user is None:
            raise ConnectionRefusedError("Could not validate credentials")
        return user


async def handle_new_message(message: str, user_id: int):
    with get_db_manager() as db:
        chat_message = await community_chat_model.create_community_chat_message(
            db=db,
            message=community_chat_schema.CommunityChatMessageCreate(
                message_text=message, user_id=user_id
            ),
        )
        return chat_message
