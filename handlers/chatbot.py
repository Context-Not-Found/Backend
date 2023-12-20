from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from dependencies.auth import get_authorization
from dependencies.openai import get_openai_key
from controllers import chatbot
from schemas import chatbot as chatbot_schema


router = APIRouter(
    prefix="/chatbot",
    tags=["ChatBot"],
)


@router.post("/", response_model=chatbot_schema.ChatbotResponse)
async def chat_with_bot(
    _: Annotated[int, Depends(get_authorization)],
    request: chatbot_schema.ChatbotRequest,
    openai_key: str = Depends(get_openai_key),
):
    bot_response = await chatbot.get_answer_from_chatbot(request.message, openai_key)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"response": bot_response}),
    )
