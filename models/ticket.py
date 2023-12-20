from sqlalchemy import (
    TIMESTAMP,
    Column,
    Float,
    ForeignKey,
    Integer,
    Text,
    func,
    BOOLEAN,
)
from sqlalchemy.orm import relationship
from configuration.database import Base
from fastapi import HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from schemas import ticket as ticket_schema
from models import user


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    is_open = Column(BOOLEAN, default=True, nullable=False)
    is_anonymous = Column(BOOLEAN, default=False, nullable=False)
    ticket_chat_messages = relationship("TicketChatMessage", backref="ticket")

    reports = relationship(
        "TicketReport", backref="ticket", foreign_keys="[TicketReport.ticket_id]"
    )


class TicketReport(Base):
    __tablename__ = "ticket_reports"

    report_id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)
    report_content = Column(Text, nullable=False)
    lat = Column(Float(precision=53), nullable=False)
    long = Column(Float(precision=53), nullable=False)


class TicketChatMessage(Base):
    __tablename__ = "ticket_chat_messages"

    message_id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    message_text = Column(Text, nullable=False)
    created_at = Column("created_at", TIMESTAMP, server_default=func.now())


async def get_user_with_min_open_tickets(db: Session):
    try:
        result = (
            db.query(
                user.User.user_id,
                func.coalesce(func.count(Ticket.ticket_id), 0).label("ticket_count"),
            )
            .outerjoin(
                Ticket,
                and_(
                    user.User.user_id == Ticket.teacher_id,
                    Ticket.is_open == True,
                ),
            )
            .filter(user.User.is_teacher == True)
            .group_by(user.User.user_id)
            .order_by(func.coalesce(func.count(Ticket.ticket_id), 0).asc())
            .first()
        )
        if result:
            return int(result.user_id)
        else:
            return None
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def create_ticket(
    db: Session, ticket: ticket_schema.TicketCreate, user_id: int, teacher_id: int
):
    try:
        ticket_model = Ticket(
            user_id=user_id,
            teacher_id=teacher_id,
            is_anonymous=ticket.is_anonymous,
            is_open=True,
        )
        db.add(ticket_model)
        db.commit()
        db.refresh(ticket_model)

        message = ticket_schema.TicketChatMessageCreate(
            message_text=ticket.report_content,
            user_id=user_id,
            ticket_id=int(str(ticket_model.ticket_id)),
        )

        # Create a message by user with the report
        await create_ticket_message(db, message)

        return ticket_model
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


async def close_ticket(db: Session, ticket_id: int):
    try:
        id = (
            db.query(Ticket)
            .filter(Ticket.ticket_id == ticket_id)
            .update({"is_open": False})
        )
        db.commit()
        return id
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


async def get_ticket(db: Session, ticket_id: int):
    try:
        return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


async def get_open_user_tickets(db: Session, user_id: int):
    try:
        return (
            db.query(Ticket)
            .filter(
                Ticket.is_open == True,
                (Ticket.user_id == user_id) | (Ticket.teacher_id == user_id),
            )
            .all()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


async def get_ticket_messages(db: Session, ticket_id: int):
    try:
        return (
            db.query(TicketChatMessage)
            .filter(TicketChatMessage.ticket_id == ticket_id)
            .all()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


async def create_ticket_message(
    db: Session, message: ticket_schema.TicketChatMessageCreate
):
    try:
        ticket_message = TicketChatMessage(
            ticket_id=message.ticket_id,
            message_text=message.message_text,
            user_id=message.user_id,
        )
        db.add(ticket_message)
        db.commit()
        db.refresh(ticket_message)
        return ticket_message
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
