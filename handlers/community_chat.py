from typing import List
from urllib.parse import parse_qs
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.db import get_db
import socketio
from utils import sio
from controllers import community_chat
from schemas import community_chat as community_chat_schema


router = APIRouter(
    prefix="/community_chat",
    tags=["Community Chat"],
)


@router.get(
    "/messages/",
    response_model=List[community_chat_schema.CommunityChatMessage],
)
async def get_community_chat_messages(db: Session = Depends(get_db)):
    return await community_chat.get_community_chat_messages(db)


class CommunityChatNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        # TODO: # ADD Authentication, get user details through it and store them in session.
        query = parse_qs(environ["QUERY_STRING"])
        user_id = (
            int(query.get("user_id", [])[0]) if "user_id" in query else None
        )  # TODO: Remove after implementing auth

        if user_id is None:
            raise ConnectionRefusedError("user_id parameter is required")

        await sio.save_session(sid, {"user_id": user_id}, namespace="/community_chat")

        print(f"connected to community_chat auth={auth} sid={sid} environ={environ}")

    async def on_message(self, sid, data):
        # NOTE: Probably under-performant. See on_connect
        # We can move the crud operation to a callback.
        session = await sio.get_session(sid=sid, namespace="/community_chat")
        chat_message, user = await community_chat.handle_new_message(
            data, session["user_id"]
        )

        await sio.send(
            {
                "user": {
                    "user_id": str(user.user_id),
                    "name": str(user.name),
                },
                "message_id": str(chat_message.message_id),
                "message_text": str(chat_message.message_text),
                "created_at": str(chat_message.created_at),
            },
            namespace="/community_chat",
        )

    async def on_disconnect(self, sid):
        print("disconnect ", sid)
