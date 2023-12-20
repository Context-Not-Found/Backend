from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dependencies.db import get_db
import socketio
from urllib.parse import parse_qs
from socketio.exceptions import ConnectionRefusedError
from dependencies.db import get_db
from utils import sio
from controllers import tickets
from schemas import ticket as ticket_schema, UpdateResponse

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


# Create Ticket
@router.post("/create/", response_model=ticket_schema.Ticket)
async def create_ticket(
    ticket: ticket_schema.TicketCreate, db: Session = Depends(get_db)
):
    return await tickets.create_ticket(ticket, db)


# Close Ticket
@router.patch("/close/", response_model=UpdateResponse)
async def close_ticket(
    ticket_id: Annotated[int, Query(title="Ticket ID", description="ID of the ticket")],
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
    db: Session = Depends(get_db),
):
    return await tickets.get_ticket_messages(ticket_id, db)


# Get Open Tickets for user_id
@router.get("/", response_model=List[ticket_schema.Ticket])
async def read_open_user_tickets(
    user_id: Annotated[
        int,
        Query(title="User ID", description="ID of the User"),
    ],
    db: Session = Depends(get_db),
):
    return await tickets.read_open_user_tickets(user_id, db)


class TicketChatNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        query = parse_qs(environ["QUERY_STRING"])
        ticket_id = int(query.get("ticket_id", [])[0]) if "ticket_id" in query else None
        user_id = (
            int(query.get("user_id", [])[0]) if "user_id" in query else None
        )  # TODO: Remove after implementing auth

        if ticket_id is None or user_id is None:
            raise ConnectionRefusedError("ticket_id and user_id parameter is required")

        # Check if ticket exists, and user that is trying to join
        await tickets.handle_new_connection(user_id, ticket_id)

        await sio.enter_room(sid, f"ticket-{ticket_id}", namespace="/tickets")
        await sio.save_session(
            sid, {"user_id": user_id, "ticket_id": ticket_id}, namespace="/tickets"
        )

        print(f"connected to ticket chat. auth={auth} sid={sid} environ={environ}")

    async def on_message(self, sid, data):
        session = await sio.get_session(sid=sid, namespace="/tickets")
        ticket_message, user = await tickets.handle_new_message(
            data, session["user_id"], session["ticket_id"]
        )

        await sio.emit(
            {
                "user": {
                    "user_id": str(ticket_message.user_id),
                    "name": str(user.name),
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
