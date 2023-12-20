from pydantic import BaseModel


class UpdateResponse(BaseModel):
    response: str
