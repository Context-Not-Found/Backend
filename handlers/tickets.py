from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dependencies.auth import get_authorization
from dependencies.db import get_db
import socketio
from urllib.parse import parse_qs
from socketio.exceptions import ConnectionRefusedError
from dependencies.db import get_db
from utils import decode_token, sio
from controllers import tickets
from schemas import ticket as ticket_schema, token as token_schema, UpdateResponse

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


# Create Ticket
@router.post("/create/", response_model=ticket_schema.Ticket)
async def create_ticket(
    ticket: ticket_schema.TicketCreate,
    user_id: Annotated[int, Depends(get_authorization)],
    db: Session = Depends(get_db),
):
    return await tickets.create_ticket(ticket, user_id, db)


# Close Ticket
@router.patch("/close/", response_model=UpdateResponse)
async def close_ticket(
    ticket_id: Annotated[int, Query(title="Ticket ID", description="ID of the ticket")],
    _: Annotated[int, Depends(get_authorization)],
    db: Session = Depends(get_db),
):
    id = await tickets.close_ticket(ticket_id, db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"respone": f"success, updated id ${id}"}),
    )


# Get Ticket Messages
@router.get("/messages/", response_model=List[ticket_schema.TicketChatMessage])
async def get_ticket_messages(
    ticket_id: Annotated[int, Query(title="Ticket ID", description="ID of the ticket")],
    _: Annotated[int, Depends(get_authorization)],
    db: Session = Depends(get_db),
):
    return await tickets.get_ticket_messages(ticket_id, db)


# Get Open Tickets for user_id
@router.get("/", response_model=List[ticket_schema.Ticket])
async def read_open_user_tickets(
    user_id: Annotated[int, Depends(get_authorization)],
    db: Session = Depends(get_db),
):
    return await tickets.read_open_user_tickets(user_id, db)


class TicketChatNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        # Extract Token Payload
        token = auth["token"]
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise ConnectionRefusedError("Could not validate credentials")
        user_id = token_schema.TokenData(user_id=user_id).user_id

        # Extract ticket ID from query string
        query = parse_qs(environ["QUERY_STRING"])
        ticket_id = int(query.get("ticket_id", [])[0]) if "ticket_id" in query else None
        if ticket_id is None or user_id is None:
            raise ConnectionRefusedError("ticket_id and user_id parameter is required")

        # Check if ticket exists, and user that is trying to join
        user, ticket = await tickets.handle_new_connection(user_id, ticket_id)

        await sio.enter_room(sid, f"ticket-{ticket_id}", namespace="/tickets")
        # Save User Details and Ticket ID in socket sesssion
        await sio.save_session(
            sid,
            {
                "user": {"user_id": user.user_id, "name": user.name},
                "ticket_id": ticket.ticket_id,
            },
            namespace="/tickets",
        )

        print(f"connected to ticket chat. auth={auth} sid={sid} environ={environ}")

    async def on_message(self, sid, data):
        session = await sio.get_session(sid=sid, namespace="/tickets")
        user = session["user"]
        ticket_message = await tickets.handle_new_message(
            data, user["user_id"], session["ticket_id"]
        )

        await sio.emit(
            {
                "user": {
                    "user_id": str(user["user_id"]),
                    "name": str(user["name"]),
                },
                "message_id": str(ticket_message.message_id),
                "message_text": str(ticket_message.message_text),
                "created_at": str(ticket_message.created_at),
            },
            room=f"ticket-{session['ticket_id']}",
            namespace="/tickets",
        )

    async def on_disconnect(self, sid):
        print("disconnect ", sid)
