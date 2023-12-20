from datetime import datetime
from pydantic import BaseModel, Field, validator


class TicketBase(BaseModel):
    is_anonymous: bool = Field(description="If Ticket is anonymous")


class TicketCreate(TicketBase):
    user_id: int = Field(title="User ID", description="User ID of the User")
    report_content: str = Field(title="Ticket Report", description="Report from ticket")
    lat: float = Field(title="Latitude", description="Latitude from the ticket report")
    long: float = Field(
        title="Longitude", description="Longitude from the ticket report"
    )


class Ticket(TicketBase):
    user_id: int | None = Field(
        title="User ID",
        description="User ID of the User. Won't be returned if ticket is marked anonymous",
    )
    ticket_id: int = Field(title="Ticket ID", description="Generated Ticket ID")
    teacher_id: int = Field(
        title="Teacher ID", description="User ID of assigned teacher"
    )
    is_open: bool = Field(description="If Ticket is Open or not")

    @validator("user_id", always=True)
    def validate_user_id(cls, value, values):
        if values["is_anonymous"]:
            return None
        else:
            return value

    class Config:
        from_attributes = True


# TicketChatMessage
class TickerChatMessageBase(BaseModel):
    message_text: str = Field(title="Message Text", description="Contents of Message")
    user_id: int = Field(title="User ID", description="User ID of the User")


class TicketChatMessageCreate(TickerChatMessageBase):
    ticket_id: int = Field(
        title="Ticket ID", description="Ticket ID associated with this message"
    )


class TicketChatMessage(TickerChatMessageBase):
    message_id: int = Field(title="Message ID", description="Generated Message ID")
    created_at: datetime = Field(
        title="Created At", description="Message Creation Time"
    )

    class Config:
        from_attributes = True
