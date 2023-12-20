from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.auth import get_authorization
from dependencies.db import get_db
import socketio
from utils import decode_token, sio
from controllers import community_chat
from schemas import community_chat as community_chat_schema, token as token_schema


router = APIRouter(
    prefix="/community_chat",
    tags=["Community Chat"],
)


@router.get(
    "/messages/",
    response_model=List[community_chat_schema.CommunityChatMessage],
)
async def get_community_chat_messages(
    _: Annotated[int, Depends(get_authorization)],
    db: Session = Depends(get_db),
):
    return await community_chat.get_community_chat_messages(db)


class CommunityChatNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        print(f"connected to community_chat auth={auth} sid={sid} environ={environ}")
        # Extract Token Payload
        token = auth["token"]
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise ConnectionRefusedError("Could not validate credentials")
        user_id = token_schema.TokenData(user_id=user_id).user_id

        # Check if user exists
        user = await community_chat.handle_new_connection(user_id)

        # Save User Details in socket sesssion
        await sio.save_session(
            sid,
            {"user": {"user_id": user.user_id, "name": user.name}},
            namespace="/community_chat",
        )

    async def on_message(self, sid, data):
        session = await sio.get_session(sid=sid, namespace="/community_chat")
        user = session["user"]
        chat_message = await community_chat.handle_new_message(data, user["user_id"])

        await sio.send(
            {
                "user": {
                    "user_id": str(user["user_id"]),
                    "name": str(user["name"]),
                },
                "message_id": str(chat_message.message_id),
                "message_text": str(chat_message.message_text),
                "created_at": str(chat_message.created_at),
            },
            namespace="/community_chat",
        )

    async def on_disconnect(self, sid):
        print("disconnect ", sid)
