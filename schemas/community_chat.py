from datetime import datetime
from pydantic import BaseModel, Field


class CommunityChatMessageBase(BaseModel):
    message_text: str = Field(title="Message Text", description="Contents of Message")


class CommunityChatMessageCreate(CommunityChatMessageBase):
    user_id: int = Field(title="User ID", description="User ID of the User")


class CommunityChatMessage(CommunityChatMessageBase):
    class UserSchema(BaseModel):
        user_id: int = Field(title="User ID", description="User ID of the User")
        name: str = Field(title="Name", description="Name of the User")

    user: UserSchema
    message_id: int = Field(title="Message ID", description="Generated Message ID")
    created_at: datetime = Field(
        title="Created At", description="Message Creation Time"
    )

    class Config:
        from_attributes = True
