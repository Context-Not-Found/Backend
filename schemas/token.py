from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(title="Access Token", description="JWT Bearer Token")
    token_type: str = Field(
        title="Token Type", description="Information about token type"
    )


class TokenData(BaseModel):
    user_id: int = Field(title="User ID", description="User ID of the User")
