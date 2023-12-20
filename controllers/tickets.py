from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import ticket
from utils import get_db_manager, sio
from schemas import ticket as ticket_schema


async def create_ticket(ticketSchema: ticket_schema.TicketCreate, db: Session):
    teacher_id = await ticket.get_user_with_min_open_tickets(db)
    if teacher_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No teacher found to open ticket with",
        )

    return await ticket.create_ticket(db, ticketSchema, teacher_id)


async def close_ticket(ticket_id: int, db: Session):
    db_ticket = await ticket.get_ticket(db, ticket_id)
    if db_ticket is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket not found",
        )

    # Destroy room
    await sio.close_room(f"ticket-{ticket_id}", namespace="/tickets")
    # Close Ticket
    return await ticket.close_ticket(db, ticket_id)


async def get_ticket_messages(ticket_id: int, db: Session):
    db_ticket = await ticket.get_ticket(db, ticket_id)
    if db_ticket is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket not found",
        )

    return await ticket.get_ticket_messages(db, ticket_id)


async def read_open_user_tickets(user_id: int, db: Session):
    return await ticket.get_open_user_tickets(db, user_id)


async def handle_new_connection(user_id: int, ticket_id: int):
    with get_db_manager() as db:
        db_ticket = await ticket.get_ticket(db, ticket_id)

        # If ticket is closed or not available
        if db_ticket is None or bool(db_ticket.is_open) == False:
            raise ConnectionRefusedError("ticket not found or closed ticket")

        # If some user aside from the users in ticket tries to join the room then do nothing
        # Ugly type casting, is there really no better way to do this?
        if (
            int(str(db_ticket.user_id)) != user_id
            and int(str(db_ticket.teacher_id)) != user_id
        ):
            raise ConnectionRefusedError("user not allowed in this ticket room")


async def handle_new_message(message: str, user_id: int, ticket_id: int):
    with get_db_manager() as db:
        ticket_message, user = await ticket.create_ticket_message(
            db=db,
            message=ticket_schema.TicketChatMessageCreate(
                ticket_id=ticket_id,
                message_text=message,
                user_id=user_id,
            ),
        )
        return ticket_message, user
