from pydantic import BaseModel, Field
from schemas.token import Token


class UserBase(BaseModel):
    email: str = Field(title="Email", description="Email of the User")


class UserCreate(UserBase):
    password: str = Field(title="Password", description="Password of the User")
    name: str = Field(title="Name", description="Name of the User")
    phone_number: str = Field(title="Phone Number", description="Phone Numbe of User")


class UserLogin(UserBase):
    password: str = Field(title="Password", description="Password of the User")


class User(UserBase):
    user_id: int = Field(title="User ID", description="User ID of the User")
    name: str = Field(title="Name", description="Name of the User")
    phone_number: str = Field(title="Phone Number", description="Phone Numbe of User")
    is_teacher: bool = Field(description="User is a teacher or not")

    class Config:
        from_attributes = True


class UserLoginResp(User):
    token: Token = Field(title="Token", description="Access Token Details")
