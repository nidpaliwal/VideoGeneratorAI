from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import structlog

from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import ValidationError

logger = structlog.get_logger()

router = APIRouter()


class VoiceoverSegmentRequest(BaseModel):
    text: str
    voiceId: str
    pace: float = Field(default=1.0, ge=0.5, le=2.0)


class VoiceSettings(BaseModel):
    defaultVoiceId: str
    defaultPace: float = Field(default=1.0, ge=0.5, le=2.0)


class GenerateVoiceoverRequest(BaseModel):
    projectId: str
    segments: List[VoiceoverSegmentRequest]
    voiceSettings: VoiceSettings


class GenerateVoiceoverResponse(BaseModel):
    segmentAudioUrls: List[str]
    totalDuration: float
    costEstimate: float


@router.post("/generate", response_model=GenerateVoiceoverResponse)
async def generate_voiceover(
    data: GenerateVoiceoverRequest,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": data.projectId})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    await prisma.project.update(
        where={"id": data.projectId},
        data={"status": "VOICEOVER_READY"},
    )

    return GenerateVoiceoverResponse(
        segmentAudioUrls=[f"https://example.com/audio/seg-{i}.mp3" for i in range(len(data.segments))],
        totalDuration=sum(10.0 for _ in data.segments),
        costEstimate=0.05,
    )


@router.get("/voices")
async def list_voices(current_user: dict = Depends(get_current_user)):
    return {
        "voices": [
            {"id": "eleven_rachel", "name": "Rachel", "gender": "female", "accent": "american", "provider": "elevenlabs"},
            {"id": "eleven_adam", "name": "Adam", "gender": "male", "accent": "american", "provider": "elevenlabs"},
            {"id": "google_en_us_1", "name": "US Female 1", "gender": "female", "accent": "american", "provider": "google"},
            {"id": "google_en_us_2", "name": "US Male 1", "gender": "male", "accent": "american", "provider": "google"},
        ]
    }