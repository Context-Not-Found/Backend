from fastapi import HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
import bcrypt

import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt)
    try:
        db_user = models.User(
            email=user.email,
            name=user.name,
            hashed_password=hashed_password,
            phone_number=user.phone_number,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as exc:
        # Handle any other unexpected errors
        db.rollback()
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


def create_community_chat_message(
    db: Session, message: schemas.CommunityChatMessageCreate
):
    try:
        chat_message = models.CommunityChatMessage(
            message_text=message.message_text, user_id=message.user_id
        )
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        return chat_message
    except Exception as exc:
        # Handle any other unexpected errors
        db.rollback()
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


def get_community_chat_messages(db: Session):
    return db.query(models.CommunityChatMessage).all()


def get_user_with_min_open_tickets(db: Session):
    result = (
        db.query(
            models.User.user_id,
            func.coalesce(func.count(models.Ticket.ticket_id), 0).label("ticket_count"),
        )
        .outerjoin(
            models.Ticket,
            and_(
                models.User.user_id == models.Ticket.teacher_id,
                models.Ticket.is_open == True,
            ),
        )
        .filter(models.User.is_teacher == True)
        .group_by(models.User.user_id)
        .order_by(func.coalesce(func.count(models.Ticket.ticket_id), 0).asc())
        .first()
    )
    if result:
        return int(result.user_id)
    else:
        return None


def create_ticket(db: Session, user_id: int, teacher_id: int):
    try:
        ticket = models.Ticket(
            user_id=user_id,
            teacher_id=teacher_id,
            is_open=True,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    except Exception as exc:
        # Handle any other unexpected errors
        db.rollback()
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


def close_ticket(db: Session, ticket_id: int):
    try:
        id = (
            db.query(models.Ticket)
            .filter(models.Ticket.ticket_id == ticket_id)
            .update({"is_open": False})
        )
        db.commit()
        return id
    except Exception as exc:
        # Handle any other unexpected errors
        db.rollback()
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()


def get_open_tickets(db: Session):
    return db.query(models.Ticket).filter(models.Ticket.is_open == True).all()


def get_ticket_messages(db: Session, ticket_id: int):
    return (
        db.query(models.TicketChatMessage)
        .filter(models.TicketChatMessage.ticket_id == ticket_id)
        .all()
    )


def create_ticket_message(db: Session, message: schemas.TicketChatMessageCreate):
    try:
        ticket_message = models.TicketChatMessage(
            ticket_id=message.ticket_id,
            message_text=message.message_text,
            user_id=message.user_id,
        )
        db.add(ticket_message)
        db.commit()
        db.refresh(ticket_message)
        return ticket_message
    except Exception as exc:
        # Handle any other unexpected errors
        db.rollback()
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )