from fastapi import APIRouter
from app.client.verseen_ai import VerseenAI
from starlette import status
from pydantic import BaseModel

router = APIRouter()

class LyricsRequest(BaseModel):
    lyrics: str

class InterpretationResponse(BaseModel):
    interpretation: str

@router.post("/interpret", status_code=status.HTTP_200_OK)
def interpret_lyrics(lyrics: LyricsRequest) -> InterpretationResponse:
    response = VerseenAI().interpret_lyrics(lyrics)
    return InterpretationResponse(interpretation=response)