from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import sos, user, community_chat
from utils import sio
from schemas import sos as sos_schema, community_chat as community_chat_schema


async def create_sos(request: sos_schema.SOSCreate, db: Session):
    userResp = await user.get_user(db, user_id=request.user_id)
    if userResp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Details not found"
        )

    name = str(userResp.name)
    phone_number = str(userResp.phone_number)
    map_link = (
        f"https://www.google.com/maps/search/?api=1&query={request.lat},{request.long}"
    )

    message = f"""
Urgent! Need Help Now 🆘

Hey everyone,

I'm in a tough spot and need assistance ASAP.

📍 Location: {map_link}

If anyone's nearby, please come to help.

Thanks,
{name}
{phone_number}
"""
    chat_message, _ = await community_chat.create_community_chat_message(
        db,
        message=community_chat_schema.CommunityChatMessageCreate(
            message_text=message, user_id=request.user_id
        ),
    )
    await sio.send(
        data={
            "user": {
                "user_id": str(chat_message.user_id),
                "name": str(userResp.name),
            },
            "message_id": str(chat_message.message_id),
            "message_text": str(chat_message.message_text),
            "created_at": str(chat_message.created_at),
        },
        namespace="/community_chat",
    )

    return sos.create_sos(db, request)


async def close_sos(user_id: int, db: Session):
    db_sos = await sos.get_open_sos_for_user_id(db, user_id)
    if db_sos is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Open SOS found for user",
        )
    return await sos.close_sos(db, db_sos.sos_id)


async def get_sos(db: Session):
    return await sos.get_sos(db)
