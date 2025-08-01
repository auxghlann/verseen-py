from fastapi import APIRouter
from app.client.verseen_ai import VerseenAI
from starlette import status
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/verseen",
    tags=["Verseen AI"]
)

class ClientRequest(BaseModel):
    artist: Optional[str]
    lyrics: str

class InterpretationResponse(BaseModel):
    interpretation: str

@router.post("/interpret", status_code=status.HTTP_200_OK)
def interpret_lyrics(request: ClientRequest) -> InterpretationResponse:
    response = VerseenAI().interpret_lyrics(request)
    return InterpretationResponse(interpretation=response)