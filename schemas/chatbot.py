from pydantic import BaseModel, Field


class ChatbotRequest(BaseModel):
    message: str = Field(
        title="Message", description="Message/Question to be sent to ChatBot"
    )


class ChatbotResponse(BaseModel):
    response: str = Field(title="Response", description="Response from ChatBot")
